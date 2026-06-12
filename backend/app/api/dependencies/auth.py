"""
JWT authentication dependency for FastAPI.

Provides get_current_user() dependency that:
1. Extracts the Bearer token from the Authorization header
2. Validates the JWT and returns the user_id (str UUID)
3. Raises HTTP 401 for missing/invalid/expired tokens
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth_service import auth_service, AuthenticationError

# OAuth2 / Bearer token extractors
_bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="JWT access token obtained from POST /auth/login",
    auto_error=True,  # raises 403 if Authorization header is missing
)

_optional_bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="JWT access token obtained from POST /auth/login",
    auto_error=False,  # does NOT raise 403 if missing
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """
    FastAPI dependency: extract and validate the JWT, return user_id.

    Raises:
        HTTPException 401: If the token is missing, expired, or invalid
    """
    token = credentials.credentials
    try:
        user_id = auth_service.verify_token(token)
        return user_id
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer_scheme),
) -> Optional[str]:
    """
    FastAPI dependency: extract and validate JWT if present, return user_id or None.
    """
    if not credentials:
        return None
    token = credentials.credentials
    try:
        user_id = auth_service.verify_token(token)
        return user_id
    except AuthenticationError:
        return None

