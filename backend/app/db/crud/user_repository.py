"""
User repository for JurisFind.

Abstracts all SQLAlchemy queries related to the User model.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:
    """CRUD operations for the User model."""

    @staticmethod
    def get_by_id(db: Session, user_id: str) -> Optional[User]:
        """Fetch a user by UUID string."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch a user by email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user: User) -> User:
        """Persist a new User record."""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def exists_by_email(db: Session, email: str) -> bool:
        """Return True if a user with the given email exists."""
        return db.query(User.id).filter(User.email == email).first() is not None

    @staticmethod
    def delete(db: Session, user: User) -> None:
        """Delete a user record."""
        db.delete(user)
        db.commit()
