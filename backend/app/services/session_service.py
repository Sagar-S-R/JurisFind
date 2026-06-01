"""
Session service for JurisFind.

Handles creation, retrieval, listing, update, and deletion of
DocumentSessions and ChatSessions, plus ChatMessage persistence.

All cross-user access is blocked at this layer (HTTP 403).
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.models import (
    DocumentSession,
    DocumentChunk,
    ChatSession,
    ChatMessage,
)


class SessionService:
    """
    Service for managing DocumentSession and ChatSession lifecycle.

    Implements the repository pattern internally — all DB access goes through
    this service; routes never query the ORM directly.
    """

    # ── DocumentSession CRUD ─────────────────────────────────────────────────

    def create_document_session(
        self,
        db: Session,
        user_id: str,
        document_name: str,
        blob_path: str,
        source_type: str,  # "uploaded" | "retrieved"
    ) -> DocumentSession:
        """
        Create a new DocumentSession with status 'pending'.

        Args:
            db: SQLAlchemy session
            user_id: UUID string of the authenticated user
            document_name: Original filename
            blob_path: Blob Storage path (documents/{user_id}/{uuid}.pdf)
            source_type: 'uploaded' or 'retrieved'

        Returns:
            DocumentSession: Newly created and committed session
        """
        session = DocumentSession(
            session_id=uuid.uuid4(),
            user_id=user_id,
            document_name=document_name,
            blob_path=blob_path,
            source_type=source_type,
            processing_status="pending",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_document_session(
        self,
        db: Session,
        session_id: str,
        user_id: str,
    ) -> DocumentSession:
        """
        Retrieve a DocumentSession, enforcing user ownership.

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session
            user_id: UUID string of the requesting user

        Returns:
            DocumentSession

        Raises:
            HTTPException 404: If session not found
            HTTPException 403: If requesting user is not the owner
        """
        session = (
            db.query(DocumentSession)
            .filter(DocumentSession.session_id == session_id)
            .first()
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Document session not found.")
        if str(session.user_id) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this session.",
            )
        return session

    def list_user_sessions(
        self,
        db: Session,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[DocumentSession], int]:
        """
        List all DocumentSessions for a user, paginated, newest first.

        Args:
            db: SQLAlchemy session
            user_id: UUID string of the user
            page: Page number (1-indexed)
            page_size: Items per page (default 20, max 100)

        Returns:
            Tuple[List[DocumentSession], int]: (sessions, total_count)
        """
        page_size = min(max(1, page_size), 100)
        offset = (max(1, page) - 1) * page_size

        query = (
            db.query(DocumentSession)
            .filter(DocumentSession.user_id == user_id)
            .order_by(desc(DocumentSession.created_at))
        )
        total_count = query.count()
        sessions = query.offset(offset).limit(page_size).all()
        return sessions, total_count

    def update_processing_status(
        self,
        db: Session,
        session_id: str,
        status: str,
        error_message: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> DocumentSession:
        """
        Update processing_status (and optionally summary/error_message).

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session
            status: New status ('pending'|'processing'|'completed'|'failed')
            error_message: Error details on failure
            summary: Generated document summary on completion

        Returns:
            DocumentSession: Updated instance

        Raises:
            HTTPException 404: If session not found
        """
        session = (
            db.query(DocumentSession)
            .filter(DocumentSession.session_id == session_id)
            .first()
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Document session not found.")

        session.processing_status = status
        session.updated_at = datetime.now(timezone.utc)
        if error_message is not None:
            session.error_message = error_message
        if summary is not None:
            session.summary = summary

        db.commit()
        db.refresh(session)
        return session

    def delete_document_session(
        self,
        db: Session,
        session_id: str,
        user_id: str,
    ) -> None:
        """
        Delete a DocumentSession and all cascading data (chunks, chat).

        DB cascade handles DocumentChunk, ChatSession, ChatMessage deletion.
        The caller is responsible for:
          - Removing embeddings from VectorStoreService
          - Deleting the blob from BlobStorageService

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session
            user_id: UUID string of the requesting user

        Raises:
            HTTPException 404: If session not found
            HTTPException 403: If user is not the owner
        """
        session = self.get_document_session(db, session_id, user_id)
        db.delete(session)
        db.commit()

    # ── DocumentChunk helpers ────────────────────────────────────────────────

    def get_chunks_by_refs(
        self,
        db: Session,
        embedding_refs: List[str],
    ) -> List[DocumentChunk]:
        """
        Retrieve DocumentChunks by their embedding_reference values.

        Args:
            db: SQLAlchemy session
            embedding_refs: List of embedding_reference strings

        Returns:
            List[DocumentChunk]: Matching chunks (may be fewer if some not found)
        """
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.embedding_reference.in_(embedding_refs))
            .all()
        )

    def get_session_chunks(
        self,
        db: Session,
        session_id: str,
    ) -> List[DocumentChunk]:
        """
        Retrieve all chunks for a session, ordered by page_number.

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session

        Returns:
            List[DocumentChunk]: Chunks ordered by page_number
        """
        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.session_id == session_id)
            .order_by(DocumentChunk.page_number)
            .all()
        )

    def get_session_embedding_refs(
        self,
        db: Session,
        session_id: str,
    ) -> List[str]:
        """
        Get all embedding_reference values for a session (for FAISS cleanup).

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session

        Returns:
            List[str]: All embedding_reference strings for the session
        """
        chunks = (
            db.query(DocumentChunk.embedding_reference)
            .filter(DocumentChunk.session_id == session_id)
            .all()
        )
        return [c.embedding_reference for c in chunks]

    # ── ChatSession CRUD ─────────────────────────────────────────────────────

    def get_or_create_chat_session(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        first_question: str,
    ) -> ChatSession:
        """
        Return existing ChatSession for this document session, or create one.

        Creates a new ChatSession with a title derived from the first_question
        if none exists yet. Only one ChatSession per DocumentSession is created
        (subsequent questions reuse the same chat).

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session
            user_id: UUID string of the user
            first_question: The user's question (used as title source)

        Returns:
            ChatSession: Existing or newly created instance
        """
        existing = (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )
        if existing:
            return existing

        # Generate title from first 80 chars of the first question
        title = first_question.strip()[:80]
        if len(first_question.strip()) > 80:
            title += "..."

        chat = ChatSession(
            chat_id=uuid.uuid4(),
            session_id=session_id,
            user_id=user_id,
            title=title,
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    def get_chat_session(
        self,
        db: Session,
        session_id: str,
        user_id: str,
    ) -> Optional[ChatSession]:
        """
        Retrieve the ChatSession for a document session (if it exists).

        Args:
            db: SQLAlchemy session
            session_id: UUID string of the document session
            user_id: UUID string of the user

        Returns:
            ChatSession | None
        """
        return (
            db.query(ChatSession)
            .filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id,
            )
            .first()
        )

    def add_chat_message(
        self,
        db: Session,
        chat_id: str,
        role: str,
        message: str,
        retrieved_chunks: Optional[List[str]] = None,
        llm_response: Optional[str] = None,
    ) -> ChatMessage:
        """
        Persist a chat message (user or assistant).

        Args:
            db: SQLAlchemy session
            chat_id: UUID string of the chat session
            role: 'user' or 'assistant'
            message: Message content
            retrieved_chunks: List of chunk_ids used (assistant messages only)
            llm_response: Raw LLM response (assistant messages only)

        Returns:
            ChatMessage: Newly created and committed message
        """
        msg = ChatMessage(
            message_id=uuid.uuid4(),
            chat_id=chat_id,
            role=role,
            message=message,
            retrieved_chunks=retrieved_chunks,
            llm_response=llm_response,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def get_chat_history(
        self,
        db: Session,
        chat_id: str,
        limit: Optional[int] = None,
    ) -> List[ChatMessage]:
        """
        Retrieve chat messages ordered by timestamp (ascending).

        Args:
            db: SQLAlchemy session
            chat_id: UUID string of the chat session
            limit: If set, returns only the last N messages

        Returns:
            List[ChatMessage]: Messages in chronological order
        """
        query = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.timestamp)
        )
        if limit:
            # Get last N messages while preserving chronological order
            total = query.count()
            offset = max(0, total - limit)
            query = query.offset(offset)

        return query.all()


# Module-level singleton
session_service = SessionService()
