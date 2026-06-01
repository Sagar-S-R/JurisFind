"""
Document repository for JurisFind.

Abstracts SQLAlchemy queries for DocumentSession and DocumentChunk models.
"""

from typing import List, Optional, Tuple
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.models import DocumentSession, DocumentChunk


class DocumentRepository:
    """CRUD and query operations for DocumentSession and DocumentChunk."""

    # ── DocumentSession ───────────────────────────────────────────────────────

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[DocumentSession]:
        return (
            db.query(DocumentSession)
            .filter(DocumentSession.session_id == session_id)
            .first()
        )

    @staticmethod
    def list_sessions_by_user(
        db: Session,
        user_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[DocumentSession], int]:
        q = (
            db.query(DocumentSession)
            .filter(DocumentSession.user_id == user_id)
            .order_by(desc(DocumentSession.created_at))
        )
        total = q.count()
        sessions = q.offset(offset).limit(limit).all()
        return sessions, total

    @staticmethod
    def create_session(db: Session, session: DocumentSession) -> DocumentSession:
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def update_session(db: Session, session: DocumentSession) -> DocumentSession:
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete_session(db: Session, session: DocumentSession) -> None:
        db.delete(session)
        db.commit()

    # ── DocumentChunk ─────────────────────────────────────────────────────────

    @staticmethod
    def get_chunks_by_session(
        db: Session, session_id: str
    ) -> List[DocumentChunk]:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.session_id == session_id)
            .order_by(DocumentChunk.page_number)
            .all()
        )

    @staticmethod
    def get_chunks_by_refs(
        db: Session, embedding_refs: List[str]
    ) -> List[DocumentChunk]:
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding_reference.in_(embedding_refs))
            .all()
        )

    @staticmethod
    def get_embedding_refs(db: Session, session_id: str) -> List[str]:
        rows = (
            db.query(DocumentChunk.embedding_reference)
            .filter(DocumentChunk.session_id == session_id)
            .all()
        )
        return [r.embedding_reference for r in rows]

    @staticmethod
    def bulk_create_chunks(
        db: Session, chunks: List[DocumentChunk]
    ) -> None:
        db.add_all(chunks)
        db.commit()
