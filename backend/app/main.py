import logging
import os
import sys
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend/ is in sys.path
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.

    Document processing is now handled by an external Celery worker process
    (connected via RabbitMQ).  FastAPI is fully stateless — no background
    asyncio tasks are spawned here.

    Start the Celery worker separately:
        celery -A workers.celery_app worker --loglevel=info -P prefork -Q jurisfind_documents

    Or via Docker Compose:
        docker compose up celery_worker
    """
    logger.info(
        "JurisFind API starting up. "
        "Document processing offloaded to Celery worker (RabbitMQ broker)."
    )
    yield  # Application runs here
    logger.info("JurisFind API shutting down.")


# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Load .env early so all downstream imports can access env vars
    _dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    try:
        load_dotenv(dotenv_path=_dotenv_path, override=False)
        groq = os.environ.get("GROQ_API_KEY", "")
        masked = (
            f"{groq[:4]}...{groq[-4:]}"
            if groq and len(groq) >= 8
            else "(missing or too short)"
        )
        print(f"Env loaded from: {_dotenv_path} | GROQ_API_KEY: {masked}")
    except Exception as _e:
        print(f"Warning: Could not load .env from {_dotenv_path}: {_e}")

    app = FastAPI(
        title="JurisFind API",
        description=(
            "AI-powered legal document search and analysis platform. "
            "Semantic search over 46,456+ legal cases, persistent document sessions, "
            "RAG-based Q&A, and a legal domain chatbot."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",          # Vite dev server
            "http://localhost:3000",          # React dev server
            "http://20.186.113.106",          # Azure VM public IP
            "https://jurisfind.vercel.app",   # Vercel frontend
            "https://blue-cliff-0dfeb910f.2.azurestaticapps.net",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global error handlers ─────────────────────────────────────────────────
    from app.core.exceptions import register_error_handlers
    register_error_handlers(app)

    # ── API Business-Capability Routes ────────────────────────────────────────
    from app.api.auth import router as auth_router
    from app.api.cases import router as cases_router
    from app.api.documents import router as documents_router
    from app.api.chat import router as chat_router

    app.include_router(auth_router, prefix="/api")
    app.include_router(cases_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")

    # ── Root endpoint ─────────────────────────────────────────────────────────
    @app.get("/", tags=["Root"])
    async def home():
        storage_info = (
            "Azure Blob Storage"
            if os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            else "Local Files"
        )
        return {
            "message": "JurisFind API - Legal AI Platform",
            "version": "2.0.0",
            "storage_backend": storage_info,
            "api_endpoints": {
                "docs": "/docs",
                "health": "/api/health (GET)",
                "auth_register": "/api/auth/register (POST)",
                "auth_login": "/api/auth/login (POST)",
                "cases_search": "/api/cases/search (POST/GET)",
                "cases_get": "/api/cases/{case_id} (GET)",
                "pdf_files": "/api/pdf/{filename} (GET)",
                "documents_ingest": "/api/documents (POST)",
                "documents_list": "/api/documents (GET)",
                "documents_status": "/api/documents/{id}/status (GET)",
                "documents_analysis": "/api/documents/{id}/analysis (GET)",
                "documents_chat": "/api/documents/{id}/chat (POST/GET)",
                "documents_similar": "/api/documents/{id}/similar-cases (GET)",
                "chat_legal": "/api/chat/legal (POST)",
            },
            "azure_features": {
                "enabled": bool(os.getenv("AZURE_STORAGE_CONNECTION_STRING")),
                "container": os.getenv("AZURE_DATA_CONTAINER", "data"),
            },
        }


    return app


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    """Run the FastAPI server."""
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    reload = os.environ.get("RELOAD", "False").lower() == "true"

    print("=" * 50)
    print("🚀 Starting JurisFind FastAPI Server")
    print("=" * 50)
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 Docs:   http://{host}:{port}/docs")
    print("=" * 50)

    try:
        uvicorn.run(
            "main:create_app",
            factory=True,
            host=host,
            port=port,
            reload=reload,
        )
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")


if __name__ == "__main__":
    main()
