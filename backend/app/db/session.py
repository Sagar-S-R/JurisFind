"""
SQLAlchemy session management and dependency injection for FastAPI.

This module provides database session management with automatic cleanup
and dependency injection for FastAPI route handlers.
"""

from typing import Generator
from sqlalchemy.orm import Session
from .config import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    This function creates a new SQLAlchemy session for each request,
    yields it to the route handler, and ensures it's closed after the request
    completes (even if an exception occurs).
    
    Usage in FastAPI routes:
        @app.get("/example")
        def example_route(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        ```python
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from api.database.session import get_db
        
        @router.get("/users/{user_id}")
        def get_user(user_id: str, db: Session = Depends(get_db)):
            user = db.query(User).filter(User.id == user_id).first()
            return user
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseSession:
    """
    Context manager for database sessions outside of FastAPI routes.
    
    This class provides a context manager for database operations
    that need to be performed outside of FastAPI request handlers,
    such as in background tasks, CLI scripts, or tests.
    
    Usage:
        with DatabaseSession() as db:
            user = db.query(User).filter(User.email == "test@example.com").first()
            # Session is automatically committed and closed
    
    Example:
        ```python
        from api.database.session import DatabaseSession
        from api.database.models import User
        
        # In a background task or script
        with DatabaseSession() as db:
            user = User(email="test@example.com", hashed_password="...")
            db.add(user)
            db.commit()
        ```
    """
    
    def __init__(self):
        """Initialize the database session context manager."""
        self.db: Session = None
    
    def __enter__(self) -> Session:
        """
        Enter the context manager and create a new database session.
        
        Returns:
            Session: SQLAlchemy database session
        """
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and close the database session.
        
        If an exception occurred, the transaction is rolled back.
        Otherwise, changes are committed.
        
        Args:
            exc_type: Exception type (if an exception occurred)
            exc_val: Exception value (if an exception occurred)
            exc_tb: Exception traceback (if an exception occurred)
        """
        if exc_type is not None:
            # An exception occurred, rollback the transaction
            self.db.rollback()
        else:
            # No exception, commit the transaction
            self.db.commit()
        
        # Always close the session
        self.db.close()


def create_tables():
    """
    Create all database tables defined in SQLAlchemy models.
    
    This function should only be used for development and testing.
    In production, use Alembic migrations instead.
    
    Warning:
        This function does not handle schema migrations. Use Alembic
        for production database schema management.
    
    Example:
        ```python
        from api.database.session import create_tables
        
        # Create all tables (development only)
        create_tables()
        ```
    """
    from .models import Base
    from .config import engine
    
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables defined in SQLAlchemy models.
    
    Warning:
        This function permanently deletes all data in the database.
        Use with extreme caution and only in development/testing environments.
    
    Example:
        ```python
        from api.database.session import drop_tables
        
        # Drop all tables (development/testing only)
        drop_tables()
        ```
    """
    from .models import Base
    from .config import engine
    
    Base.metadata.drop_all(bind=engine)
