"""
Node 2B — DocumentChat

Answers questions about documents attached to the session.
Routes retrieval based on document source type:
  - source_type = "legal_case"  → Qdrant (filtered by document_id)
  - source_type = "uploaded"    → pgvector via raw SQL

Citations are built directly from Qdrant payload / pgvector row data.
"""
import logging
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from qdrant_client.http.models import FieldCondition, Filter, MatchValue
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.agents.nodes._embedder import embed
from app.agents.nodes._qdrant import COLLECTION_NAME, get_qdrant
from app.agents.state import JurisFindState
from app.db.models import Document
from app.db.session import DatabaseSession

_dotenv_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=False)

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a senior legal assistant. Answer the user's question using "
    "ONLY the source blocks provided below. Each source block contains "
    "text from a specific legal case. Cite inline as [Case Name, Year]. "
    "If the answer cannot be found in the sources, say: "
    "'I cannot find this information in the attached documents.'"
)

TOP_K_QDRANT  = 8
TOP_K_PGVECTOR = 8


def _clean(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^(System:|Assistant:|AI:|Response:)\s*", "", text,
                  flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── Retrieval helpers ─────────────────────────────────────────────────────────

def _search_qdrant_by_doc(db: Session, doc_id: str, query_vector: list[float]) -> list[dict]:
    """Search Qdrant filtered to a single document_id. Returns raw dicts."""
    client = get_qdrant()
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=doc_id))]
        ),
        limit=TOP_K_QDRANT,
        with_payload=True,
    )
    
    # Fetch chunk texts from PostgreSQL
    chunk_ids = [r.payload.get("chunk_id") for r in result.points if r.payload.get("chunk_id")]
    chunk_texts = {}
    if chunk_ids:
        rows = db.execute(
            text("SELECT id::text, chunk_text FROM legal_chunks WHERE id = ANY(CAST(:ids AS uuid[]))"),
            {"ids": chunk_ids}
        ).fetchall()
        chunk_texts = {r[0]: r[1] for r in rows}

    return [
        {
            "chunk_text":  chunk_texts.get(r.payload.get("chunk_id", ""), ""),
            "document_id": r.payload.get("document_id", doc_id),
            "chunk_id":    r.payload.get("chunk_id", ""),
            "title":       r.payload.get("title", "Unknown"),
            "court":       r.payload.get("court", ""),
            "year":        r.payload.get("year", ""),
            "citation":    r.payload.get("citation", ""),
            "score":       r.score,
            "source":      "qdrant",
        }
        for r in result.points
    ]


def _search_pgvector_by_doc(db: Session, doc_id: str,
                             query_vector: list[float]) -> list[dict]:
    """Search pgvector for a single uploaded document. Returns raw dicts."""
    vector_str = "[" + ",".join(f"{v:.6f}" for v in query_vector) + "]"
    sql = text("""
        SELECT
            dc.id          AS chunk_id,
            dc.document_id,
            d.title        AS title,
            d.blob_path    AS blob_path,
            dc.page_number,
            dc.chunk_text,
            1 - (de.embedding <=> CAST(:query_vec AS vector)) AS score
        FROM document_embeddings de
        JOIN document_chunks dc ON dc.id = de.chunk_id
        JOIN documents d        ON d.id  = de.document_id
        WHERE de.document_id = CAST(:doc_id AS uuid)
        ORDER BY de.embedding <=> CAST(:query_vec AS vector) ASC
        LIMIT :top_k
    """)
    rows = db.execute(sql, {
        "query_vec": vector_str,
        "doc_id":    doc_id,
        "top_k":     TOP_K_PGVECTOR,
    }).fetchall()

    import os as _os
    return [
        {
            "chunk_text":  row.chunk_text,
            "document_id": str(row.document_id),
            "chunk_id":    str(row.chunk_id),
            "title":       row.title,
            "page_number": row.page_number,
            "blob_path":   _os.path.basename(row.blob_path),
            "score":       float(row.score),
            "source":      "pgvector",
        }
        for row in rows
    ]


