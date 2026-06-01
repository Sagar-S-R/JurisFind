"""
Database configuration for JurisFind persistent document sessions.

This module configures the PostgreSQL database connection with connection pooling
and provides the SQLAlchemy engine and session factory.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment variable
# Format: postgresql://username:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/jurisfind"
)

# Create SQLAlchemy engine with connection pooling
# pool_size: Number of connections to maintain in the pool
# max_overflow: Maximum number of connections that can be created beyond pool_size
# pool_pre_ping: Verify connections before using them (handles stale connections)
# pool_recycle: Recycle connections after 3600 seconds (1 hour) to prevent stale connections
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,  # Set to True for SQL query logging during development
)

# Create session factory
# autocommit=False: Transactions must be explicitly committed
# autoflush=False: Changes are not automatically flushed to the database
# bind=engine: Bind the session to the engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_engine():
    """
    Get the SQLAlchemy engine instance.
    
    Returns:
        Engine: SQLAlchemy engine with connection pooling configured
    """
    return engine


def get_session_factory():
    """
    Get the SQLAlchemy session factory.
    
    Returns:
        sessionmaker: Session factory for creating database sessions
    """
    return SessionLocal
