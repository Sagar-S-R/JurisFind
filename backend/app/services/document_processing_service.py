"""
Document processing service for JurisFind.

Full async pipeline:
  1. Download PDF bytes from BlobStorageService
  2. Extract text + page numbers with PyMuPDF
  3. Chunk with RecursiveCharacterTextSplitter (1000/200)
  4. Generate 768-dim embeddings with all-mpnet-base-v2
  5. Persist chunks to PostgreSQL + embeddings to FAISS
  6. Generate legal summary via Groq LLM
  7. Update DocumentSession status (pending → processing → completed/failed)

Processing occurs exactly once per session (idempotency guard).
"""

import asyncio
import io
import logging
import uuid
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from app.db.models import DocumentChunk
from app.db.session import DatabaseSession
from app.services.blob_storage_service import blob_storage_service
from app.services.vector_store_service import vector_store_service
from app.services.session_service import session_service

logger = logging.getLogger(__name__)

# ── Embedding model (loaded once at module level) ─────────────────────────────
_EMBEDDING_MODEL: Optional[SentenceTransformer] = None


def _get_embedding_model() -> SentenceTransformer:
    """Lazy-load the sentence-transformers model (768-dim)."""
    global _EMBEDDING_MODEL
    if _EMBEDDING_MODEL is None:
        logger.info("Loading sentence-transformers/all-mpnet-base-v2 ...")
        _EMBEDDING_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        logger.info("Embedding model loaded.")
    return _EMBEDDING_MODEL


