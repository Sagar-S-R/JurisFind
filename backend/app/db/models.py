"""
SQLAlchemy models for JurisFind V2.

Domain model centred on AssistantSession (ChatGPT-style conversation):

  User (1) ──── (N) AssistantSession (1) ──── (N) Message
                          │
                          └──── (M:N via SessionDocument) ──── (1) Document
                                                                       │
                                                                   (N) DocumentChunk
                                                                       │
                                                                   (1) DocumentEmbedding
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


# ── User ──────────────────────────────────────────────────────────────────────

class User(Base):
    """
    Authenticated user. Owns AssistantSessions and uploaded Documents.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship(
        "AssistantSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    documents = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Document.owner_id",
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


# ── AssistantSession ──────────────────────────────────────────────────────────

class AssistantSession(Base):
    """
    A ChatGPT-style conversation session.

    Contains an ordered sequence of Messages and has many Documents
    attached via the SessionDocument join table.
    """
    __tablename__ = "assistant_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(500), nullable=False, default="New Session")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    session_documents = relationship(
        "SessionDocument",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    # Convenience accessor (not a DB column)
    @property
    def documents(self):
        return [sd.document for sd in self.session_documents]

    __table_args__ = (
        Index("ix_assistant_sessions_user_updated", "user_id", "updated_at"),
    )

    def __repr__(self):
        return f"<AssistantSession(id={self.id}, title={self.title!r})>"


# ── Message ───────────────────────────────────────────────────────────────────

class Message(Base):
    """
    A single turn in an AssistantSession conversation.

    role:         'user' | 'assistant' | 'system'
    message_type: 'text' | 'summary_card' | 'event_card'
    citations:    JSON list of {doc_name, page_number, excerpt} for RAG answers
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assistant_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(
        Enum("user", "assistant", "system", name="message_role_enum_v2"),
        nullable=False,
    )
    message_type = Column(
        Enum("text", "summary_card", "event_card", "legal_notice_card", name="message_type_enum"),
        nullable=False,
        default="text",
    )
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)  # [{doc_name, page_number, excerpt}]
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("AssistantSession", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_session_created", "session_id", "created_at"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, type={self.message_type})>"


# ── Document ──────────────────────────────────────────────────────────────────

class Document(Base):
    """
    A reusable PDF document resource.

    Can be:
      - owner_id=NULL, source_type='legal_case'  → pre-indexed corpus case
      - owner_id=UUID, source_type='uploaded'    → user-uploaded PDF

    Documents are independent of sessions. Sessions reference documents
    via the SessionDocument join table. Processing state is tracked here.

    file_hash: SHA-256 of the raw PDF bytes — used for upload deduplication.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_type = Column(
        Enum("uploaded", "legal_case", name="doc_source_type_enum"),
        nullable=False,
    )
    title = Column(String(500), nullable=False)
    blob_path = Column(String(1000), nullable=False)
    file_hash = Column(String(64), nullable=True, unique=True)
    file_size_bytes = Column(Integer, nullable=True)
    status = Column(
        Enum("uploaded", "processing", "ready", "failed", name="doc_status_enum"),
        nullable=False,
        default="uploaded",
    )
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="documents", foreign_keys=[owner_id])
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    session_documents = relationship(
        "SessionDocument",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_documents_status", "status"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title!r}, status={self.status})>"


# ── SessionDocument (join table) ──────────────────────────────────────────────

class SessionDocument(Base):
    """
    Many-to-many association between AssistantSession and Document.

    A session can have many documents.
    A document can belong to many sessions.
    Deleting a session cleans up these links but NOT the document records.
    """
    __tablename__ = "session_documents"

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assistant_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    attached_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("AssistantSession", back_populates="session_documents")
    document = relationship("Document", back_populates="session_documents")

    def __repr__(self):
        return (
            f"<SessionDocument(session={self.session_id}, doc={self.document_id})>"
        )


# ── DocumentChunk ─────────────────────────────────────────────────────────────

class DocumentChunk(Base):
    """
    A sequential text segment extracted from a Document page.

    chunk_index: zero-based ordering within the document.
    Owned by Document — not by Session.
    """
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    page_number = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")
    embedding = relationship(
        "DocumentEmbedding",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_document_chunks_doc_page", "document_id", "page_number"),
    )

    def __repr__(self):
        return (
            f"<DocumentChunk(id={self.id}, doc={self.document_id}, "
            f"page={self.page_number}, idx={self.chunk_index})>"
        )


# ── DocumentEmbedding ─────────────────────────────────────────────────────────

class DocumentEmbedding(Base):
    """
    The 768-dimensional pgvector embedding for a DocumentChunk.

    One-to-one with DocumentChunk.
    Owned by Document (cascade delete from Document removes all embeddings).

    document_id is denormalised here for efficient filtered vector search:
        SELECT ... WHERE document_id = ANY(:ids) ORDER BY embedding <=> :query_vec

    The HNSW index (created in migration) makes this sub-50ms even at scale.
    """
    __tablename__ = "document_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # pgvector column: 768-dim float vector
    embedding = Column(Vector(768), nullable=False)

    # Relationships
    chunk = relationship("DocumentChunk", back_populates="embedding")

    def __repr__(self):
        return f"<DocumentEmbedding(id={self.id}, chunk={self.chunk_id})>"
