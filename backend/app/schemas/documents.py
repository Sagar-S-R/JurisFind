"""
Document session schemas for request/response validation.

This module defines Pydantic schemas for document session management including
session creation, retrieval, listing, and status tracking.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentRetrieveRequest(BaseModel):
    """
    Schema for retrieving a document from the indexed case database.
    
    Validates:
    - Document name is provided and non-empty
    """
    document_name: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Name of the document to retrieve from the case database",
        examples=["case_123.pdf", "legal_document_2024.pdf"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "document_name": "case_123.pdf"
                }
            ]
        }
    }


class DocumentSessionResponse(BaseModel):
    """
    Schema for document session response.
    
    Returns complete information about a document session including:
    - Session identification
    - Document metadata
    - Processing status
    - Summary (if available)
    - Timestamps
    """
    session_id: UUID = Field(
        ...,
        description="Unique session identifier (UUID v4)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    document_name: str = Field(
        ...,
        description="Name of the document",
        examples=["case_123.pdf"]
    )
    source_type: str = Field(
        ...,
        description="Source of the document (uploaded or retrieved)",
        examples=["uploaded", "retrieved"]
    )
    processing_status: str = Field(
        ...,
        description="Current processing status (pending, processing, completed, failed)",
        examples=["completed", "pending", "processing", "failed"]
    )
    summary: Optional[str] = Field(
        None,
        description="Document summary (available after processing completes)",
        examples=["This legal case involves a dispute between..."]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the session was created",
        examples=["2024-01-15T10:30:00Z"]
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the session was last updated",
        examples=["2024-01-15T10:32:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "document_name": "case_123.pdf",
                    "source_type": "uploaded",
                    "processing_status": "completed",
                    "summary": "This legal case involves a dispute between two parties regarding contract enforcement.",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:32:00Z"
                }
            ]
        }
    }


class DocumentListResponse(BaseModel):
    """
    Schema for paginated list of document sessions.
    
    Returns:
    - List of document sessions
    - Pagination metadata (total count, page, page size)
    """
    sessions: List[DocumentSessionResponse] = Field(
        ...,
        description="List of document sessions for the current page"
    )
    total_count: int = Field(
        ...,
        ge=0,
        description="Total number of sessions across all pages",
        examples=[45]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of sessions per page",
        examples=[20]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sessions": [
                        {
                            "session_id": "550e8400-e29b-41d4-a716-446655440000",
                            "document_name": "case_123.pdf",
                            "source_type": "uploaded",
                            "processing_status": "completed",
                            "summary": "This legal case involves...",
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:32:00Z"
                        }
                    ],
                    "total_count": 45,
                    "page": 1,
                    "page_size": 20
                }
            ]
        }
    }


class DocumentStatusResponse(BaseModel):
    """
    Schema for document processing status response.
    
    Returns:
    - Session ID
    - Current processing status
    - Error message (if failed)
    - Last update timestamp
    """
    session_id: UUID = Field(
        ...,
        description="Unique session identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    processing_status: str = Field(
        ...,
        description="Current processing status",
        examples=["completed", "pending", "processing", "failed"]
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if processing failed",
        examples=["PDF extraction failed: corrupted file"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of last status update",
        examples=["2024-01-15T10:32:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "processing_status": "completed",
                    "error_message": None,
                    "updated_at": "2024-01-15T10:32:00Z"
                },
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440001",
                    "processing_status": "failed",
                    "error_message": "PDF extraction failed: corrupted file",
                    "updated_at": "2024-01-15T10:32:00Z"
                }
            ]
        }
    }


class DocumentSummaryResponse(BaseModel):
    """
    Schema for document summary response.
    
    Returns:
    - Session ID
    - Document summary
    - Generation timestamp
    """
    session_id: UUID = Field(
        ...,
        description="Unique session identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    summary: str = Field(
        ...,
        description="Generated document summary",
        examples=["This legal case involves a dispute between two parties regarding contract enforcement."]
    )
    generated_at: datetime = Field(
        ...,
        description="Timestamp when the summary was generated",
        examples=["2024-01-15T10:32:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "summary": "This legal case involves a dispute between two parties regarding contract enforcement.",
                    "generated_at": "2024-01-15T10:32:00Z"
                }
            ]
        }
    }


class DocumentUploadResponse(BaseModel):
    """
    Schema for document upload response.
    
    Returns:
    - Session ID
    - Document name
    - Processing status (initially 'pending')
    - Creation timestamp
    """
    session_id: UUID = Field(
        ...,
        description="Unique session identifier for the uploaded document",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    document_name: str = Field(
        ...,
        description="Name of the uploaded document",
        examples=["case_123.pdf"]
    )
    processing_status: str = Field(
        default="pending",
        description="Initial processing status",
        examples=["pending"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the session was created",
        examples=["2024-01-15T10:30:00Z"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "550e8400-e29b-41d4-a716-446655440000",
                    "document_name": "case_123.pdf",
                    "processing_status": "pending",
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }


class DocumentDeleteResponse(BaseModel):
    """
    Schema for document deletion response.
    
    Returns:
    - Success message
    - Deleted session ID
    """
    message: str = Field(
        ...,
        description="Success message",
        examples=["Document session deleted successfully"]
    )
    session_id: UUID = Field(
        ...,
        description="ID of the deleted session",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Document session deleted successfully",
                    "session_id": "550e8400-e29b-41d4-a716-446655440000"
                }
            ]
        }
    }
