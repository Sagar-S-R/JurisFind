"""
Retrieval Service — pgvector-based RAG retrieval scoped to session documents.

Given a session and a user query, retrieves the most relevant DocumentChunk
records from the documents attached to that session.

Flow:
  1. Get attached document IDs for the session
  2. Encode the user query → 768-dim vector
  3. Execute pgvector cosine similarity search filtered by document_id
  4. Load matching chunk texts + metadata
  5. Return formatted context blocks with source attribution

This service is used synchronously inside the chat request handler.
"""
import logging
import uuid
from typing import List, Optional, Tuple

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.embedding_service import embed_query
from app.db.crud.session_document_repository import get_attached_document_ids

logger = logging.getLogger(__name__)

# Maximum chunks to retrieve per query
DEFAULT_TOP_K = 8
# Minimum cosine similarity score (0.0 = anything, 1.0 = exact match)
MIN_SIMILARITY = 0.20


class RetrievedChunk:
    """A chunk retrieved from pgvector search with its source metadata."""

    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_title: str,
        page_number: int,
        chunk_text: str,
        similarity: float,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.page_number = page_number
        self.chunk_text = chunk_text
        self.similarity = similarity

    def as_context_block(self) -> str:
        """Format this chunk as a labelled context block for the LLM prompt."""
        return (
            f"--- SOURCE: {self.document_title}, Page {self.page_number} ---\n"
            f"{self.chunk_text}\n"
            f"--- END SOURCE ---"
        )

    def as_citation(self) -> dict:
        """Return citation metadata for the API response."""
        return {
            "document_title": self.document_title,
            "page_number": self.page_number,
            "excerpt": self.chunk_text[:200],
        }


def retrieve_for_session(
    db: Session,
    session_id: uuid.UUID,
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> List[RetrievedChunk]:
    """
    Retrieve the most relevant document chunks for a query within a session.

    Returns an empty list if no documents are attached to the session.
    """
    # Get document IDs attached to this session
    document_ids = get_attached_document_ids(db, session_id)
    if not document_ids:
        logger.debug("Session %s has no attached documents — skipping retrieval.", session_id)
        return []

    # Encode query
    query_vector = embed_query(query)

    # Convert to pgvector-compatible string format: '[0.1, 0.2, ...]'
    vector_str = "[" + ",".join(f"{v:.6f}" for v in query_vector.tolist()) + "]"

    # Convert UUIDs to strings for the SQL array
    doc_id_strings = [str(d) for d in document_ids]

    # pgvector cosine distance search with document filter
    # We remove the strict 'min_sim' check from the WHERE clause to ensure we always 
    # give the LLM some context if documents are attached.
    sql = text(
        """
        SELECT
            dc.id            AS chunk_id,
            dc.document_id,
            d.title          AS document_title,
            dc.page_number,
            dc.chunk_text,
            1 - (de.embedding <=> CAST(:query_vec AS vector)) AS similarity
        FROM document_embeddings de
        JOIN document_chunks dc ON dc.id = de.chunk_id
        JOIN documents d ON d.id = de.document_id
        WHERE de.document_id = ANY(CAST(:doc_ids AS uuid[]))
        ORDER BY de.embedding <=> CAST(:query_vec AS vector) ASC
        LIMIT :top_k
        """
    )

    rows = db.execute(
        sql,
        {
            "query_vec": vector_str,
            "doc_ids": "{" + ",".join(doc_id_strings) + "}",
            "top_k": top_k,
        },
    ).fetchall()

    results = [
        RetrievedChunk(
            chunk_id=str(row.chunk_id),
            document_id=str(row.document_id),
            document_title=row.document_title,
            page_number=row.page_number,
            chunk_text=row.chunk_text,
            similarity=float(row.similarity),
        )
        for row in rows
    ]

    logger.debug(
        "Retrieved %d chunks for session %s (query: %r)",
        len(results),
        session_id,
        query[:60],
    )
    return results


def build_context_prompt(chunks: List[RetrievedChunk]) -> str:
    """Combine retrieved chunks into a single formatted context string for the LLM."""
    if not chunks:
        return ""
    return "\n\n".join(chunk.as_context_block() for chunk in chunks)
