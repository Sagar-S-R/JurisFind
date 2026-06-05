# JurisFind

AI-powered legal document search and analysis platform. Search across 46,456+ legal cases using semantic similarity, read AI-generated summaries, ask follow-up questions, upload confidential documents for isolated analysis, and consult a legal domain chatbot. Backed by a FastAPI backend, PostgreSQL with pgvector, Celery for asynchronous processing, and a React frontend.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Documentation](#documentation)

## Features

### Semantic Search
Natural language search over indexed legal cases. Queries are embedded using `sentence-transformers/all-mpnet-base-v2` and compared against a FAISS index using cosine similarity. Results are ranked by relevance score.

### PDF Analysis and Contextual Q&A
Clicking any search result opens a document analysis view. The system asynchronously processes the PDF using Celery workers: extracting text with PyMuPDF, chunking it, generating embeddings, and storing them in PostgreSQL using pgvector. Once processed, users can ask follow-up questions against the document context using a Retrieval-Augmented Generation (RAG) pipeline backed by Groq LLMs.

### Confidential Document Analysis
Users can upload their own PDFs directly from the browser. The file is saved locally, processed asynchronously by Celery, and its embeddings are stored in the database. Users can chat with their documents in persistent, stateful sessions. 

### Legal Chatbot
A general-purpose AI assistant pre-prompted for legal domain queries. Accepts a message and conversation history, passes them through a LangChain agent backed by Groq, and returns a streamed response. Features a guardrail to reject non-legal queries.

## Architecture

The system relies on a decoupled architecture for performance and scalability:

- **Web Server:** FastAPI handles incoming HTTP requests, session management, and streaming LLM responses via Server-Sent Events (SSE).
- **Asynchronous Processing:** Celery workers (backed by RabbitMQ) handle heavy background tasks such as PDF text extraction, chunking, and embedding generation.
- **Database:** PostgreSQL stores user data, chat sessions, messages, and document metadata. The `pgvector` extension is used to store and query document embeddings natively in the database.
- **Frontend:** React application that provides the UI for semantic search, document management, and chat interfaces.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, lucide-react |
| Backend | FastAPI, Python 3.11, SQLAlchemy, Alembic |
| Task Queue | Celery, RabbitMQ |
| Database | PostgreSQL 17, pgvector |
| LLM | Groq `llama-3.3-70b-versatile` via LangChain |
| Embeddings | `sentence-transformers/all-mpnet-base-v2` |
| Search | FAISS (Main Corpus), pgvector (Session Documents) |
| PDF Processing | PyMuPDF, LangChain RecursiveCharacterTextSplitter |
| Deployment | Docker Compose, Nginx, Azure VM, Azure Static Web Apps |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Groq API key

### Backend & Database

The backend services are orchestrated using Docker Compose.

```bash
# 1. Start the database and message broker
docker-compose up db rabbitmq -d

# 2. Setup the Python environment
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your GROQ_API_KEY

# 4. Run database migrations
alembic upgrade head

# 5. Start the API server
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

# 6. Start the Celery worker (in a new terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Project Structure

```text
JurisFind/
├── backend/
│   ├── alembic/                 # Database migrations
│   ├── app/
│   │   ├── ai/                  # LangChain agents (RAG, Chatbot)
│   │   ├── api/                 # FastAPI routers (auth, sessions, documents)
│   │   ├── db/                  # SQLAlchemy models and CRUD operations
│   │   ├── schemas/             # Pydantic models for request/response validation
│   │   ├── services/            # Core business logic and blob storage integration
│   │   └── workers/             # Celery tasks (document processing)
│   ├── data/                    # Local storage for uploaded documents and FAISS index
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── config/              # API client configuration
│   │   ├── context/             # React Context (Auth)
│   │   └── pages/               # Main application views (Search, Assistant, Login)
│   └── package.json
└── docker-compose.yml           # Infrastructure definition (Postgres, RabbitMQ)
```

## Environment Variables

### Backend (.env)

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `RABBITMQ_URL` | RabbitMQ connection string |
| `GROQ_API_KEY` | Required for LLM inference |
| `SECRET_KEY` | JWT signing key |
| `USE_LOCAL_FILES` | Set to `true` to use local filesystem instead of Azure Blob |

### Frontend (.env)

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Backend URL (defaults to http://localhost:8000) |

## Documentation

Detailed documentation is available in the `docs/` directory:
- `docs/architecture.md`: System architecture and data flow.
- `docs/api_reference.md`: API endpoint specifications.
- `docs/technical_documentation.md`: Comprehensive internal reference.
