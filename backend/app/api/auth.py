"""
Authentication routes — v1
POST /api/v1/auth/register  – create a new user account
POST /api/v1/auth/login     – authenticate and return a JWT token
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.services.auth_service import (
    auth_service,
    DuplicateEmailError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["v1 · Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    response_description="User ID of the newly created account",
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters

    Returns the new user's `user_id` (UUID v4).
    """
    try:
        user = auth_service.register_user(db, request.email, request.password)
        logger.info("New user registered: %s", request.email)
        return {
            "user_id": str(user.id),
            "email": user.email,
            "message": "Account created successfully.",
        }
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception("Unexpected error during registration: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to an internal error.",
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain a JWT token",
    response_description="JWT access token valid for 24 hours",
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate with email and password.

    Returns a JWT `access_token` valid for 24 hours.
    Include it in subsequent requests as:
    `Authorization: Bearer <token>`
    """
    try:
        user = auth_service.authenticate_user(db, request.email, request.password)
        token = auth_service.create_access_token(str(user.id))
        logger.info("User logged in: %s", request.email)
        return TokenResponse(access_token=token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        logger.exception("Unexpected error during login: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to an internal error.",
        )
