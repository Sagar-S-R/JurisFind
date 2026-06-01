"""
Celery application factory for JurisFind.

Creates the central Celery app instance that is imported by:
  - workers/document_worker.py  (task definitions)
  - Any future task modules under api/workers/

Broker:         RabbitMQ  (AMQP) — CELERY_BROKER_URL
Result Backend: PostgreSQL        — CELERY_RESULT_BACKEND

Both values are read from the environment (api/.env or Docker env_file).

Boot the worker locally:
    celery -A workers.celery_app worker --loglevel=info -P prefork -Q jurisfind_documents

Boot with concurrency override:
    celery -A workers.celery_app worker --loglevel=info -P prefork -c 4 -Q jurisfind_documents
"""

import logging
import os
import sys

from celery import Celery
from dotenv import load_dotenv

# ── Ensure api/ is on sys.path when the worker is launched directly ───────────
_API_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

# Load .env so env vars are available whether running locally or in Docker
_dotenv_path = os.path.abspath(os.path.join(_API_DIR, "..", ".env"))
load_dotenv(dotenv_path=_dotenv_path, override=False)

logger = logging.getLogger(__name__)

# ── Read configuration from environment ──────────────────────────────────────
_BROKER_URL = os.environ.get(
    "CELERY_BROKER_URL",
    "amqp://guest:guest@localhost:5672//",  # sane local-dev default
)
_RESULT_BACKEND = os.environ.get(
    "CELERY_RESULT_BACKEND",
    "db+postgresql://postgres:postgres@localhost:5432/jurisfind",
)

# ── Celery app instance ───────────────────────────────────────────────────────
celery_app = Celery(
    "jurisfind_worker",
    broker=_BROKER_URL,
    backend=_RESULT_BACKEND,
)

# ── Configuration ─────────────────────────────────────────────────────────────
celery_app.conf.update(
    # Serialization — JSON keeps tasks human-readable in the broker UI
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Routing — all document tasks go to a dedicated queue
    task_default_queue="jurisfind_documents",
    task_queues={
        "jurisfind_documents": {
            "exchange": "jurisfind_documents",
            "routing_key": "jurisfind_documents",
        }
    },

    # Reliability settings
    task_acks_late=True,           # ACK only after successful execution
    worker_prefetch_multiplier=1,  # One task per worker slot (fair dispatch)
    task_reject_on_worker_lost=True,  # Re-queue if the worker process crashes

    # Result expiry — keep results for 24 h then auto-delete
    result_expires=86400,

    # Timezone
    timezone="UTC",
    enable_utc=True,
)

# ── Auto-discover tasks inside the api.workers package ───────────────────────
celery_app.autodiscover_tasks(["workers"])

logger.info(
    "Celery app '%s' configured | broker=%s",
    celery_app.main,
    _BROKER_URL,
)
