"""
SQLAlchemy models for JurisFind persistent document sessions.

This module defines the database schema for users, document sessions,
document chunks, chat sessions, and chat messages.
"""

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    Enum,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """
    User model for authentication and session ownership.
    
    Attributes:
        id: Unique user identifier (UUID v4)
        email: User email address (unique)
        hashed_password: Bcrypt hashed password
        role: User role (default: "user")
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document_sessions = relationship(
        "DocumentSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class DocumentSession(Base):
    """
    Document session model tracking document lifecycle and processing state.
    
    Attributes:
        session_id: Unique session identifier (UUID v4)
        user_id: Foreign key to users table
        source_type: Document source ("uploaded" or "retrieved")
        document_name: Original document filename
        blob_path: Azure Blob Storage path
        summary: Generated document summary
        processing_status: Current processing state
        error_message: Error details if processing failed
        created_at: Session creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "document_sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    source_type = Column(
        Enum("uploaded", "retrieved", name="source_type_enum"),
        nullable=False
    )
    document_name = Column(String(500), nullable=False)
    blob_path = Column(String(1000), nullable=False)
    summary = Column(Text, nullable=True)
    processing_status = Column(
        Enum("pending", "processing", "completed", "failed", name="processing_status_enum"),
        default="pending",
        nullable=False
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="document_sessions")
    chunks = relationship(
        "DocumentChunk",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession",
        back_populates="document_session",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_user_created", "user_id", "created_at"),
        Index("idx_processing_status", "processing_status"),
    )
    
    def __repr__(self):
        return (
            f"<DocumentSession(session_id={self.session_id}, "
            f"document_name={self.document_name}, "
            f"status={self.processing_status})>"
        )


class DocumentChunk(Base):
    """
    Document chunk model storing text segments with embeddings.
    
    Attributes:
        chunk_id: Unique chunk identifier (UUID v4)
        session_id: Foreign key to document_sessions table
        page_number: Page number in source document
        chunk_text: Extracted text content
        chunk_metadata: Additional chunk metadata (JSON)
        embedding_reference: Reference to vector embedding in FAISS
        created_at: Chunk creation timestamp
    """
    __tablename__ = "document_chunks"
    
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    page_number = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    embedding_reference = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("DocumentSession", back_populates="chunks")
    
    # Indexes
    __table_args__ = (
        Index("idx_session_page", "session_id", "page_number"),
    )
    
    def __repr__(self):
        return (
            f"<DocumentChunk(chunk_id={self.chunk_id}, "
            f"session_id={self.session_id}, "
            f"page={self.page_number})>"
        )


class ChatSession(Base):
    """
    Chat session model for conversation threads.
    
    Attributes:
        chat_id: Unique chat identifier (UUID v4)
        session_id: Foreign key to document_sessions table
        user_id: Foreign key to users table
        title: Chat session title (generated from first message)
        created_at: Chat creation timestamp
    """
    __tablename__ = "chat_sessions"
    
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    document_session = relationship("DocumentSession", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "ChatMessage",
        back_populates="chat_session",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return (
            f"<ChatSession(chat_id={self.chat_id}, "
            f"session_id={self.session_id}, "
            f"title={self.title})>"
        )


class ChatMessage(Base):
    """
    Chat message model storing conversation history.
    
    Attributes:
        message_id: Unique message identifier (UUID v4)
        chat_id: Foreign key to chat_sessions table
        role: Message role ("user" or "assistant")
        message: Message content
        retrieved_chunks: Array of chunk_ids used for response (JSON)
        llm_response: Raw LLM response text
        timestamp: Message timestamp
    """
    __tablename__ = "chat_messages"
    
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.chat_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role = Column(
        Enum("user", "assistant", name="message_role_enum"),
        nullable=False
    )
    message = Column(Text, nullable=False)
    retrieved_chunks = Column(JSON, nullable=True)  # Array of chunk_ids
    llm_response = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index("idx_chat_timestamp", "chat_id", "timestamp"),
    )
    
    def __repr__(self):
        return (
            f"<ChatMessage(message_id={self.message_id}, "
            f"chat_id={self.chat_id}, "
            f"role={self.role})>"
        )
