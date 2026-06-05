"""
Sessions API Router — JurisFind V2.

Handles AssistantSessions, their Messages (including SSE streaming for AI responses),
and attaching/detaching Documents.
"""
import json
import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.db.crud import session_repository as session_repo
from app.db.crud import message_repository as message_repo
from app.db.crud import document_repository as doc_repo
from app.db.crud import session_document_repository as sd_repo
from app.services.retrieval_service import retrieve_for_session, build_context_prompt
from app.ai.legal_agent import get_agent
from app.ai.legal_chatbot import get_legal_chatbot
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
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.create_session(db, uuid.UUID(user_id), request.title)
    return session


@router.get("", response_model=List[SessionListItem])
async def list_sessions(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    return session_repo.list_sessions(db, uuid.UUID(user_id))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def rename_session(
    session_id: UUID,
    request: SessionRenameRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_repo.rename_session(db, session, request.title)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session_repo.delete_session(db, session)


# ── Session Documents ─────────────────────────────────────────────────────────

@router.post("/{session_id}/documents", status_code=status.HTTP_201_CREATED)
async def attach_document(
    session_id: UUID,
    request: AttachDocumentRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
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
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not sd_repo.detach_document(db, session.id, document_id):
        raise HTTPException(status_code=404, detail="Document not attached to session")


# ── Messages & Streaming Chat ─────────────────────────────────────────────────

@router.get("/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    session_id: UUID,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return message_repo.list_messages(db, session.id)


@router.post("/{session_id}/messages")
async def send_message(
    session_id: UUID,
    request: MessageCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """
    Send a message and get an SSE streaming response from the AI.
    
    If the session has documents attached, it uses the RAG LegalAgent.
    If the session has NO documents, it uses the general LegalChatbot.
    """
    import uuid
    session = session_repo.get_session_for_user(db, session_id, uuid.UUID(user_id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    question = request.content.strip()

    # 1. Save user message
    message_repo.append_message(db, session.id, "user", question)
    
    # Auto-rename if it's the first message and title is default
    if session.title == "New Session":
        new_title = (question[:40] + "...") if len(question) > 40 else question
        session_repo.rename_session(db, session, new_title)
    else:
        session_repo.touch_session(db, session)

    # 2. Check if we have documents attached
    attached_docs = sd_repo.get_session_documents(db, session.id)
    
    # Get recent conversation history (last 3 pairs = 6 messages) for context
    recent_msgs = message_repo.get_recent_messages(db, session.id, n=6)
    history = [{"role": msg.role, "content": msg.content} for msg in recent_msgs]

    if attached_docs:
        # RAG Path
        logger.info("Session %s has documents. Using RAG Agent.", session.id)
        
        # Retrieve chunks
        chunks = retrieve_for_session(db, session.id, question)
        context = build_context_prompt(chunks)
        citations = [chunk.as_citation() for chunk in chunks] if chunks else []
        
        def generate():
            agent = get_agent()
            
            # Send prompt to Groq with streaming enabled
            system_prompt = (
                "You are a senior legal assistant. Answer the user's question using "
                "ONLY the source blocks provided below. Each source block is marked with "
                "the Document Title and Page number. Cite your sources inline as "
                "[Document Title, Page X]. If the answer cannot be found in the sources, "
                "say: 'I cannot find this information in the attached documents.'"
            )

            user_prompt = f"Context from attached documents:\n\n{context}\n\nQuestion: {question}\n\nAnswer:"
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": user_prompt})

            full_response = ""
            try:
                stream = agent.groq.chat.completions.create(
                    model=agent.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=1500,
                    stream=True,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                        
            except Exception as e:
                logger.error("Streaming error: %s", e)
                # Avoid leaking raw API errors (like Rate Limits) to the user
                yield f"data: {json.dumps({'content': '[Server busy. Please try again in a moment.]'})}\n\n"
            
            # Signal text stream complete FIRST — citations appear after the answer
            yield "data: [DONE]\n\n"
            if citations:
                yield f"event: citations\ndata: {json.dumps(citations)}\n\n"
            
            # Save assistant message to DB after stream completes
            # Note: Need a fresh session here since we're in a generator yielding to FastAPI
            if full_response:
                from app.db.session import DatabaseSession
                with DatabaseSession() as write_db:
                    cleaned = agent.clean_ai_response(full_response)
                    message_repo.append_message(write_db, session.id, "assistant", cleaned, citations=citations)

    else:
        # General Chatbot Path
        logger.info("Session %s has NO documents. Using General Chatbot.", session.id)
        
        def generate():
            chatbot = get_legal_chatbot()
            
            # Check domain first
            if not chatbot.is_legal_question(question):
                content = "I'm a specialized legal AI assistant focused on judicial and legal matters. Please ask questions related to law, legal procedures, court systems, or legal concepts."
                yield f"data: {json.dumps({'content': content})}\n\n"
                yield "data: [DONE]\n\n"
                
                from app.db.session import DatabaseSession
                with DatabaseSession() as write_db:
                    message_repo.append_message(write_db, session.id, "assistant", content)
                return

            system_prompt = (
                "You are an expert legal AI assistant specialising in the Indian judicial "
                "system and legal matters. Provide accurate, professional information about "
                "laws, legal processes, court systems, and legal concepts. Always note that "
                "your answers are for informational purposes only and do not constitute "
                "formal legal advice."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": question})

            full_response = ""
            try:
                stream = chatbot.groq_client.chat.completions.create(
                    model=chatbot.model_name,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=1024,
                    stream=True,
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
                        
            except Exception as e:
                logger.error("Streaming error: %s", e)
                # Avoid leaking raw API errors (like Rate Limits) to the user
                yield f"data: {json.dumps({'content': '[Server busy. Please try again in a moment.]'})}\n\n"
                
            yield "data: [DONE]\n\n"
            
            if full_response:
                from app.db.session import DatabaseSession
                with DatabaseSession() as write_db:
                    cleaned = chatbot.clean_ai_response(full_response)
                    message_repo.append_message(write_db, session.id, "assistant", cleaned)

    return StreamingResponse(generate(), media_type="text/event-stream")
