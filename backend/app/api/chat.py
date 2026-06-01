"""
General legal chatbot route — v1

POST /api/v1/chat/legal  – conversational legal domain Q&A
"""

import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.ai.legal_chatbot import get_legal_chatbot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["v1 · Legal Chat"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class LegalChatRequest(BaseModel):
    question: str


class LegalChatResponse(BaseModel):
    success: bool
    response: str
    is_legal: bool


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post(
    "/legal",
    response_model=LegalChatResponse,
    summary="Ask the general legal domain AI assistant",
)
async def legal_chat(request: LegalChatRequest):
    """
    Interact with the general-purpose legal AI assistant.

    The assistant:
    - Answers questions about law, judicial systems, legal procedures, and precedents
    - Applies a domain guardrail to reject non-legal questions
    - Maintains conversational memory for the last 3 exchanges

    > **Disclaimer**: Responses are for informational purposes only and do not
    > constitute formal legal advice. Consult a qualified attorney for specific guidance.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    try:
        chatbot = get_legal_chatbot()
        result = chatbot.chat(question)
    except Exception as exc:
        logger.exception("Legal chatbot failure: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The legal assistant is temporarily unavailable. Please try again.",
        )

    if not result.get("success") and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"],
        )

    return LegalChatResponse(
        success=result.get("success", True),
        response=result.get("response", ""),
        is_legal=result.get("is_legal", True),
    )
