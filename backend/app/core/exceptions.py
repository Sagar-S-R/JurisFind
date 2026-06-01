"""
Global exception handlers for JurisFind FastAPI application.

Returns consistent error response format:
    {
        "detail":     str,
        "error_code": str,
        "timestamp":  ISO8601 str,
        "request_id": str (UUID)
    }

Registered via register_error_handlers(app) in main.py.
"""

import logging
import traceback
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _error_body(
    detail: str,
    error_code: str,
    request_id: str,
) -> dict:
    """Construct the standard error response body."""
    return {
        "detail": detail,
        "error_code": error_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
    }


def _get_request_id(request: Request) -> str:
    """Return X-Request-ID header if present, else generate one."""
    return request.headers.get("X-Request-ID", str(uuid.uuid4()))


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI app instance.

    Call this inside create_app() after the app is constructed.
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI/Starlette HTTP exceptions (401, 403, 404, 409, etc.)."""
        request_id = _get_request_id(request)
        error_code = f"HTTP_{exc.status_code}"

        logger.warning(
            "HTTPException %s | %s | path=%s request_id=%s",
            exc.status_code,
            exc.detail,
            request.url.path,
            request_id,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(
                detail=exc.detail,
                error_code=error_code,
                request_id=request_id,
            ),
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors (400 Bad Request)."""
        request_id = _get_request_id(request)

        # Flatten validation errors into a readable message
        errors = exc.errors()
        messages = []
        for err in errors:
            loc = " → ".join(str(l) for l in err.get("loc", []))
            msg = err.get("msg", "Validation error")
            messages.append(f"{loc}: {msg}" if loc else msg)

        detail = "; ".join(messages) if messages else "Invalid request data."

        logger.warning(
            "ValidationError | path=%s request_id=%s errors=%s",
            request.url.path,
            request_id,
            errors,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body(
                detail=detail,
                error_code="VALIDATION_ERROR",
                request_id=request_id,
            ),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Catch-all handler for unhandled exceptions (500 Internal Server Error).

        Logs the full stack trace but returns a generic message to the client
        (never exposes implementation details).
        """
        request_id = _get_request_id(request)

        logger.error(
            "Unhandled exception | path=%s request_id=%s\n%s",
            request.url.path,
            request_id,
            traceback.format_exc(),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                detail="An internal server error occurred. Please try again later.",
                error_code="INTERNAL_SERVER_ERROR",
                request_id=request_id,
            ),
        )
