"""
Unified Document routes — v1

POST   /api/v1/documents                         – ingest document (upload / retrieve / ephemeral)
GET    /api/v1/documents                         – list all document sessions for current user
GET    /api/v1/documents/{document_id}           – session metadata
DELETE /api/v1/documents/{document_id}           – purge session + all data
GET    /api/v1/documents/{document_id}/status    – poll worker progress
GET    /api/v1/documents/{document_id}/analysis  – unified analysis (summary + stats)
POST   /api/v1/documents/{document_id}/chat      – Q&A gateway (persistent or ephemeral)
GET    /api/v1/documents/{document_id}/chat      – conversation thread history

Ingestion routing logic (POST /documents):
  - multipart/form-data + is_confidential=true  → ephemeral in-memory (no DB/blob)
  - multipart/form-data + is_confidential=false → persistent upload (Celery + blob)
  - application/json + source_type=database     → persistent retrieve from case index
"""

import logging
import os
import re
import tempfile
from typing import Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.dependencies.auth import get_current_user, get_optional_current_user
from app.ai.legal_agent import get_agent
from app.services.blob_storage_service import blob_storage_service, BlobStorageError
from app.services.session_service import session_service
from app.services.vector_store_service import vector_store_service
from app.services.document_processing_service import document_processing_service
from app.services.search_service import get_searcher
from app.workers.document_worker import process_document_task
from app.schemas.documents import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentSessionResponse,
    DocumentStatusResponse,
    DocumentSummaryResponse,
    DocumentUploadResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["v1 · Documents"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class DocumentIngestJsonRequest(BaseModel):
    """JSON body for ingesting an existing database case."""
    source_type: str           # "database"
    case_id: str               # filename / stable case identifier
    is_confidential: bool = False


class DocumentAnalysisResponse(BaseModel):
    document_id: str
    analysis: dict
    stats: dict
    processed_at: Optional[str] = None


class ChatRequest(BaseModel):
    question: str


class ChatMessageOut(BaseModel):
    message_id: str
    role: str
    message: str
    timestamp: Optional[str] = None


class ChatThreadResponse(BaseModel):
    document_id: str
    messages: list[ChatMessageOut]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _session_to_response(session) -> DocumentSessionResponse:
    return DocumentSessionResponse(
        session_id=session.session_id,
        document_name=session.document_name,
        source_type=session.source_type,
        processing_status=session.processing_status,
        summary=session.summary,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def _get_pdf_preview(filename: str) -> str:
    """Extract a short text snippet from a local case PDF."""
    local_pdf_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "pdfs",
    )
    pdf_path = os.path.join(local_pdf_dir, filename)
    if not os.path.exists(pdf_path):
        return "Legal case document details are available for analysis."
    try:
        import fitz  # PyMuPDF
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        idx = pdf_bytes.find(b"%PDF-")
        if idx > 0:
            pdf_bytes = pdf_bytes[idx:]
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for i in range(min(2, len(doc))):
            text += doc[i].get_text()
        doc.close()
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:400] + "..." if len(text) > 400 else (text or "Legal case document details are available for analysis.")
    except Exception:
        return "Legal case document details are available for analysis."


def _extract_key_points(summary: str) -> list[str]:
    """Pull bullet/numbered items from a summary string."""
    kps = re.findall(r'(?:^|\n)[-*•\d\.]+\s*(.*?)(?=\n|$)', summary)
    kps = [k.strip() for k in kps if len(k.strip()) > 15][:5]
    if not kps:
        kps = [
            "Primary legal matters and procedural history",
            "Key factual findings and evidentiary details",
            "Statutory interpretation and legal precedents cited",
            "Court's reasoning, final ruling, and conclusion",
            "Significance and long-term legal implications",
        ]
    return kps


