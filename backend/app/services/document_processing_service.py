"""
Document Processing Service for JurisFind V2.

Full synchronous pipeline (runs in Celery worker process):
  1. Download PDF bytes from BlobStorageService
  2. Extract text + page numbers with PyMuPDF (with %PDF- self-healing)
  3. Chunk with RecursiveCharacterTextSplitter (1000/200)
  4. Generate 768-dim embeddings via EmbeddingService
  5. Persist chunks to document_chunks table
  6. Persist embeddings to document_embeddings table (pgvector)
  7. Generate legal summary via Groq LLM
  8. Update Document.status (uploaded → processing → ready | failed)

Key V2 change: Processing is scoped to a Document (not a DocumentSession).
Embeddings are persisted in PostgreSQL via pgvector (not ephemeral FAISS).
"""

import logging
import uuid
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.db.models import Document, DocumentChunk, DocumentEmbedding
from app.db.session import DatabaseSession
from app.services.blob_storage_service import blob_storage_service
from app.services.embedding_service import embed_texts

logger = logging.getLogger(__name__)

# ── Text splitter (shared instance) ──────────────────────────────────────────
_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
    separators=["\n\n", "\n", " ", ""],
)


class DocumentProcessingError(Exception):
    """Raised when document processing fails unrecoverably."""
    pass


class DocumentProcessingService:
    """
    Stateless service for the V2 document processing pipeline.

    All methods are synchronous. Called from the Celery worker (no event loop).
    """

    # ── Step 1: Text extraction ───────────────────────────────────────────────

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> List[Tuple[str, int]]:
        """
        Extract (text, page_number) tuples from PDF bytes using PyMuPDF.

        Applies self-healing: if the bytes have garbage before %PDF-, we slice
        from the %PDF- marker to avoid the 'format error: cannot recognize
        version marker' MuPDF error.

        Returns:
            List of (page_text, 1-indexed page_number) tuples.
        """
        idx = pdf_bytes.find(b"%PDF-")
        if idx > 0:
            logger.debug("PDF self-heal: slicing %d leading bytes.", idx)
            pdf_bytes = pdf_bytes[idx:]

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            raise DocumentProcessingError(f"Failed to open PDF: {exc}") from exc

        pages: List[Tuple[str, int]] = []
        for i in range(len(doc)):
            text = doc[i].get_text("text")
            if text.strip():
                pages.append((text, i + 1))  # 1-indexed
        doc.close()

        if not pages:
            raise DocumentProcessingError("PDF contains no extractable text.")

        return pages

    # ── Step 2: Chunking ──────────────────────────────────────────────────────

    @staticmethod
    def chunk_text(pages: List[Tuple[str, int]]) -> List[Tuple[str, int, int]]:
        """
        Split page text into overlapping chunks.

        Returns:
            List of (chunk_text, page_number, chunk_index) tuples.
        """
        chunks: List[Tuple[str, int, int]] = []
        chunk_index = 0
        for page_text, page_num in pages:
            for chunk in _SPLITTER.split_text(page_text):
                if chunk.strip():
                    chunks.append((chunk.strip(), page_num, chunk_index))
                    chunk_index += 1
        return chunks

    # ── Step 3+4: Store chunks + embeddings ───────────────────────────────────

    @staticmethod
    def store_chunks_and_embeddings(
        document_id: uuid.UUID,
        chunks: List[Tuple[str, int, int]],
        db,
    ) -> int:
        """
        Persist chunks to document_chunks and embeddings to document_embeddings.

        Embeddings are written as pgvector native vectors.

        Returns:
            Number of chunks stored.
        """
        if not chunks:
            return 0

        chunk_texts = [c[0] for c in chunks]
        logger.info("Generating embeddings for %d chunks...", len(chunk_texts))
        embeddings = embed_texts(chunk_texts)  # shape (N, 768)

        # Build and flush DocumentChunk records first to get their IDs
        chunk_records = []
        for (chunk_text, page_num, chunk_idx) in chunks:
            chunk_record = DocumentChunk(
                id=uuid.uuid4(),
                document_id=document_id,
                page_number=page_num,
                chunk_index=chunk_idx,
                chunk_text=chunk_text,
                chunk_metadata={"char_count": len(chunk_text)},
            )
            chunk_records.append(chunk_record)

        db.add_all(chunk_records)
        db.flush()  # assign IDs without committing

        # Build DocumentEmbedding records
        embedding_records = []
        for chunk_record, vector in zip(chunk_records, embeddings):
            emb_record = DocumentEmbedding(
                id=uuid.uuid4(),
                chunk_id=chunk_record.id,
                document_id=document_id,
                embedding=vector.tolist(),  # pgvector accepts list[float]
            )
            embedding_records.append(emb_record)

        db.add_all(embedding_records)
        db.commit()

        logger.info("Stored %d chunks + embeddings for document %s.", len(chunk_records), document_id)
        return len(chunk_records)

    # ── Step 5: Summarization ─────────────────────────────────────────────────

    @staticmethod
    def generate_summary(full_text: str) -> str:
        """Generate a structured legal summary via the Legal Agent (Groq)."""
        from app.ai.legal_agent import get_agent
        agent = get_agent()
        truncated = full_text[:8000] if len(full_text) > 8000 else full_text
        return agent.generate_summary(truncated)

    # ── Orchestrator ──────────────────────────────────────────────────────────

    def process_document(self, document_id: str, blob_path: str) -> None:
        """
        Execute the full synchronous processing pipeline for a Document.

        Status transitions: uploaded → processing → ready | failed

        Args:
            document_id: UUID string of the Document record.
            blob_path:   Blob Storage path (or local path) to the PDF.
        """
        doc_uuid = uuid.UUID(document_id)

        with DatabaseSession() as db:
            from app.db.crud.document_repository import get_document, update_status
            doc = get_document(db, doc_uuid)
            if doc is None:
                logger.warning("Document %s not found — skipping.", document_id)
                return
            if doc.status not in ("uploaded", "processing", "failed"):
                logger.info(
                    "Document %s already in status '%s' — skipping.", document_id, doc.status
                )
                return
            # Mark as processing
            update_status(db, doc, "processing")

        try:
            # Download PDF
            pdf_bytes = blob_storage_service.download_pdf(blob_path)

            # Extract text
            pages = self.extract_text(pdf_bytes)
            full_text = "\n\n".join(text for text, _ in pages)

            # Chunk
            chunks = self.chunk_text(pages)
            if not chunks:
                raise DocumentProcessingError("No text chunks produced.")

            # Store chunks + embeddings
            with DatabaseSession() as db:
                self.store_chunks_and_embeddings(doc_uuid, chunks, db)

            # Summarize
            summary = self.generate_summary(full_text)

            # Mark ready
            with DatabaseSession() as db:
                from app.db.crud.document_repository import get_document, update_status
                doc = get_document(db, doc_uuid)
                update_status(db, doc, "ready", summary=summary)

            logger.info(
                "Document %s processed successfully (%d chunks).",
                document_id,
                len(chunks),
            )

        except Exception as exc:
            logger.exception("Processing failed for document %s: %s", document_id, exc)
            try:
                with DatabaseSession() as db:
                    from app.db.crud.document_repository import get_document, update_status
                    doc = get_document(db, doc_uuid)
                    if doc:
                        update_status(db, doc, "failed", error_message=str(exc))
            except Exception as inner:
                logger.error("Failed to update status to 'failed': %s", inner)
            raise exc


# Module-level singleton
document_processing_service = DocumentProcessingService()
