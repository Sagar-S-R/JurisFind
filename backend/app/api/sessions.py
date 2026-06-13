"""
Sessions API Router — JurisFind V2.

Handles AssistantSessions, their Messages (including SSE streaming for AI responses),
and attaching/detaching Documents.
"""
import json
import logging
import uuid
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from app.api.dependencies.auth import get_current_user
from app.db.session import DatabaseSession, get_db
from app.db.crud import session_repository as session_repo
from app.db.crud import message_repository as message_repo
from app.db.crud import document_repository as doc_repo
from app.db.crud import session_document_repository as sd_repo
from app.agents import juris_graph, JurisFindState
from app.schemas.sessions import (
    SessionCreate,
    SessionListItem,
    SessionRenameRequest,
    SessionResponse,
)
from app.schemas.messages import MessageCreate, MessageResponse
from app.schemas.documents import AttachDocumentRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["v2 · Sessions"])


# ── Session CRUD ──────────────────────────────────────────────────────────────

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: SessionCreate,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.create_session(db, uuid.UUID(user_id), request.title)
    return session


@router.get("", response_model=List[SessionListItem])
async def list_sessions(
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return session_repo.list_sessions(db, uuid.UUID(user_id))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def rename_session(
    session_id: UUID,
    request: SessionRenameRequest,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_repo.rename_session(db, session, request.title)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session_repo.delete_session(db, session)


# ── Session Documents ─────────────────────────────────────────────────────────

@router.post("/{session_id}/documents", status_code=status.HTTP_201_CREATED)
async def attach_document(
    session_id: UUID,
    request: AttachDocumentRequest,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    doc = doc_repo.get_document(db, request.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    sd_repo.attach_document(db, session.id, doc.id)
    return {"status": "attached"}


@router.delete("/{session_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_document(
    session_id: UUID,
    document_id: UUID,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not sd_repo.detach_document(db, session.id, document_id):
        raise HTTPException(status_code=404, detail="Document not attached to session")


# ── Messages & Streaming Chat ─────────────────────────────────────────────────

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return message_repo.list_messages(db, session.id)


@router.post("/{session_id}/messages")
async def send_message(
    session_id: UUID,
    request: MessageCreate,
    db: DBSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Send a message and receive an SSE-streamed AI response via LangGraph.

    The graph classifies the intent, routes to the correct retrieval path,
    and returns the answer. Citations (if any) are emitted as a separate
    SSE event after [DONE].
    """
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = request.content.strip()

    # ── Persist user message ──────────────────────────────────────────────────
    message_repo.append_message(db, session.id, "user", question)

    # Auto-title on first message
    if session.title == "New Session":
        new_title = (question[:40] + "...") if len(question) > 40 else question
        session_repo.rename_session(db, session, new_title)
    else:
        session_repo.touch_session(db, session)

    # ── Build initial graph state ─────────────────────────────────────────────
    recent_msgs = message_repo.get_recent_messages(db, session.id, n=6)
    history = [{"role": m.role, "content": m.content} for m in recent_msgs]

    doc_ids = [str(doc_id) for doc_id in sd_repo.get_attached_document_ids(db, session.id)]

    explicit_mode = getattr(request, "explicit_mode", None) or "auto"

    initial_state: JurisFindState = {
        "session_id":       str(session.id),
        "user_id":          str(user_id),
        "question":         question,
        "history":          history,
        "explicit_mode":    explicit_mode,
        "document_ids":     doc_ids,
        "is_legal":         False,
        "intent":           "",
        "retrieved_chunks": [],
        "citations":        [],
        "answer":           "",
        "error":            None,
    }

    # ── Run graph and stream result ───────────────────────────────────────────
    # Nodes use the raw Groq SDK (stream=False), not LangChain ChatGroq.
    # astream_events does NOT emit on_chat_model_stream in this setup.
    # ainvoke runs the full graph and returns the final state, then we emit
    # the complete answer as a single SSE chunk.
    async def generate():
        final_answer    = ""
        final_citations = []

        try:
            final_state     = await juris_graph.ainvoke(initial_state)
            final_answer    = final_state.get("answer", "")
            final_citations = final_state.get("citations", [])

            if final_answer:
                yield f"data: {json.dumps({'content': final_answer})}\n\n"
            else:
                yield f"data: {json.dumps({'content': 'No response was generated. Please try again.'})}\n\n"

        except Exception as exc:
            logger.error("Graph error: %s", exc)
            yield f"data: {json.dumps({'content': '[Server busy. Please try again in a moment.]'})}\n\n"

        # Signal stream complete
        yield "data: [DONE]\n\n"

        # Emit citations as a separate SSE event if present
        if final_citations:
            yield f"event: citations\ndata: {json.dumps(final_citations)}\n\n"

        # ── Persist assistant reply to DB ─────────────────────────────────────
        if final_answer:
            with DatabaseSession() as write_db:
                message_repo.append_message(
                    write_db,
                    session.id,
                    "assistant",
                    final_answer,
                    citations=final_citations or None,
                )

    return StreamingResponse(generate(), media_type="text/event-stream")