# ── POST /documents — Unified Ingestion Gate ──────────────────────────────────

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Ingest a document (upload, database retrieve, or ephemeral)",
)
async def ingest_document(
    # Multipart fields (for file uploads)
    file: Optional[UploadFile] = File(None),
    is_confidential: Optional[bool] = Form(None),
    # JSON body fields (for database case retrieval) — injected via dependency
    db: Session = Depends(get_db),
    # Auth is optional — required for persistent sessions, not for ephemeral
    user_id: Optional[str] = Depends(get_current_user),
):
    """
    Unified document ingestion gateway.

    Three ingestion modes are supported, differentiated by the request:

    **Mode A — Persistent File Upload** (`multipart/form-data`, `is_confidential=false`):
    Upload a new PDF. Stored in blob storage and processed asynchronously via Celery.
    Returns `status: pending` — poll `/status` to track progress.

    **Mode B — Ephemeral / Confidential Upload** (`multipart/form-data`, `is_confidential=true`):
    Upload a PDF for a one-off, in-memory analysis. No DB or blob storage is written.
    Returns `status: completed` immediately.

    **Mode C — Database Case Ingestion** (send as JSON body via `/documents/retrieve`):
    Use `POST /api/v1/documents/retrieve` with a JSON body containing `case_id`.
    """
    # ── Mode B & A: file upload ──────────────────────────────────────────────
    if file is not None:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are accepted.",
            )

        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        # ── Mode B: Ephemeral / confidential ────────────────────────────────
        if is_confidential is True:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
            try:
                agent = get_agent()
                text = agent.extract_text_from_pdf(tmp_path)
                if not text.strip():
                    raise ValueError("No text could be extracted from this PDF.")
                agent.create_temp_embeddings(file.filename, text)
                logger.info("Ephemeral PDF processed: %s", file.filename)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            return {
                "document_id": file.filename,
                "document_name": file.filename,
                "status": "completed",
                "is_confidential": True,
                "created_at": None,
            }

        # ── Mode A: Persistent file upload ───────────────────────────────────
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for persistent document uploads.",
            )

        try:
            blob_path = blob_storage_service.upload_pdf(pdf_bytes, user_id)
        except BlobStorageError as exc:
            logger.error("Blob upload failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to store the document. Please try again.",
            )

        doc_session = session_service.create_document_session(
            db=db,
            user_id=user_id,
            document_name=file.filename,
            blob_path=blob_path,
            source_type="uploaded",
        )

        process_document_task.delay(
            session_id=str(doc_session.session_id),
            blob_path=blob_path,
        )

        logger.info(
            "Persistent upload: session=%s file=%s user=%s",
            doc_session.session_id, file.filename, user_id,
        )

        return {
            "document_id": str(doc_session.session_id),
            "document_name": doc_session.document_name,
            "status": doc_session.processing_status,
            "is_confidential": False,
            "created_at": doc_session.created_at.isoformat() if doc_session.created_at else None,
        }

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Request must include a file (multipart/form-data) or use POST /documents/retrieve for database cases.",
    )


