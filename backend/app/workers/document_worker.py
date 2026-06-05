"""
Celery document processing task for JurisFind V2.

Task name:  process_document_task
Queue:      jurisfind_documents
Retry:      Up to 3 automatic retries with exponential back-off

V2 change: Task accepts document_id (not session_id).
           Processing pipeline writes to documents / document_chunks / document_embeddings.

Usage (from FastAPI routes):
    from app.workers.document_worker import process_document_task
    process_document_task.delay(document_id=str(doc.id), blob_path=blob_path)

Boot the worker:
    celery -A app.workers.celery_app worker --loglevel=info -P threads -Q jurisfind_documents
"""

import logging
import os
import sys

# Ensure backend/ is on sys.path when the worker process boots directly
_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app.workers.celery_app import celery_app  # noqa: E402

logger = logging.getLogger(__name__)


@celery_app.task(
    name="process_document_task",
    bind=True,
    queue="jurisfind_documents",
    max_retries=3,
    default_retry_delay=30,
    acks_late=True,
)
def process_document_task(self, document_id: str, blob_path: str) -> dict:
    """
    Celery task: run the full document processing pipeline for a Document.

    Executes synchronously inside Celery's worker process pool.
    Heavy CPU/IO work (embedding generation, PDF parsing, Groq API call)
    runs natively in-process.

    Args:
        document_id: UUID string of the Document record in PostgreSQL.
        blob_path:   Blob Storage path (or local path) to the PDF file.

    Returns:
        dict with {"document_id": str, "status": "ready"} on success.
    """
    logger.info(
        "[Task %s] Starting document processing | document_id=%s blob=%s",
        self.request.id,
        document_id,
        blob_path,
    )

    try:
        from app.services.document_processing_service import document_processing_service

        document_processing_service.process_document(document_id, blob_path)

        logger.info(
            "[Task %s] Document processing completed | document_id=%s",
            self.request.id,
            document_id,
        )
        return {"document_id": document_id, "status": "ready"}

    except Exception as exc:
        logger.exception(
            "[Task %s] Unexpected error during processing | document_id=%s: %s",
            self.request.id,
            document_id,
            exc,
        )
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
