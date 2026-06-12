# API Reference

All endpoints are prefixed with `/api`. Authentication is required for most endpoints using JWT Bearer tokens.

## Authentication
- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Authenticate and receive a JWT token.
- `GET /auth/me`: Retrieve current user profile.

## Sessions & Chat
- `POST /sessions`: Create a new chat session.
- `GET /sessions`: List all sessions for the current user.
- `GET /sessions/{id}`: Retrieve a specific session.
- `DELETE /sessions/{id}`: Delete a session and its associated messages.
- `GET /sessions/{id}/messages`: Retrieve chat history for a session.
- `POST /sessions/{id}/messages`: Send a message to the AI. Returns an SSE (Server-Sent Events) stream containing the AI's response.
- `POST /sessions/{id}/documents`: Attach an uploaded document to a session for RAG context.
- `DELETE /sessions/{session_id}/documents/{document_id}`: Detach a document from a session.

## Documents
- `POST /documents`: Upload a PDF document. Enqueues a Celery task for processing.
- `GET /documents`: List user's uploaded documents.
- `GET /documents/{id}/status`: Poll the processing status of a document (`uploaded`, `processing`, `ready`, `failed`).
- `DELETE /documents/{id}`: Delete a document and its associated vectors.

## Search
- `POST /cases/search`: Semantic search across the main legal corpus.
- `POST /cases/{case_id}/analyze`: Helper endpoint that creates a session, attaches a specific legal case document to it, and initiates background processing. Returns the `session_id`.