@router.post(
    "/retrieve",
    status_code=status.HTTP_201_CREATED,
    summary="Retrieve a database case for persistent analysis",
)
async def retrieve_document(
    request: DocumentIngestJsonRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Create a persistent document session from an existing indexed legal case.

    - **case_id**: Must match a filename in the case database (e.g. from `/cases/search`)
    - Returns `document_id` immediately; Celery processes the document asynchronously.
    """
    document_name = request.case_id

    local_pdf_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "pdfs",
    )
    local_path = os.path.join(local_pdf_dir, document_name)

    if os.path.exists(local_path):
        try:
            blob_path = blob_storage_service.store_local_file(local_path, user_id)
        except Exception as exc:
            logger.error("Failed to register local file: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to prepare the document for processing.",
            )
    else:
        azure_blob_path = f"pdfs/{document_name}"
        if not blob_storage_service.blob_exists(azure_blob_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case '{document_name}' not found in the case database.",
            )
        try:
            pdf_bytes = blob_storage_service.download_pdf(azure_blob_path)
            blob_path = blob_storage_service.upload_pdf(pdf_bytes, user_id)
        except BlobStorageError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve document: {exc}",
            )

    doc_session = session_service.create_document_session(
        db=db,
        user_id=user_id,
        document_name=document_name,
        blob_path=blob_path,
        source_type="retrieved",
    )

    process_document_task.delay(
        session_id=str(doc_session.session_id),
        blob_path=blob_path,
    )

    logger.info(
        "Database retrieve: session=%s file=%s user=%s",
        doc_session.session_id, document_name, user_id,
    )

    return {
        "document_id": str(doc_session.session_id),
        "document_name": doc_session.document_name,
        "status": doc_session.processing_status,
        "is_confidential": False,
        "created_at": doc_session.created_at.isoformat() if doc_session.created_at else None,
    }


# ── GET /documents — List all sessions ───────────────────────────────────────

@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List all document sessions for the current user",
)
async def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Return paginated document sessions, ordered by created_at descending."""
    sessions, total_count = session_service.list_user_sessions(
        db, user_id, page=page, page_size=page_size
    )
    return DocumentListResponse(
        sessions=[_session_to_response(s) for s in sessions],
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


# ── GET /documents/{document_id}/status ──────────────────────────────────────

@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Poll document processing status",
)
async def get_document_status(
    document_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Poll the processing status of a persistent document session.
    Returns one of: `pending`, `processing`, `completed`, `failed`.
    """
    doc_session = session_service.get_document_session(db, str(document_id), user_id)
    return DocumentStatusResponse(
        session_id=doc_session.session_id,
        processing_status=doc_session.processing_status,
        error_message=doc_session.error_message,
        updated_at=doc_session.updated_at or doc_session.created_at,
    )


# ── GET /documents/{document_id}/analysis — Unified Analysis ─────────────────

@router.get(
    "/{document_id}/analysis",
    summary="Retrieve unified document analysis (summary + stats)",
)
def get_document_analysis(
    document_id: str,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_optional_current_user),
):
    """
    Retrieve the full analysis for a document — summary, key points, and statistics.

    Works for both **persistent** (UUID document_id) and **ephemeral** (filename document_id) sessions.
    For persistent sessions the document must have `processing_status == completed`.
    """
    agent = get_agent()

    # ── Try ephemeral / confidential path first ────────────────────────────
    if document_id in agent.temp_document_texts:
        text = agent.temp_document_texts[document_id]
        summary = agent.generate_summary(text)
        key_points = _extract_key_points(summary)
        return {
            "document_id": document_id,
            "analysis": {
                "summary": summary,
                "key_points": key_points,
            },
            "stats": {
                "pages": max(1, len(text) // 3000),
                "words": len(text.split()),
                "chunks": 0,
            },
        }

    # ── Try persistent session (UUID) ──────────────────────────────────────
    try:
        uuid_id = UUID(document_id)
    except ValueError:
        uuid_id = None

    if uuid_id and user_id:
        try:
            doc_session = session_service.get_document_session(db, str(uuid_id), user_id)
        except HTTPException:
            doc_session = None

        if doc_session:
            if doc_session.processing_status != "completed":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Document processing is not complete (status: {doc_session.processing_status}). "
                           "Please wait for processing to finish.",
                )
            if not doc_session.summary:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Summary not yet generated for this document.",
                )
            return {
                "document_id": document_id,
                "analysis": {
                    "summary": doc_session.summary,
                    "key_points": _extract_key_points(doc_session.summary),
                },
                "stats": {
                    "pages": 0,
                    "words": 0,
                    "chunks": 0,
                },
                "processed_at": doc_session.updated_at.isoformat() if doc_session.updated_at else None,
            }

    # ── Fall back: on-demand analysis for database case filename ───────────
    local_pdf_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "pdfs",
    )
    local_path = os.path.join(local_pdf_dir, document_id)
    temp_cleanup = False

    if os.path.exists(local_path):
        pdf_path = local_path
    else:
        azure_blob_path = f"pdfs/{document_id}"
        if not blob_storage_service.blob_exists(azure_blob_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document '{document_id}' not found.",
            )
        try:
            pdf_bytes = blob_storage_service.download_pdf(azure_blob_path)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                pdf_path = tmp.name
            temp_cleanup = True
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download case document.",
            )

    try:
        try:
            analysis_res = agent.analyze_document(pdf_path, document_id)
            if not analysis_res.get("success"):
                raise Exception(analysis_res.get("error", "Analysis pipeline failed."))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        try:
            import fitz
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            idx = pdf_data.find(b"%PDF-")
            if idx > 0:
                pdf_data = pdf_data[idx:]
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            page_count = len(doc)
            word_count = sum(len(page.get_text().split()) for page in doc)
            doc.close()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF metadata: {str(e)}"
            )

        summary = analysis_res["summary"]
        return {
            "document_id": document_id,
            "analysis": {
                "summary": summary,
                "key_points": _extract_key_points(summary),
            },
            "stats": {
                "pages": page_count,
                "words": word_count,
                "chunks": 0,
            },
        }
    finally:
        if temp_cleanup and os.path.exists(pdf_path):
            os.remove(pdf_path)


# ── POST /documents/{document_id}/chat — Q&A Gateway ─────────────────────────

@router.post(
    "/{document_id}/chat",
    summary="Ask a question about a document (persistent or ephemeral)",
)
def document_chat(
    document_id: str,
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_optional_current_user),
):
    """
    Unified Q&A gateway for a document.

    Routes internally to the appropriate pipeline:
    - **Ephemeral** (confidential filename): uses the in-memory FAISS index
    - **Persistent** (UUID session): uses the full RAG pipeline with Postgres chunk storage

    Returns the AI-generated answer with context attribution.
    """
    agent = get_agent()
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # ── Ephemeral path: filename-keyed in-memory embeddings ───────────────
    if document_id in agent.temp_vector_stores:
        answer = agent.answer_question(document_id, question)
        return {
            "message_id": f"ephemeral_msg_{id(question)}",
            "role": "assistant",
            "message": answer,
            "timestamp": None,
        }

    # ── Try to auto-load database PDF into ephemeral memory ───────────────
    # If the document_id looks like a filename (not a UUID), try loading it
    try:
        UUID(document_id)
        is_uuid = True
    except ValueError:
        is_uuid = False

    if not is_uuid:
        # Load PDF into ephemeral memory on-demand
        local_pdf_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data", "pdfs",
        )
        local_path = os.path.join(local_pdf_dir, document_id)
        temp_cleanup = False

        if os.path.exists(local_path):
            pdf_path = local_path
        else:
            azure_blob_path = f"pdfs/{document_id}"
            if not blob_storage_service.blob_exists(azure_blob_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ephemeral embeddings for '{document_id}' not found. Please upload the document again.",
                )
            pdf_bytes = blob_storage_service.download_pdf(azure_blob_path)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                pdf_path = tmp.name
            temp_cleanup = True

        try:
            text = agent.extract_text_from_pdf(pdf_path)
            agent.create_temp_embeddings(document_id, text)
        finally:
            if temp_cleanup and os.path.exists(pdf_path):
                os.remove(pdf_path)

        answer = agent.answer_question(document_id, question)
        return {
            "message_id": f"ephemeral_msg_{id(question)}",
            "role": "assistant",
            "message": answer,
            "timestamp": None,
        }

    # ── Persistent RAG path: full DB + FAISS pipeline ─────────────────────
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for persistent document chat.",
        )

    doc_session = session_service.get_document_session(db, document_id, user_id)
    if doc_session.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Document processing is not complete (status: {doc_session.processing_status}). "
                   "Please wait before asking questions.",
        )

    question_embedding = document_processing_service.generate_embeddings([question])[0]
    similar = vector_store_service.search_similar(question_embedding, k=5)
    embedding_refs = [ref for ref, _ in similar]

    chunks = session_service.get_chunks_by_refs(db, embedding_refs)
    chunk_map = {c.embedding_reference: c.chunk_text for c in chunks}
    retrieved_texts = [chunk_map[ref] for ref in embedding_refs if ref in chunk_map]
    retrieved_chunk_ids = [
        str(c.chunk_id) for ref in embedding_refs
        for c in chunks if str(c.embedding_reference) == ref
    ]

    retrieved_context = "\n\n---\n\n".join(retrieved_texts) if retrieved_texts else "No relevant document sections found."

    chat_session = session_service.get_or_create_chat_session(db, document_id, user_id, question)
    history = session_service.get_chat_history(db, str(chat_session.chat_id), limit=5)
    history_texts = [f"{msg.role.capitalize()}: {msg.message}" for msg in history]

    try:
        answer = agent.answer_with_context(
            context=retrieved_context,
            question=question,
            history=history_texts,
        )
    except Exception as exc:
        logger.exception("LLM call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate an answer. Please try again.",
        )

    session_service.add_chat_message(db=db, chat_id=str(chat_session.chat_id), role="user", message=question)
    assistant_msg = session_service.add_chat_message(
        db=db,
        chat_id=str(chat_session.chat_id),
        role="assistant",
        message=answer,
        retrieved_chunks=retrieved_chunk_ids,
        llm_response=answer,
    )

    return {
        "message_id": str(assistant_msg.message_id),
        "role": "assistant",
        "message": answer,
        "timestamp": assistant_msg.timestamp.isoformat() if assistant_msg.timestamp else None,
    }


# ── GET /documents/{document_id}/chat — Thread History ───────────────────────

@router.get(
    "/{document_id}/chat",
    summary="Get conversation thread history for a document",
)
async def get_chat_history(
    document_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Retrieve the full conversation thread for a persistent document session.
    Messages are returned in chronological order (oldest first).
    """
    session_service.get_document_session(db, str(document_id), user_id)

    chat_session = session_service.get_chat_session(db, str(document_id), user_id)
    if chat_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No conversation found. Ask a question first.",
        )

    messages = session_service.get_chat_history(db, str(chat_session.chat_id))
    return {
        "document_id": str(document_id),
        "chat_id": str(chat_session.chat_id),
        "messages": [
            {
                "message_id": str(m.message_id),
                "role": m.role,
                "message": m.message,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            }
            for m in messages
        ],
    }


# ── GET /documents/{document_id} — Session metadata ──────────────────────────

@router.get(
    "/{document_id}",
    response_model=DocumentSessionResponse,
    summary="Get document session metadata",
)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Retrieve full details for a persistent document session."""
    doc_session = session_service.get_document_session(db, str(document_id), user_id)
    return _session_to_response(doc_session)


# ── DELETE /documents/{document_id} — Purge ──────────────────────────────────

@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete a document session and all associated data",
)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    user_id: Optional[str] = Depends(get_current_user),
):
    """
    Purge a document session.

    For **persistent sessions**: cascade-deletes DB records, embeddings, and blob.
    For **ephemeral sessions** (filename document_id): clears in-memory state only.
    """
    agent = get_agent()

    # ── Ephemeral cleanup ──────────────────────────────────────────────────
    if document_id in agent.temp_vector_stores or document_id in agent.temp_document_texts:
        agent.cleanup_temp_embeddings(document_id)
        logger.info("Cleaned up ephemeral session: %s", document_id)
        return DocumentDeleteResponse(
            message=f"Ephemeral session for '{document_id}' cleared successfully.",
            session_id=document_id,
        )

    # ── Persistent session cleanup ─────────────────────────────────────────
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to delete persistent sessions.",
        )

    try:
        uuid_id = UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found.",
        )

    doc_session = session_service.get_document_session(db, str(uuid_id), user_id)
    blob_path = doc_session.blob_path
    embedding_refs = session_service.get_session_embedding_refs(db, str(uuid_id))

    session_service.delete_document_session(db, str(uuid_id), user_id)

    if embedding_refs:
        removed = vector_store_service.remove_embeddings(embedding_refs)
        logger.info("Removed %d embeddings for session %s", removed, document_id)

    try:
        blob_storage_service.delete_pdf(blob_path)
    except Exception as exc:
        logger.warning("Failed to delete blob '%s': %s", blob_path, exc)

    logger.info("Session %s deleted by user %s", document_id, user_id)
    return DocumentDeleteResponse(
        message="Document session deleted successfully.",
        session_id=uuid_id,
    )


# ── Ephemeral similar-case retrieval (kept explicit per user feedback) ─────────

@router.get(
    "/{document_id}/similar-cases",
    summary="Find similar legal cases using the uploaded document as a query",
)
async def get_similar_cases(
    document_id: str,
    top_k: int = Query(5, ge=1, le=20),
):
    """
    Perform semantic search using the text of an ephemerally uploaded document.

    Requires a prior ephemeral upload (`POST /documents` with `is_confidential=true`).
    The `document_id` is the original filename returned during upload.
    """
    agent = get_agent()
    searcher = get_searcher()

    text = agent.temp_document_texts.get(document_id)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ephemeral session for '{document_id}' not found. Please upload the file again.",
        )

    query_text = text[:4000]
    try:
        results = searcher.search(query_text, top_k=top_k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {exc}")

    similar_cases = [
        {
            "case_id": r["filename"],
            "filename": r["filename"],
            "title": r["filename"].replace(".pdf", "").replace("__", " — ").replace("_", " "),
            "score": r["score"],
            "similarity_percentage": r.get("similarity_percentage", round(r["score"] * 100, 1)),
            "content": _get_pdf_preview(r["filename"]),
        }
        for r in results
    ]

    return {"document_id": document_id, "similar_cases": similar_cases}
