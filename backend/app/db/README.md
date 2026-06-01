# JurisFind Database Module

This module provides SQLAlchemy models, database configuration, and session management for the JurisFind persistent document sessions feature.

## Structure

```
database/
├── __init__.py          # Package exports
├── models.py            # SQLAlchemy ORM models
├── config.py            # Database configuration and connection pooling
├── session.py           # Session management and dependency injection
└── README.md            # This file
```

## Models

### User
- **Table**: `users`
- **Purpose**: User authentication and session ownership
- **Key Fields**: id (UUID), email (unique), hashed_password, role
- **Relationships**: Has many DocumentSessions and ChatSessions

### DocumentSession
- **Table**: `document_sessions`
- **Purpose**: Track document lifecycle and processing state
- **Key Fields**: session_id (UUID), user_id (FK), source_type, document_name, blob_path, summary, processing_status
- **Relationships**: Belongs to User, has many DocumentChunks and ChatSessions

### DocumentChunk
- **Table**: `document_chunks`
- **Purpose**: Store text segments with embeddings
- **Key Fields**: chunk_id (UUID), session_id (FK), page_number, chunk_text, chunk_metadata, embedding_reference
- **Relationships**: Belongs to DocumentSession

### ChatSession
- **Table**: `chat_sessions`
- **Purpose**: Conversation threads for document analysis
- **Key Fields**: chat_id (UUID), session_id (FK), user_id (FK), title
- **Relationships**: Belongs to DocumentSession and User, has many ChatMessages

### ChatMessage
- **Table**: `chat_messages`
- **Purpose**: Store conversation history
- **Key Fields**: message_id (UUID), chat_id (FK), role, message, retrieved_chunks, llm_response
- **Relationships**: Belongs to ChatSession

## Database Configuration

### Connection Pooling
- **Pool Size**: 10 connections
- **Max Overflow**: 20 additional connections
- **Pool Pre-ping**: Enabled (verifies connections before use)
- **Pool Recycle**: 3600 seconds (1 hour)

### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

## Usage

### In FastAPI Routes (Dependency Injection)
```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db, User

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

### In Background Tasks (Context Manager)
```python
from database import DatabaseSession, User

with DatabaseSession() as db:
    user = User(email="test@example.com", hashed_password="...")
    db.add(user)
    # Automatically commits on exit
```

### Creating Tables (Development Only)
```python
from database import create_tables

# Create all tables
create_tables()
```

**Note**: In production, use Alembic migrations instead of `create_tables()`.

## Foreign Key Cascade Deletes

All relationships use cascade deletes to maintain referential integrity:

- Deleting a User → deletes all their DocumentSessions and ChatSessions
- Deleting a DocumentSession → deletes all DocumentChunks and ChatSessions
- Deleting a ChatSession → deletes all ChatMessages

## Indexes

Performance indexes are created on:
- `users.email` (unique)
- `document_sessions(user_id, created_at)` - User session listing
- `document_sessions.processing_status` - Status filtering
- `document_chunks(session_id, page_number)` - Chunk retrieval
- `document_chunks.embedding_reference` (unique) - Vector lookup
- `chat_messages(chat_id, timestamp)` - Message ordering

## Requirements

The following dependencies are required (see `requirements.txt`):
- `sqlalchemy>=2.0.36`
- `psycopg2-binary>=2.9.10` (PostgreSQL driver)
- `alembic>=1.13.3` (for migrations)

## Next Steps

After setting up the database module:
1. Configure PostgreSQL database
2. Set `DATABASE_URL` in `.env` file
3. Run Alembic migrations (see task 1.2)
4. Implement authentication service (task 2.1)
