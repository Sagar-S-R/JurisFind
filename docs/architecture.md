# Architecture

## System Overview

Legal Case uses a microservices architecture with three main layers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend│    │   AI Services   │
│                 │    │                 │    │                 │
│ • Search UI     │◄──►│ • REST API      │◄──►│ • Groq AI       │
│ • Analysis UI   │    │ • LangChain     │    │ • Embeddings    │
│ • Router        │    │ • Vector Store  │    │ • FAISS Search  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### Frontend Layer
- **React 18** with Vite build tool
- **React Router** for navigation
- **Tailwind CSS** for styling
- **Axios** for API communication

### Backend Layer
- **FastAPI** for REST API
- **LangChain** for AI agent orchestration
- **FAISS** for vector similarity search
- **PyMuPDF** for PDF processing

### AI Services Layer
- **Groq API** for LLM inference
- **Sentence Transformers** for embeddings
- **FAISS** for vector storage

## Data Flow

1. **Ingestion**: PDF → Text Extraction → Chunking → Embedding → FAISS Index
2. **Search**: Query → Embedding → FAISS Search → Ranked Results
3. **Analysis**: Document + Query → AI Agent → Response

## Key Design Patterns

- **Separation of Concerns**: Clear boundaries between layers
- **Async Processing**: Non-blocking operations
- **Stateless API**: RESTful design
- **Vector Search**: Semantic similarity over keyword matching