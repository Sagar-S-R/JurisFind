"""
Node 1 — IntentClassifier

Single LLM call that simultaneously:
  1. Guards against non-legal questions (guardrail)
  2. Classifies intent: "general" | "document_chat" | "corpus_search"

If explicit_mode is "document" or "corpus", the LLM call is skipped entirely
and the intent is set directly from the user's UI toggle — zero extra latency.
"""
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app.agents.state import JurisFindState

# Load .env from backend/
_dotenv_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=False)

logger = logging.getLogger(__name__)

_CLASSIFIER_SYSTEM_PROMPT = """\
You are a legal AI classifier for an Indian Supreme Court case search system.
Analyse the user question and return a JSON object — nothing else.

Rules for intent:
- "general":        pure legal knowledge, no document search needed.
                    Example: "What is Article 21?" / "What is habeas corpus?"
- "document_chat":  question is about a specific attached document.
                    Only use this if has_documents=true AND the question
                    is clearly about the content of that document.
                    Example: "Summarise this case" / "What did the court hold in this PDF?"
- "corpus_search":  needs searching across multiple Supreme Court cases.
                    Example: "How has SC ruled on right to privacy?"
                             "Find cases about land acquisition after 2010"

is_legal must be false for: cooking, sports, weather, math, coding,
or anything unrelated to law, legal procedures, courts, or legal concepts.\
"""

_CLASSIFIER_USER_TEMPLATE = """\
Question: {question}
Attached documents: {has_documents}

Return JSON:
{{
  "is_legal": true or false,
  "intent": "general" | "document_chat" | "corpus_search",
  "reasoning": "one line explanation"
}}\
"""


def _get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    return Groq(api_key=api_key)


def classifier_node(state: JurisFindState) -> JurisFindState:
    """
    Classify the user's intent.

    Respects explicit_mode override from the frontend toggle — if set to
    "document" or "corpus", no LLM call is made.
    """
    explicit_mode = (state.get("explicit_mode") or "auto").lower()
    question = state["question"]
    has_documents = bool(state.get("document_ids"))

    # ── Fast path: UI toggle override ─────────────────────────────────────────
    if explicit_mode == "document":
        logger.debug("Classifier skipped — explicit_mode=document")
        return {**state, "is_legal": True, "intent": "document_chat"}

    if explicit_mode == "corpus":
        logger.debug("Classifier skipped — explicit_mode=corpus")
        return {**state, "is_legal": True, "intent": "corpus_search"}

    # ── LLM classification (auto mode) ────────────────────────────────────────
    try:
        client = _get_groq_client()
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _CLASSIFIER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _CLASSIFIER_USER_TEMPLATE.format(
                        question=question,
                        has_documents=str(has_documents).lower(),
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,  # deterministic classification
            max_tokens=100,   # short JSON output only
        )

        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)

        is_legal = bool(parsed.get("is_legal", True))
        intent   = str(parsed.get("intent", "general"))
        reasoning = parsed.get("reasoning", "")

        # Sanitise intent to known values
        if intent not in {"general", "document_chat", "corpus_search"}:
            intent = "general"

        # If document_chat but no docs attached, fall back to corpus_search
        if intent == "document_chat" and not has_documents:
            intent = "corpus_search"

        logger.info(
            "Classifier → is_legal=%s intent=%s reason=%r",
            is_legal, intent, reasoning,
        )
        return {**state, "is_legal": is_legal, "intent": intent}

    except Exception as exc:
        logger.error("Classifier error: %s", exc)
        # On failure, default to general legal answer (safe fallback)
        return {**state, "is_legal": True, "intent": "general",
                "error": f"Classifier failed: {exc}"}


def route_after_classifier(state: JurisFindState) -> str:
    """
    Conditional edge function called by LangGraph after classifier_node.

    Returns the name of the next node to execute.
    """
    if not state.get("is_legal", True):
        return "blocked"
    return state.get("intent", "general")  # "general" | "document_chat" | "corpus_search"
