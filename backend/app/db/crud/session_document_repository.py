"""
SessionDocument Repository — Attach/detach Documents to/from AssistantSessions.
"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import Document, SessionDocument


def attach_document(
    db: Session, session_id: uuid.UUID, document_id: uuid.UUID
) -> SessionDocument:
    """Attach a document to a session. Idempotent — no error if already attached."""
    existing = (
        db.query(SessionDocument)
        .filter(
            SessionDocument.session_id == session_id,
            SessionDocument.document_id == document_id,
        )
        .first()
    )
    if existing:
        return existing

    link = SessionDocument(session_id=session_id, document_id=document_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def detach_document(
    db: Session, session_id: uuid.UUID, document_id: uuid.UUID
) -> bool:
    """Detach a document from a session. Returns True if found and deleted."""
    link = (
        db.query(SessionDocument)
        .filter(
            SessionDocument.session_id == session_id,
            SessionDocument.document_id == document_id,
        )
        .first()
    )
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True


def get_session_documents(
    db: Session, session_id: uuid.UUID
) -> List[Document]:
    """Return all Document objects attached to a session."""
    links = (
        db.query(SessionDocument)
        .filter(SessionDocument.session_id == session_id)
        .all()
    )
    return [link.document for link in links]


def get_attached_document_ids(
    db: Session, session_id: uuid.UUID
) -> List[uuid.UUID]:
    """Return just the UUIDs of all documents attached to a session (for retrieval queries)."""
    links = (
        db.query(SessionDocument.document_id)
        .filter(SessionDocument.session_id == session_id)
        .all()
    )
    return [link.document_id for link in links]
