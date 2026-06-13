"""
JurisFind LangGraph State Definition.

This TypedDict is the single source of truth that flows through every node
in the graph. It is ephemeral — one fresh instance is created per request
and discarded after the response is streamed.
"""
from typing import Optional, TypedDict


class JurisFindState(TypedDict):
    # ── Input ─────────────────────────────────────────────────────────────────
    session_id:       str
    user_id:          str
    question:         str
    history:          list[dict]    # last N turns loaded from messages table
    explicit_mode:    Optional[str] # "auto" | "document" | "corpus" — frontend toggle
    document_ids:     list[str]     # doc IDs attached to this session

    # ── Classifier output ─────────────────────────────────────────────────────
    is_legal:         bool
    intent:           str           # "general" | "document_chat" | "corpus_search"

    # ── Retrieval output ──────────────────────────────────────────────────────
    retrieved_chunks: list[dict]    # raw results from Qdrant or pgvector
    citations:        list[dict]    # built directly from chunk payloads

    # ── Final output ──────────────────────────────────────────────────────────
    answer:           str
    error:            Optional[str]
