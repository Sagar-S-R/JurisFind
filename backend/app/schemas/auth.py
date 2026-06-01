"""
Authentication schemas for request/response validation.

This module defines Pydantic schemas for user authentication endpoints including
registration, login, and token responses.
"""

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    Schema for user registration request.
    
    Validates:
    - Email format using EmailStr
    - Password minimum length of 8 characters
    """
    email: EmailStr = Field(
        ...,
        description="User email address in valid format",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User password with minimum 8 characters",
        examples=["SecurePassword123!"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class UserLoginRequest(BaseModel):
    """
    Schema for user login request.
    
    Validates:
    - Email format using EmailStr
    - Password presence (no minimum length for login)
    """
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["SecurePassword123!"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePassword123!"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """
    Schema for JWT token response after successful authentication.
    
    Returns:
    - access_token: JWT token string
    - token_type: Always "bearer"
    - expires_in: Token expiration time in seconds (default 24 hours)
    """
    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always bearer)",
        examples=["bearer"]
    )
    expires_in: int = Field(
        default=86400,
        description="Token expiration time in seconds (24 hours)",
        examples=[86400]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 86400
                }
            ]
        }
    }
