# Technical Documentation

This document covers the internal technical details of JurisFind.

## Database & Models

JurisFind uses PostgreSQL 17 with the `pgvector` extension. SQLAlchemy is used as the ORM.

**Core Entities:**
- `User`: Handles authentication and ownership.
- `AssistantSession`: Represents a chat thread. Belongs to a user.
- `Message`: Individual chat bubbles within a session.
- `Document`: Represents an uploaded PDF or a selected case from the corpus. Contains metadata and status (`uploaded`, `processing`, `ready`, `failed`).
- `DocumentChunk`: Text chunks extracted from a `Document`. Includes a `pgvector` column for the 768-dimensional text embedding.
- `session_documents`: A many-to-many relationship linking a chat session to specific documents for contextual RAG.

## Document Processing Pipeline

Document processing is completely decoupled from the web API to prevent blocking.

1. **Upload**: A file is uploaded via FastAPI and saved to local storage. A `Document` record is created.
2. **Celery Task**: A background task (`process_document_task`) is queued in RabbitMQ.
3. **Extraction**: The worker uses PyMuPDF (`fitz`) to extract raw text from the PDF.
4. **Chunking**: `RecursiveCharacterTextSplitter` from LangChain splits the text into chunks of 1000 characters with a 200-character overlap.
5. **Embedding**: `all-mpnet-base-v2` (running via HuggingFace SentenceTransformers) converts each chunk into a 768-dimension vector.
6. **Storage**: The chunks and their vectors are saved to the `document_chunks` table using `pgvector`.
7. **Completion**: The document status is set to `ready`. The frontend polls for this state.

## Retrieval-Augmented Generation (RAG)

When a user asks a question in a session with attached documents, the RAG pipeline is triggered:

1. **Query Embedding**: The user's question is embedded using the same `all-mpnet-base-v2` model.
2. **Vector Search**: PostgreSQL executes an L2 distance (`<->`) search against `document_chunks`, filtered to only include chunks belonging to the session's attached documents.
3. **Context Assembly**: The top chunks are formatted into a system prompt, labeled with their source document name and page number.
4. **LLM Inference**: The prompt, history, and context are sent to the Groq API (using `llama-3.3-70b-versatile`).
5. **Streaming (SSE)**: The response streams back chunk-by-chunk via Server-Sent Events. Once the text completes, the backend emits a final `citations` event containing the exact metadata of the retrieved chunks.

## Frontend Polling & State

The frontend React application uses a polling mechanism for background tasks. When a document is attached, the UI checks its status every 3 seconds. Once it turns `ready`, the chat interface is fully unlocked for contextual Q&A. The UI is optimistic, rendering actions (like deleting a session or creating a new chat) immediately while synchronizing with the backend in the background.
