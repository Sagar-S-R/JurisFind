"""
JurisFind — Search Schemas
==========================
Pydantic request/response models for the Qdrant-backed corpus search layer.
These schemas are entirely separate from the user-upload document schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ── Request ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    """Payload for POST /api/search."""

    query: str = Field(..., min_length=1, max_length=2000, description="Natural language legal query")
    court: Optional[str] = Field(None, description="Filter by court name, e.g. 'Supreme Court'")
    year_min: Optional[int] = Field(None, ge=1950, le=2030, description="Earliest judgment year (inclusive)")
    year_max: Optional[int] = Field(None, ge=1950, le=2030, description="Latest judgment year (inclusive)")
    state: Optional[str] = Field(None, description="Filter by state, e.g. 'Maharashtra'")
    case_type: Optional[str] = Field(None, description="Filter by case type, e.g. 'Writ Petition', 'Criminal Appeal'")
    section_type: Optional[str] = Field(
        None,
        description="Restrict chunks to a legal section: 'held', 'facts', 'judgment', 'headnote', 'issues', 'order', etc."
    )
    top_k: int = Field(10, ge=1, le=50, description="Number of unique cases to return")

    model_config = {"json_schema_extra": {
        "example": {
            "query": "right to privacy as a fundamental right",
            "court": "Supreme Court",
            "year_min": 2000,
            "top_k": 5,
        }
    }}


class AskRequest(BaseModel):
    """Payload for POST /api/search/ask — RAG context fetch."""

    question: str = Field(..., min_length=1, max_length=2000)
    document_id: str = Field(..., description="UUID of a legal_documents row")
    top_k: int = Field(5, ge=1, le=20, description="Number of relevant chunks to return")


# ── Result atoms ───────────────────────────────────────────────────────────────

class ChunkResult(BaseModel):
    """A single text chunk returned from Qdrant."""

    chunk_id: str
    chunk_text: str
    chunk_index: int
    section_type: str
    score: float


class CaseResult(BaseModel):
    """
    A single case (document-level) result.

    Qdrant returns chunk-level hits; these are grouped by document_id.
    'score' is the *maximum* chunk score for the document.
    'top_chunk' is the single highest-scoring chunk.
    'all_chunks' contains every chunk from this document that appeared in the
    raw Qdrant results.
    """

    document_id: str
    title: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None
    citation: Optional[str] = None
    judges: List[str] = Field(default_factory=list)
    case_type: Optional[str] = None
    state: Optional[str] = None
    score: float
    top_chunk: ChunkResult
    all_chunks: List[ChunkResult] = Field(default_factory=list)


# ── Top-level responses ────────────────────────────────────────────────────────

class SearchResponse(BaseModel):
    """Response for POST /api/search."""

    query: str
    total_results: int
    results: List[CaseResult]
    search_time_ms: float


class CaseDetailResponse(BaseModel):
    """Full case detail — GET /api/search/case/{document_id}."""

    document_id: str
    title: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    court: Optional[str] = None
    state: Optional[str] = None
    year: Optional[int] = None
    citation: Optional[str] = None
    judges: List[str] = Field(default_factory=list)
    case_type: Optional[str] = None
    page_count: Optional[int] = None
    chunk_strategy: Optional[str] = None
    chunks: List[ChunkResult] = Field(default_factory=list)


class SimilarCasesResponse(BaseModel):
    """Response for GET /api/search/similar/{document_id}."""

    source_document_id: str
    total_results: int
    results: List[CaseResult]


class AskResponse(BaseModel):
    """Response for POST /api/search/ask — RAG context chunks."""

    document_id: str
    question: str
    context_chunks: List[ChunkResult]
    total_chunks: int
