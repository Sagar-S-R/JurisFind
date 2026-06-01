"""
Celery document processing task for JurisFind.

Replaces the old asyncio.Queue-based DocumentWorker class with a proper
Celery task that executes in Celery's pre-fork process pool, bypassing
the GIL limitation and keeping FastAPI completely stateless.

Task name:  process_document_task
Queue:      jurisfind_documents
Retry:      Up to 3 automatic retries with exponential back-off

Usage (from FastAPI routes):
    from workers.document_worker import process_document_task
    process_document_task.delay(session_id=session_id, blob_path=blob_path)

Boot the worker:
    celery -A workers.celery_app worker --loglevel=info -P prefork -Q jurisfind_documents
"""

import logging
import os
import sys

# ── Ensure backend/ is on sys.path when the worker process boots directly ─────────
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app.workers.celery_app import celery_app  # noqa: E402 (must be after sys.path fix)

logger = logging.getLogger(__name__)


@celery_app.task(
    name="process_document_task",
    bind=True,                  # gives access to self (the task instance)
    queue="jurisfind_documents",
    max_retries=3,
    default_retry_delay=30,     # seconds between retries (base; Celery doubles it)
    acks_late=True,             # honour the global acks_late setting explicitly
)
def process_document_task(self, session_id: str, blob_path: str) -> dict:
    """
    Celery task: run the full document processing pipeline for a session.

    Executes synchronously inside Celery's worker process pool — no event
    loop, no asyncio.to_thread() required.  All heavy CPU/IO work (embedding
    generation, PDF parsing, Groq API call) runs natively in-process.

    Args:
        session_id: UUID string of the DocumentSession record in PostgreSQL.
        blob_path:  Blob Storage path (or local path) to the PDF file.

    Returns:
        dict with {"session_id": str, "status": "completed"} on success.

    Raises:
        Retries the task (up to max_retries) on unexpected exceptions.
        The processing service itself writes the "failed" status to DB.
    """
    logger.info(
        "[Task %s] Starting document processing | session=%s blob=%s",
        self.request.id,
        session_id,
        blob_path,
    )

    try:
        # Late import avoids circular-import issues at module load time and
        # defers the heavy model initialisation to the worker process only.
        from app.services.document_processing_service import document_processing_service

        # process_document() is fully synchronous — perfect for Celery's
        # prefork pool.  The service handles its own DB status updates
        # (pending → processing → completed | failed).
        document_processing_service.process_document(session_id, blob_path)

        logger.info(
            "[Task %s] Document processing completed | session=%s",
            self.request.id,
            session_id,
        )
        return {"session_id": session_id, "status": "completed"}

    except Exception as exc:
        logger.exception(
            "[Task %s] Unexpected error during processing | session=%s: %s",
            self.request.id,
            session_id,
            exc,
        )
        # Retry with exponential back-off; raises MaxRetriesExceededError
        # after max_retries attempts (the service has already marked it failed).
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