# ── Splitter config ───────────────────────────────────────────────────────────
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
    Stateless service that implements the full document processing pipeline.

    All methods are sync; the public `process_document_async()` wraps the
    heavy pipeline in asyncio.to_thread() so it doesn't block the event loop.
    """

    # ── Step 1: Text extraction ───────────────────────────────────────────────

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> List[Tuple[str, int]]:
        """
        Extract (text, page_number) pairs from PDF bytes using PyMuPDF.

        Args:
            pdf_bytes: Raw PDF file content

        Returns:
            List of (page_text, 1-indexed page_number) tuples

        Raises:
            DocumentProcessingError: If PDF cannot be parsed
        """
        try:
            idx = pdf_bytes.find(b"%PDF-")
            if idx > 0:
                pdf_bytes = pdf_bytes[idx:]
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            raise DocumentProcessingError(f"Failed to open PDF: {exc}") from exc

        pages: List[Tuple[str, int]] = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                pages.append((text, page_num + 1))  # 1-indexed

        doc.close()

        if not pages:
            raise DocumentProcessingError("PDF contains no extractable text.")

        return pages

    # ── Step 2: Chunking ──────────────────────────────────────────────────────

    @staticmethod
    def chunk_text(pages: List[Tuple[str, int]]) -> List[Tuple[str, int]]:
        """
        Chunk page text using RecursiveCharacterTextSplitter (1000/200).

        Preserves the page_number of the page each chunk came from.

        Args:
            pages: List of (page_text, page_number) tuples

        Returns:
            List of (chunk_text, page_number) tuples
        """
        chunks: List[Tuple[str, int]] = []
        for page_text, page_num in pages:
            page_chunks = _SPLITTER.split_text(page_text)
            for chunk in page_chunks:
                if chunk.strip():
                    chunks.append((chunk.strip(), page_num))
        return chunks

    # ── Step 3: Embedding generation ─────────────────────────────────────────

    @staticmethod
    def generate_embeddings(chunk_texts: List[str]) -> np.ndarray:
        """
        Generate 768-dimensional embeddings for a list of text chunks.

        Args:
            chunk_texts: List of text strings to embed

        Returns:
            np.ndarray: Shape (N, 768), dtype float32
        """
        model = _get_embedding_model()
        embeddings = model.encode(
            chunk_texts,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=False,  # VectorStoreService normalizes internally
        )
        return embeddings.astype(np.float32)

    # ── Step 4: Persist chunks ────────────────────────────────────────────────

    @staticmethod
    def store_chunks(
        session_id: str,
        chunks: List[Tuple[str, int]],
        embeddings: np.ndarray,
        db,
    ) -> List[str]:
        """
        Save chunks to PostgreSQL and embeddings to FAISS.

        Args:
            session_id: UUID string of the document session
            chunks: List of (chunk_text, page_number) tuples
            embeddings: Shape (N, 768) float32 numpy array
            db: SQLAlchemy session

        Returns:
            List[str]: List of embedding_reference strings (UUID v4)
        """
        embedding_refs: List[str] = [str(uuid.uuid4()) for _ in chunks]

        # Persist to PostgreSQL
        db_chunks = [
            DocumentChunk(
                chunk_id=uuid.uuid4(),
                session_id=session_id,
                page_number=page_num,
                chunk_text=chunk_text,
                chunk_metadata={"char_count": len(chunk_text)},
                embedding_reference=ref,
            )
            for (chunk_text, page_num), ref in zip(chunks, embedding_refs)
        ]
        db.add_all(db_chunks)
        db.commit()

        # Persist to FAISS
        vector_store_service.add_embeddings(embedding_refs, embeddings)

        return embedding_refs

    # ── Step 5: Summarization ─────────────────────────────────────────────────

    @staticmethod
    def generate_summary(full_text: str) -> str:
        """
        Generate a structured legal document summary via the Legal Agent.

        Args:
            full_text: Combined text from all pages (truncated to ~8000 chars)

        Returns:
            str: AI-generated summary
        """
        from app.ai.legal_agent import get_agent
        agent = get_agent()

        # Truncate to avoid token limits (~8000 chars approx ~2000 tokens)
        truncated = full_text[:8000] if len(full_text) > 8000 else full_text

        return agent.generate_summary(truncated)

    # ── Orchestrator ──────────────────────────────────────────────────────────

    def process_document(self, session_id: str, blob_path: str) -> None:
        """
        Execute the full synchronous processing pipeline for a document session.

        Updates processing_status:
          pending → processing → completed | failed

        This method is intentionally synchronous and should be called via
        asyncio.to_thread() from the async worker.

        Args:
            session_id: UUID string of the document session
            blob_path: Blob Storage path to the PDF
        """
        with DatabaseSession() as db:
            # Idempotency guard: only process if still pending
            from app.db.models import DocumentSession
            current = (
                db.query(DocumentSession)
                .filter(DocumentSession.session_id == session_id)
                .first()
            )
            if current is None:
                logger.warning("Session %s not found — skipping processing.", session_id)
                return
            if current.processing_status != "pending":
                logger.info(
                    "Session %s already in status '%s' — skipping.",
                    session_id,
                    current.processing_status,
                )
                return

        try:
            # ── Mark as processing ────────────────────────────────────────────
            with DatabaseSession() as db:
                session_service.update_processing_status(db, session_id, "processing")

            # ── Download PDF ──────────────────────────────────────────────────
            pdf_bytes = blob_storage_service.download_pdf(blob_path)

            # ── Extract text ──────────────────────────────────────────────────
            pages = self.extract_text(pdf_bytes)
            full_text = "\n\n".join(text for text, _ in pages)

            # ── Chunk text ────────────────────────────────────────────────────
            chunks = self.chunk_text(pages)
            if not chunks:
                raise DocumentProcessingError("No text chunks produced from document.")

            chunk_texts = [text for text, _ in chunks]

            # ── Generate embeddings ───────────────────────────────────────────
            embeddings = self.generate_embeddings(chunk_texts)

            # ── Store chunks + embeddings ─────────────────────────────────────
            with DatabaseSession() as db:
                self.store_chunks(session_id, chunks, embeddings, db)

            # ── Generate summary ──────────────────────────────────────────────
            summary = self.generate_summary(full_text)

            # ── Mark as completed ─────────────────────────────────────────────
            with DatabaseSession() as db:
                session_service.update_processing_status(
                    db, session_id, "completed", summary=summary
                )

            logger.info(
                "Session %s processed successfully (%d chunks).",
                session_id,
                len(chunks),
            )

        except Exception as exc:
            logger.exception("Processing failed for session %s: %s", session_id, exc)
            try:
                with DatabaseSession() as db:
                    session_service.update_processing_status(
                        db, session_id, "failed", error_message=str(exc)
                    )
            except Exception as inner:
                logger.error("Failed to update status to 'failed': %s", inner)

    async def process_document_async(self, session_id: str, blob_path: str) -> None:
        """
        Async wrapper around process_document() using asyncio.to_thread().

        Runs the CPU/IO-heavy pipeline in a thread pool without blocking
        the FastAPI event loop.

        Args:
            session_id: UUID string of the document session
            blob_path: Blob Storage path to the PDF
        """
        await asyncio.to_thread(self.process_document, session_id, blob_path)


# Module-level singleton
document_processing_service = DocumentProcessingService()
