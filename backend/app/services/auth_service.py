"""
Authentication service for JurisFind.

Handles user registration, password hashing with bcrypt,
credential verification, and JWT token management (HS256, 24-hour expiry).
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from app.db.models import User

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "changeme-in-production")
ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class DuplicateEmailError(Exception):
    """Raised when registering with an already-used email."""
    pass


class AuthenticationService:
    """
    Service for user registration, login, and JWT token management.

    Usage:
        auth_svc = AuthenticationService()
        user = auth_svc.register_user(db, email, password)
        token = auth_svc.create_access_token(str(user.id))
        user_id = auth_svc.verify_token(token)
    """

    # ── Password helpers ─────────────────────────────────────────────────────

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password with bcrypt."""
        pw_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pw_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    # ── User management ──────────────────────────────────────────────────────

    def register_user(self, db: Session, email: str, password: str) -> User:
        """
        Register a new user with hashed password.

        Args:
            db: SQLAlchemy database session
            email: User email address
            password: Plaintext password (min 8 chars enforced at schema layer)

        Returns:
            User: Newly created User model instance

        Raises:
            DuplicateEmailError: If email is already registered
        """
        # Check for existing email
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise DuplicateEmailError(f"Email '{email}' is already registered.")

        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=self.hash_password(password),
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        """
        Verify credentials and return the user.

        Args:
            db: SQLAlchemy database session
            email: User email address
            password: Plaintext password

        Returns:
            User: Authenticated User model instance

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = db.query(User).filter(User.email == email).first()
        if not user or not self.verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        return user

    # ── JWT management ───────────────────────────────────────────────────────

    @staticmethod
    def create_access_token(user_id: str) -> str:
        """
        Create a JWT access token for the given user_id.

        Args:
            user_id: String representation of the user's UUID

        Returns:
            str: Signed JWT token (HS256, 24-hour expiration)
        """
        expire = datetime.now(timezone.utc) + timedelta(hours=EXPIRATION_HOURS)
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> str:
        """
        Decode and verify a JWT token, returning the user_id.

        Args:
            token: JWT token string

        Returns:
            str: user_id extracted from the token subject claim

        Raises:
            AuthenticationError: If the token is invalid, expired, or malformed
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: Optional[str] = payload.get("sub")
            if user_id is None:
                raise AuthenticationError("Token missing subject claim.")
            return user_id
        except JWTError as exc:
            raise AuthenticationError(f"Token validation failed: {exc}") from exc


# Module-level singleton for dependency injection
auth_service = AuthenticationService()
