"""
Database package for JurisFind persistent document sessions.

This package contains SQLAlchemy models, database configuration,
and session management for the persistent document sessions feature.
"""

from .models import Base, User, DocumentSession, DocumentChunk, ChatSession, ChatMessage
from .config import engine, SessionLocal, get_engine, get_session_factory
from .session import get_db, DatabaseSession, create_tables, drop_tables

__all__ = [
    # Models
    "Base",
    "User",
    "DocumentSession",
    "DocumentChunk",
    "ChatSession",
    "ChatMessage",
    # Configuration
    "engine",
    "SessionLocal",
    "get_engine",
    "get_session_factory",
    # Session management
    "get_db",
    "DatabaseSession",
    "create_tables",
    "drop_tables",
]
