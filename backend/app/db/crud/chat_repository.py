"""
Chat repository for JurisFind.

Abstracts SQLAlchemy queries for ChatSession and ChatMessage models.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.db.models import ChatSession, ChatMessage


class ChatRepository:
    """CRUD and query operations for ChatSession and ChatMessage."""

    # ── ChatSession ───────────────────────────────────────────────────────────

    @staticmethod
    def get_session(
        db: Session, session_id: str, user_id: str
    ) -> Optional[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def create_session(db: Session, chat: ChatSession) -> ChatSession:
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def delete_session(db: Session, chat: ChatSession) -> None:
        db.delete(chat)
        db.commit()

    # ── ChatMessage ───────────────────────────────────────────────────────────

    @staticmethod
    def add_message(db: Session, message: ChatMessage) -> ChatMessage:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    @staticmethod
    def get_messages(
        db: Session,
        chat_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatMessage]:
        """Return messages in chronological order, optionally limited to last N."""
        q = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.timestamp)
        )
        if limit:
            total = q.count()
            offset = max(0, total - limit)
            q = q.offset(offset)
        return q.all()

    @staticmethod
    def count_messages(db: Session, chat_id: str) -> int:
        return db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).count()
