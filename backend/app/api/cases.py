"""
Case search & retrieval routes — v1

POST /api/v1/cases/search      – semantic search over indexed legal cases
GET  /api/v1/cases/{case_id}   – get case metadata + PDF access URL
GET  /api/v1/health            – system health check
"""

import os
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.services.search_service import get_searcher

logger = logging.getLogger(__name__)

router = APIRouter(tags=["v1 · Cases"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class CaseSearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10


class CaseSearchResult(BaseModel):
    case_id: str          # filename used as stable case identifier
    title: str
    score: float
    similarity_percentage: float


class CaseSearchResponse(BaseModel):
    success: bool
    query: str
    results: list[CaseSearchResult]
    total_results: int


class CaseDetailResponse(BaseModel):
    case_id: str
    title: str
    pdf_url: str


class HealthResponse(BaseModel):
    status: str
    message: str
    total_cases: int


# ── Helpers ───────────────────────────────────────────────────────────────────

def _filename_to_title(filename: str) -> str:
    """Convert raw filename like 'abc__court__2019.pdf' into a readable title."""
    if not filename:
        return "Legal Case Document"
    return (
        filename
        .replace(".pdf", "")
        .replace("__", " — ")
        .replace("_", " ")
        .strip()
    )


def _get_pdf_base_url() -> str:
    """Return the configured base URL for PDF file access."""
    base = os.getenv("VITE_API_BASE_URL", "")
    return base


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse, summary="System health check")
async def health_check():
    """
    Check the health of the legal case search service.

    Returns searcher status and total number of indexed cases.
    """
    try:
        searcher = get_searcher()
        total = searcher.index.ntotal if searcher.index else 0
        return HealthResponse(
            status="healthy",
            message="Legal case search service is running.",
            total_cases=total,
        )
    except Exception as exc:
        logger.warning("Health check degraded: %s", exc)
        return HealthResponse(
            status="degraded",
            message=str(exc),
            total_cases=0,
        )


@router.post(
    "/cases/search",
    response_model=CaseSearchResponse,
    summary="Semantic search over legal cases",
)
async def search_cases(request: CaseSearchRequest):
    """
    Perform semantic search over 46,000+ indexed legal cases.

    - **query**: Natural language query or case description
    - **top_k**: Maximum number of results (1–50, default 10)
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    top_k = max(1, min(request.top_k or 10, 50))

    try:
        searcher = get_searcher()
        raw_results = searcher.search(query_text, top_k=top_k)
    except Exception as exc:
        logger.error("Search failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}")

    results = [
        CaseSearchResult(
            case_id=r["filename"],
            title=_filename_to_title(r["filename"]),
            score=r["score"],
            similarity_percentage=r.get("similarity_percentage", round(r["score"] * 100, 1)),
        )
        for r in raw_results
    ]

    return CaseSearchResponse(
        success=True,
        query=query_text,
        results=results,
        total_results=len(results),
    )


@router.get(
    "/cases/search",
    response_model=CaseSearchResponse,
    summary="Semantic search over legal cases (GET)",
)
async def search_cases_get(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(10, ge=1, le=50, description="Number of results"),
):
    """
    GET variant of case search — same semantics as POST but uses query params.
    Useful for shareable links and browser-level caching.
    """
    query_text = q.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        searcher = get_searcher()
        raw_results = searcher.search(query_text, top_k=top_k)
    except Exception as exc:
        logger.error("Search failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}")

    results = [
        CaseSearchResult(
            case_id=r["filename"],
            title=_filename_to_title(r["filename"]),
            score=r["score"],
            similarity_percentage=r.get("similarity_percentage", round(r["score"] * 100, 1)),
        )
        for r in raw_results
    ]

    return CaseSearchResponse(
        success=True,
        query=query_text,
        results=results,
        total_results=len(results),
    )


@router.get(
    "/cases/{case_id:path}",
    response_model=CaseDetailResponse,
    summary="Get case metadata and PDF access URL",
)
async def get_case(case_id: str):
    """
    Retrieve metadata and the PDF access URL for a specific legal case.

    - **case_id**: The stable case identifier (typically the PDF filename)
    """
    base_url = os.getenv("VITE_API_BASE_URL", "")
    pdf_url = f"{base_url}/api/pdf/{case_id}"

    return CaseDetailResponse(
        case_id=case_id,
        title=_filename_to_title(case_id),
        pdf_url=pdf_url,
    )


@router.get(
    "/pdf/{filename}",
    summary="Serve a legal case PDF",
)
async def serve_pdf(filename: str):
    """
    Serve a PDF file from the data/pdfs directory.
    """
    safe_filename = os.path.basename(filename)
    local_pdf_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "pdfs",
    )
    pdf_path = os.path.join(local_pdf_dir, safe_filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")
    return FileResponse(pdf_path, media_type="application/pdf", filename=safe_filename)

