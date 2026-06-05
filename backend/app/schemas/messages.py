"""
Pydantic schemas for Message API endpoints.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CitationModel(BaseModel):
    document_title: str
    page_number: int
    excerpt: str


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: UUID
    role: str
    message_type: str
    content: str
    citations: Optional[List[CitationModel]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