def _build_citations(chunks: list[dict]) -> list[dict]:
    """Build citation objects directly from chunk dicts — no LLM involved."""
    citations = []
    for c in chunks:
        # truncate chunk_text for the excerpt
        text = c.get("chunk_text", "")
        excerpt = text[:200] + "..." if len(text) > 200 else text
        
        if c.get("source") == "qdrant":
            citations.append({
                "document_id": c.get("document_id"),
                "chunk_id":    c.get("chunk_id"),
                "document_title": c.get("title"),
                "court":       c.get("court"),
                "year":        c.get("year"),
                "citation":    c.get("citation"),
                "score":       c.get("score"),
                "excerpt":     excerpt,
            })
        else:  # pgvector / uploaded
            citations.append({
                "document_id":    c.get("document_id"),
                "chunk_id":       str(c.get("chunk_id")),
                "document_title": c.get("title"),
                "page_number":    c.get("page_number"),
                "filename":       c.get("blob_path"),
                "score":          c.get("score"),
                "excerpt":     excerpt,
            })
    return citations


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a labelled context block for the LLM."""
    parts = []
    for c in chunks:
        label = f"{c.get('title', 'Unknown')} ({c.get('year', c.get('page_number', ''))})"
        parts.append(f"Source: {label}\n{c.get('chunk_text', '')}")
    return "\n\n---\n\n".join(parts)


# ── Node ──────────────────────────────────────────────────────────────────────

def document_chat_node(state: JurisFindState) -> JurisFindState:
    """
    Retrieve chunks from all attached documents and generate a RAG answer.

    Corpus cases    → Qdrant (filtered by document_id)
    Uploaded PDFs   → pgvector (filtered by document_id)
    """
    question    = state["question"]
    history     = state.get("history", [])
    doc_ids     = state.get("document_ids", [])

    if not doc_ids:
        return {
            **state,
            "answer": "No documents are attached to this session.",
            "citations": [],
            "retrieved_chunks": [],
        }

    query_vector = embed(question)
    all_chunks: list[dict] = []

    try:
        with DatabaseSession() as db:
            for doc_id in doc_ids:
                doc = db.query(Document).filter(
                    Document.id == doc_id
                ).first()

                if not doc:
                    logger.warning("Document %s not found — skipping.", doc_id)
                    continue

                if doc.source_type == "legal_case":
                    chunks = _search_qdrant_by_doc(db, str(doc_id), query_vector)
                    logger.debug("Qdrant returned %d chunks for doc %s", len(chunks), doc_id)
                else:  # "uploaded"
                    chunks = _search_pgvector_by_doc(db, str(doc_id), query_vector)
                    logger.debug("pgvector returned %d chunks for doc %s", len(chunks), doc_id)

                all_chunks.extend(chunks)

    except Exception as exc:
        logger.error("DocumentChat retrieval error: %s", exc)
        return {**state, "answer": "Retrieval failed. Please try again.",
                "citations": [], "retrieved_chunks": [], "error": str(exc)}

    if not all_chunks:
        return {
            **state,
            "answer": "I could not find relevant content in the attached documents for your question.",
            "citations": [],
            "retrieved_chunks": [],
        }

    context   = _build_context(all_chunks)
    citations = _build_citations(all_chunks)

    # ── LLM call ──────────────────────────────────────────────────────────────
    user_prompt = f"Context:\n\n{context}\n\nQuestion: {question}\n\nAnswer:"
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})

    try:
        api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
        model   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        client  = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.1,
            max_tokens=1500,
            stream=False,
        )

        answer = _clean(response.choices[0].message.content or "")
        logger.info("DocumentChat answered (%d chars, %d citations)", len(answer), len(citations))
        return {**state, "answer": answer,
                "citations": citations, "retrieved_chunks": all_chunks}

    except Exception as exc:
        logger.error("DocumentChat LLM error: %s", exc)
        return {**state, "answer": "The AI encountered an error. Please try again.",
                "citations": citations, "retrieved_chunks": all_chunks, "error": str(exc)}
