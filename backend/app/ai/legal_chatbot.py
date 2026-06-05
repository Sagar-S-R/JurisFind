"""
Legal Chatbot Agent using Groq.
Specialized for judicial and legal domain questions.

Note on history: This agent does NOT maintain its own internal chat history.
All conversation state lives in PostgreSQL and is passed in from the API layer
on each request, ensuring consistency across users and requests.
"""
import os
import logging
import re
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

_dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=False)

logger = logging.getLogger(__name__)


class LegalChatbotAgent:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.groq_client = Groq(api_key=api_key)
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        # Legal domain classification prompt (inline — no LangChain template needed)
        self._domain_filter_system = "You are a domain classification assistant."
        self._domain_filter_user = (
            "You are a domain filter for a legal AI assistant. Determine if the "
            "question is related to the judicial system, legal matters, or law.\n\n"
            "Question: {question}\n\n"
            "Respond with ONLY 'LEGAL' or 'NON-LEGAL'."
        )

    # ── Response sanitizer (shared logic with LegalDocumentAgent) ────────────

    @staticmethod
    def clean_ai_response(response: str) -> str:
        """Remove common LLM output artifacts (prompt leakage, excess whitespace)."""
        if not response:
            return response
        cleaned = response.strip()
        cleaned = re.sub(
            r"^(System:|Assistant:|AI:|Response:)\s*",
            "",
            cleaned,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r" {2,}", " ", cleaned)
        return cleaned.strip()

    # ── Domain guardrail ─────────────────────────────────────────────────────

    def is_legal_question(self, question: str) -> bool:
        """Return True if the question falls within the legal domain."""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self._domain_filter_system},
                    {"role": "user", "content": self._domain_filter_user.format(question=question)},
                ],
                temperature=0.1,
                max_tokens=10,
            )
            result = response.choices[0].message.content.strip().upper()
            return result == "LEGAL"
        except Exception as exc:
            logger.warning("Domain filter error (defaulting to LEGAL): %s", exc)
            return True  # Fail open


# ── Module-level singleton ────────────────────────────────────────────────────
_chatbot: LegalChatbotAgent | None = None


def get_legal_chatbot() -> LegalChatbotAgent:
    """Get or lazily create the global chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = LegalChatbotAgent()
    return _chatbot
