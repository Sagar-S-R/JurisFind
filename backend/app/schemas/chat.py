"""
Chat schemas for request/response validation.

This module defines Pydantic schemas for chat endpoints including
question answering and conversation history retrieval.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """
    Schema for asking a question on a document session.

    Validates:
    - Question is provided and within max length
    """
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The question to ask about the document",
        examples=["What are the main legal issues in this case?"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "What are the main legal issues in this case?"
                }
            ]
        }
    }


class ChatMessageResponse(BaseModel):
    """
    Schema for a single chat message response.

    Returns:
    - message_id: Unique message identifier
    - role: 'user' or 'assistant'
    - message: Message content
    - retrieved_chunks: List of chunk IDs used to generate the response
    - timestamp: Message timestamp
    """
    message_id: UUID = Field(
        ...,
        description="Unique message identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    role: str = Field(
        ...,
        description="Message role (user or assistant)",
        examples=["user", "assistant"]
    )
    message: str = Field(
        ...,
        description="Message content",
        examples=["What are the main legal issues in this case?"]
    )
    retrieved_chunks: Optional[List[str]] = Field(
        None,
        description="List of chunk IDs used to generate assistant response",
        examples=[["chunk-id-1", "chunk-id-2"]]
    )
    timestamp: datetime = Field(
        ...,
        description="Message timestamp",
        examples=["2024-01-15T10:30:00Z"]
    )

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """
    Schema for chat session history response.

    Returns:
    - chat_id: Unique chat session identifier
    - session_id: Associated document session ID
    - title: Chat session title
    - messages: Ordered list of chat messages
    """
    chat_id: UUID = Field(
        ...,
        description="Unique chat session identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    session_id: UUID = Field(
        ...,
        description="Associated document session ID",
        examples=["550e8400-e29b-41d4-a716-446655440001"]
    )
    title: str = Field(
        ...,
        description="Chat session title (generated from first message)",
        examples=["What are the main legal issues..."]
    )
    messages: List[ChatMessageResponse] = Field(
        ...,
        description="List of chat messages ordered by timestamp"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                    "session_id": "550e8400-e29b-41d4-a716-446655440001",
                    "title": "What are the main legal issues...",
                    "messages": [
                        {
                            "message_id": "msg-001",
                            "role": "user",
                            "message": "What are the main legal issues in this case?",
                            "retrieved_chunks": None,
                            "timestamp": "2024-01-15T10:30:00Z"
                        },
                        {
                            "message_id": "msg-002",
                            "role": "assistant",
                            "message": "The main legal issues in this case involve...",
                            "retrieved_chunks": ["chunk-id-1", "chunk-id-2"],
                            "timestamp": "2024-01-15T10:30:05Z"
                        }
                    ]
                }
            ]
        }
    }


class AskResponse(BaseModel):
    """
    Schema for the Q&A endpoint response.

    Returns:
    - answer: LLM-generated answer
    - chat_id: The chat session ID (created or reused)
    - retrieved_chunks: Chunk IDs used for context
    - message_id: ID of the stored assistant message
    """
    answer: str = Field(
        ...,
        description="LLM-generated answer based on document context",
        examples=["Based on the document, the main legal issue involves..."]
    )
    chat_id: UUID = Field(
        ...,
        description="Chat session ID (created on first question, reused thereafter)",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    retrieved_chunks: List[str] = Field(
        default_factory=list,
        description="List of chunk IDs used as context for the answer",
        examples=[["chunk-id-1", "chunk-id-2"]]
    )
    message_id: UUID = Field(
        ...,
        description="ID of the stored assistant message",
        examples=["550e8400-e29b-41d4-a716-446655440002"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "Based on the document, the main legal issue involves a breach of contract claim...",
                    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                    "retrieved_chunks": ["chunk-id-1", "chunk-id-2"],
                    "message_id": "550e8400-e29b-41d4-a716-446655440002"
                }
            ]
        }
    }
