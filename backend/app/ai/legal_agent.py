"""
Legal Document Agent — JurisFind.

Thin Groq wrapper for legal document AI operations (RAG Q&A and summarization).
All retrieval (embedding, vector search) is handled by EmbeddingService and RetrievalService.
"""


import os
import re
from pathlib import Path
from typing import List, Optional

from groq import Groq
from dotenv import load_dotenv

# Load env from backend/.env
_dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_dotenv_path, override=False)


class LegalDocumentAgent:
    """
    Thin Groq wrapper for legal document AI operations.

    This class is intentionally minimal in V2. All retrieval (embedding,
    FAISS, vector search) happens in EmbeddingService and RetrievalService.
    This class only handles the LLM calls.
    """

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "").strip().strip('"').strip("'")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment.")

        self.groq = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── Response sanitizer ────────────────────────────────────────────────────

    @staticmethod
    def clean_ai_response(response: str) -> str:
        """Remove common LLM output artifacts (leakage, excess whitespace)."""
        if not response:
            return response

        cleaned = response.strip()
        # Remove system prompt leakage
        cleaned = re.sub(
            r"^(System:|Assistant:|AI:|Response:)\s*",
            "",
            cleaned,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        # Collapse excessive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        # Collapse multiple spaces
        cleaned = re.sub(r" {2,}", " ", cleaned)
        return cleaned.strip()

    # ── Summary generation ────────────────────────────────────────────────────

    def generate_summary(self, text: str) -> str:
        """
        Generate a structured legal document summary.

        Args:
            text: Full document text (will be truncated to ~8000 chars).

        Returns:
            Structured summary string.
        """
        truncated = text[:8000] if len(text) > 8000 else text

        prompt = f"""You are a legal expert AI assistant. Provide a comprehensive summary of the following legal document.

Document Content:
{truncated}

Please structure your summary as follows:
1. **Document Type & Overview**
2. **Key Parties** (if applicable)
3. **Main Legal Issues**
4. **Key Facts**
5. **Legal Principles & Precedents**
6. **Conclusion / Outcome**
7. **Significance**

Be concise, professional, and use appropriate legal terminology."""

        response = self.groq.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a legal expert AI assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=2048,
        )
        return self.clean_ai_response(response.choices[0].message.content)

    # ── RAG Q&A ───────────────────────────────────────────────────────────────

    def answer_with_context(
        self,
        context: str,
        question: str,
        history: Optional[List[dict]] = None,
    ) -> str:
        """
        Answer a question using only the provided retrieved context.

        Args:
            context:  Pre-formatted source blocks from RetrievalService.
            question: The user's question.
            history:  Optional list of recent {"role", "content"} dicts.

        Returns:
            Answer string grounded in the provided context.
        """
        system_prompt = (
            "You are a senior legal assistant. Answer the user's question using "
            "ONLY the source blocks provided below. Each source block is marked with "
            "the Document Title and Page number. Cite your sources inline as "
            "[Document Title, Page X]. If the answer cannot be found in the sources, "
            "say: 'I cannot find this information in the attached documents.'"
        )

        user_prompt = f"""Context from attached documents:

{context}

Question: {question}

Answer:"""

        messages = [{"role": "system", "content": system_prompt}]

        # Include recent conversation turns for follow-up context
        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_prompt})

        response = self.groq.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=1500,
        )
        return self.clean_ai_response(response.choices[0].message.content)

    # ── General legal Q&A (no document context) ───────────────────────────────

    def answer_general(
        self,
        question: str,
        history: Optional[List[dict]] = None,
    ) -> str:
        """
        Answer a general legal question with no document context.

        Used when the session has no attached documents.
        """
        system_prompt = (
            "You are an expert legal AI assistant specialising in the Indian judicial "
            "system and legal matters. Provide accurate, professional information about "
            "laws, legal processes, court systems, and legal concepts. Always note that "
            "your answers are for informational purposes only and do not constitute "
            "formal legal advice."
        )

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": question})

        response = self.groq.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return self.clean_ai_response(response.choices[0].message.content)


# ── Module-level singleton ────────────────────────────────────────────────────
_agent: Optional[LegalDocumentAgent] = None


def get_agent() -> LegalDocumentAgent:
    """Get or lazily create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = LegalDocumentAgent()
    return _agent
