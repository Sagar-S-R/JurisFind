# Legal Bolt - Agentic AI Legal Document Analysis

<div align="center">

![Legal Bolt Logo](https://img.shields.io/badge/Legal%20Bolt-AI%20Powered-blue?style=for-the-badge&logo=law)

**A comprehensive full-stack agentic AI application for legal document analysis using advanced AI agents, LangChain, and Groq**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=white)](https://reactjs.org/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-AI%20Inference-00D4AA?style=flat&logo=groq&logoColor=white)](https://groq.com/)

</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Workflows](#usage-workflows)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

**Legal Bolt** is a cutting-edge agentic AI application designed specifically for legal professionals and researchers. It combines the power of modern AI agents with semantic search capabilities to revolutionize how legal documents are analyzed, summarized, and queried.

### What Makes Legal Bolt Special?

- **🤖 Agentic AI Architecture**: Unlike traditional chatbots, Legal Bolt uses intelligent AI agents that can reason, plan, and execute complex legal document analysis tasks
- **🧠 Context-Aware Processing**: Each document analysis creates temporary embeddings that provide deep contextual understanding
- **⚡ Real-time Analysis**: Powered by Groq's high-speed inference engine for instant document processing
- **🔍 Semantic Search**: Advanced FAISS-powered similarity search that understands legal concepts, not just keywords
- **📚 Comprehensive Coverage**: Handles everything from case law to contracts, briefs, and legal memoranda

### Target Users

- **Legal Professionals**: Attorneys, paralegals, and legal researchers seeking efficient document analysis
- **Law Students**: Academic researchers and students studying legal precedents and case law
- **Legal Tech Teams**: Developers building legal technology solutions
- **Compliance Teams**: Organizations needing to analyze legal documents for compliance purposes

## 🚀 Key Features

### 🤖 Agentic AI Architecture

**Intelligent Document Processing**
- **LangChain Integration**: Advanced prompt engineering and chain-based processing that enables complex reasoning workflows
- **Groq AI Models**: Powered by `llama3-70b-8192` for superior legal analysis with industry-leading inference speed
- **Intelligent Agents**: Context-aware document analysis with sophisticated memory management and reasoning capabilities
- **Temporary Embeddings**: Dynamic vector stores created for each document analysis session, ensuring isolated and secure processing

**Why Agentic AI?**
Unlike traditional document analysis tools, Legal Bolt uses AI agents that can:
- Plan multi-step analysis workflows
- Reason about document structure and legal concepts
- Maintain context across complex queries
- Adapt their approach based on document type and user needs

### 🎨 Frontend (React + Router)

**Professional Legal Interface**
- **Multi-Page Application**: Intuitive search interface with dedicated PDF analysis pages for focused document review
- **Real-time AI Interaction**: Instant document summarization and Q&A with live progress indicators
- **Professional Design**: Clean, responsive interface optimized for legal professionals with accessibility features
- **Smart Navigation**: Seamless routing between search and analysis workflows with breadcrumb navigation

**User Experience Features**
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Loading States**: Clear progress indicators during document processing
- **Error Handling**: User-friendly error messages with actionable suggestions
- **Keyboard Navigation**: Full keyboard accessibility for efficient workflow

### ⚙️ Backend (FastAPI + AI Agents)

**Robust API Architecture**
- **Agentic Architecture**: Intelligent document processing with LangChain agents that can handle complex legal reasoning tasks
- **PDF Processing**: Advanced text extraction with PyMuPDF supporting various PDF formats and structures
- **Vector Search**: Semantic similarity search using FAISS with configurable similarity thresholds
- **AI Summarization**: Comprehensive document analysis using Groq AI with specialized legal prompt templates
- **Context-aware Q&A**: Intelligent question answering with document-specific embeddings and conversation memory

**Performance & Scalability**
- **Async Processing**: Non-blocking API endpoints for handling multiple concurrent requests
- **Memory Management**: Efficient cleanup of temporary embeddings and resources
- **Caching**: Persistent FAISS index for fast search across document collections
- **Error Recovery**: Robust error handling with detailed logging and graceful degradation

## 🏗️ Architecture

### System Overview

Legal Bolt follows a modern microservices architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │   FastAPI Backend│    │   AI Services   │
│                 │    │                 │    │                 │
│ • Search UI     │◄──►│ • REST API      │◄──►│ • Groq AI       │
│ • Analysis UI   │    │ • LangChain     │    │ • Embeddings    │
│ • Router        │    │ • Vector Store  │    │ • FAISS Search  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

**1. Frontend Layer (React + Vite)**
- **Search Interface**: Semantic search with real-time results
- **Analysis Dashboard**: Document-specific analysis and Q&A interface
- **State Management**: React hooks for managing application state
- **API Client**: Axios-based HTTP client with error handling

**2. Backend Layer (FastAPI)**
- **API Gateway**: RESTful endpoints with automatic OpenAPI documentation
- **Agent Orchestrator**: LangChain-based AI agent coordination
- **Document Processor**: PDF text extraction and preprocessing
- **Vector Manager**: FAISS index management and similarity search

**3. AI Services Layer**
- **Groq Inference**: High-speed LLM inference for document analysis
- **Embedding Service**: HuggingFace sentence transformers for text embeddings
- **Vector Database**: FAISS for efficient similarity search
- **Memory Management**: Temporary embedding lifecycle management

### Data Flow

1. **Document Upload**: PDF → Text Extraction → Chunking → Embedding Generation
2. **Search Process**: Query → Embedding → FAISS Search → Ranked Results
3. **Analysis Process**: Document → AI Agent → Summary + Q&A Context
4. **Q&A Process**: Question → Context Retrieval → AI Response → User Interface

## 📚 Core Features

### 🔍 Advanced Search Capabilities

**Semantic Search Engine**
- **FAISS-Powered Similarity**: Vector-based search that understands legal concepts and context
- **Relevance Scoring**: Intelligent ranking based on semantic similarity and document metadata
- **Multi-Query Support**: Handle complex legal queries with multiple concepts
- **Filtering Options**: Filter by document type, date, court, or jurisdiction

**Search Features**
- **Fuzzy Matching**: Find relevant documents even with typos or variations
- **Concept Expansion**: Automatically expand legal terms and synonyms
- **Cross-Reference Detection**: Identify related cases and legal precedents
- **Citation Tracking**: Track how documents reference each other

### 🤖 AI-Powered Document Analysis

**Intelligent Summarization**
- **Multi-Aspect Analysis**: Comprehensive summaries covering key parties, legal issues, facts, and conclusions
- **Legal Structure Recognition**: Automatic identification of legal document components
- **Precedent Identification**: Highlight relevant legal precedents and case law
- **Risk Assessment**: Identify potential legal risks and implications

**Context-Aware Q&A**
- **Document-Specific Context**: Each Q&A session maintains document-specific understanding
- **Conversation Memory**: Maintain context across multiple questions
- **Citation Support**: Provide specific document sections supporting answers
- **Follow-up Questions**: Suggest relevant follow-up questions based on document content

### 🛠️ Advanced Features

**Prompt Engineering**
- **Legal-Specific Templates**: Specialized prompts for different types of legal documents
- **Adaptive Prompting**: Dynamic prompt adjustment based on document characteristics
- **Multi-Modal Reasoning**: Combine text analysis with document structure understanding
- **Chain-of-Thought**: Transparent reasoning process for AI decisions

**Performance Optimization**
- **Async Processing**: Non-blocking operations for better user experience
- **Caching Strategy**: Intelligent caching of embeddings and search results
- **Resource Management**: Automatic cleanup of temporary resources
- **Scalable Architecture**: Designed to handle large document collections

**Developer Experience**
- **Auto-Generated API Docs**: Interactive OpenAPI documentation at `/docs`
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Error Recovery**: Graceful handling of API failures and edge cases
- **Hot Reloading**: Fast development cycle with automatic reloading

## 🚀 Quick Start

### Prerequisites

Before starting, ensure you have the following installed:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Node.js** | 16+ | Frontend development and package management |
| **Python** | 3.9+ | Backend AI services and LangChain |
| **Conda/Miniconda** | Latest | Python environment management (recommended) |
| **Git** | Latest | Version control and cloning |

**API Keys Required:**
- **Groq API Key**: Get from [Groq Console](https://console.groq.com/keys)
  - Sign up for a free account
  - Generate an API key from the dashboard
  - Note: Free tier includes generous usage limits

### 📦 Installation Guide

#### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd Legal_Case

# Verify the project structure
ls -la
# Should show: api/, frontend/, README.md
```

#### Step 2: Backend Setup (AI Services)

```bash
# Navigate to the API directory
cd api

# Create and activate conda environment
conda create -p ./venv python=3.9 -y
conda activate ./venv

# Alternative: Using virtualenv
# python -m venv venv
# source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import langchain, groq, fastapi; print('✅ All dependencies installed successfully')"
```

**Configure Environment Variables:**

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API key
# Windows (PowerShell):
notepad .env

# macOS/Linux:
nano .env
```

**Required Environment Variables:**
```env
# Groq API Configuration
GROQ_API_KEY="your_groq_api_key_here"

# Model Configuration
GROQ_MODEL=llama3-70b-8192

# API Configuration
API_HOST=localhost
API_PORT=8000

# Optional: Customize AI behavior
TEMPERATURE=0.1
MAX_TOKENS=2048
```

#### Step 3: Frontend Setup (React Application)

```bash
# From project root, navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0

# Optional: Install additional development tools
npm install -g eslint prettier
```

**Frontend Environment (Optional):**
```bash
# Create frontend environment file for custom API URL
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env
```

#### Step 4: Start the Application

**Terminal 1 - Backend Services:**
```bash
# Navigate to API directory
cd api

# Activate environment
conda activate ./venv

# Start the FastAPI server
python main.py

# Expected output:
# INFO:     Started server process [xxxxx]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://localhost:8000
```

**Terminal 2 - Frontend Development Server:**
```bash
# Navigate to frontend directory
cd frontend

# Start Vite development server
npm run dev

# Expected output:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

### 🎯 First Run Verification

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/health
   # Expected: {"status": "healthy", "documents": X, "version": "1.0.0"}
   ```

2. **Frontend Access:**
   - Open browser to `http://localhost:5173`
   - You should see the Legal Bolt search interface

3. **API Documentation:**
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Test endpoints directly from the Swagger UI

### 🔧 Development Commands

**Backend Commands:**
```bash
# Start with auto-reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with debug logging
python main.py --debug

# Test specific endpoints
python -m pytest tests/  # If tests are available
```

**Frontend Commands:**
```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format code
npm run lint
npm run format
```

### 🚨 Common Setup Issues

**Python Environment Issues:**
```bash
# If conda command not found:
# Install Miniconda from: https://docs.conda.io/en/latest/miniconda.html

# If pip install fails:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

**Node.js Issues:**
```bash
# Clear npm cache if needed
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Key Issues:**
- Ensure your Groq API key is correctly set in the `.env` file
- Check that there are no extra spaces or quotes around the key
- Verify the API key is active in your Groq console

## 📚 API Documentation

### 🔍 Interactive API Explorer

The fastest way to explore and test the API is through the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 🏥 Health & Status Endpoints

#### GET `/api/health`
Check system status and document statistics.

**Response Example:**
```json
{
  "status": "healthy",
  "documents": 42,
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "groq_api": "connected",
    "faiss_index": "loaded",
    "embeddings": "ready"
  }
}
```

### 🔍 Search Endpoints

#### POST `/api/search`
Perform semantic search across the document collection.

**Request Body:**
```json
{
  "query": "contract breach remedies",
  "limit": 10,
  "min_similarity": 0.7
}
```

**Response Example:**
```json
{
  "results": [
    {
      "filename": "contract_law_breach.pdf",
      "similarity": 0.89,
      "score": 0.95,
      "metadata": {
        "title": "Contract Law: Breach and Remedies",
        "court": "Supreme Court",
        "date": "2023-06-15",
        "type": "case_law"
      },
      "snippet": "In cases of contract breach, the following remedies are available..."
    }
  ],
  "total_results": 15,
  "query_time": 0.234
}
```

#### GET `/api/pdf/{filename}`
Serve PDF files directly from the collection.

**Parameters:**
- `filename`: Name of the PDF file (URL encoded)

**Example:**
```bash
curl "http://localhost:8000/api/pdf/contract_law_breach.pdf"
```

### 🤖 Agentic AI Endpoints

#### POST `/api/analyze-document`
Perform comprehensive AI analysis of a specific document.

**Query Parameters:**
- `filename`: Name of the document to analyze

**Response Example:**
```json
{
  "filename": "contract_law_breach.pdf",
  "analysis": {
    "document_type": "Legal Case",
    "summary": "This case involves a contract dispute between two parties...",
    "key_parties": [
      {
        "name": "Plaintiff Corp",
        "role": "Plaintiff",
        "description": "Software development company"
      },
      {
        "name": "Defendant LLC",
        "role": "Defendant", 
        "description": "Technology consulting firm"
      }
    ],
    "legal_issues": [
      "Breach of contract",
      "Damages calculation",
      "Specific performance"
    ],
    "key_facts": [
      "Contract signed on 2022-01-15",
      "Development timeline: 6 months",
      "Payment structure: milestone-based"
    ],
    "legal_principles": [
      "Uniform Commercial Code Article 2",
      "Common law contract principles",
      "Restatement of Contracts"
    ],
    "conclusions": "The court found in favor of the plaintiff, awarding damages...",
    "significance": "This case establishes precedent for software development contracts..."
  },
  "processing_time": 12.5,
  "chunks_processed": 45
}
```

#### POST `/api/ask-question`
Ask context-aware questions about a specific document.

**Request Body:**
```json
{
  "filename": "contract_law_breach.pdf",
  "question": "What were the main arguments presented by the defendant?",
  "context": "previous_question_id" // Optional: for conversation context
}
```

**Response Example:**
```json
{
  "question": "What were the main arguments presented by the defendant?",
  "answer": "The defendant presented three main arguments: 1) The contract was ambiguous regarding delivery timelines, 2) Force majeure clauses should apply due to supply chain disruptions, and 3) The plaintiff failed to provide adequate specifications...",
  "sources": [
    {
      "chunk_id": 23,
      "text": "Defendant argued that the contract language was ambiguous...",
      "confidence": 0.92
    },
    {
      "chunk_id": 31,
      "text": "The force majeure argument centered on...",
      "confidence": 0.88
    }
  ],
  "follow_up_questions": [
    "How did the court respond to the ambiguity argument?",
    "What evidence supported the force majeure claim?",
    "Were there any precedents cited by the defendant?"
  ],
  "conversation_id": "conv_12345"
}
```

#### GET `/api/document-stats/{filename}`
Get statistics about document embeddings and processing.

**Response Example:**
```json
{
  "filename": "contract_law_breach.pdf",
  "stats": {
    "total_chunks": 45,
    "embedding_dimensions": 768,
    "total_tokens": 12500,
    "processing_time": 8.2,
    "created_at": "2024-01-15T10:30:00Z",
    "last_accessed": "2024-01-15T14:22:00Z"
  },
  "chunk_distribution": {
    "small_chunks": 12,
    "medium_chunks": 28,
    "large_chunks": 5
  }
}
```

#### DELETE `/api/cleanup-embeddings/{filename}`
Clean up temporary embeddings for a specific document.

**Response Example:**
```json
{
  "message": "Embeddings cleaned up successfully",
  "filename": "contract_law_breach.pdf",
  "freed_memory": "2.3 MB",
  "chunks_removed": 45
}
```

### 📄 Document Management

#### GET `/api/case/{filename}`
Get detailed metadata and information about a specific case.

**Response Example:**
```json
{
  "filename": "contract_law_breach.pdf",
  "metadata": {
    "title": "Smith v. Johnson Contract Dispute",
    "court": "Supreme Court of California",
    "date": "2023-06-15",
    "case_number": "SC-2023-001234",
    "type": "case_law",
    "jurisdiction": "California",
    "area_of_law": "Contract Law",
    "keywords": ["breach", "contract", "damages", "software development"],
    "file_size": "2.1 MB",
    "page_count": 45,
    "word_count": 12500
  },
  "parties": [
    {
      "name": "Smith Software Corp",
      "role": "Plaintiff",
      "representation": "Jones & Associates"
    },
    {
      "name": "Johnson Consulting LLC", 
      "role": "Defendant",
      "representation": "Legal Partners Inc"
    }
  ],
  "procedural_history": [
    {
      "date": "2022-01-15",
      "event": "Contract executed",
      "description": "Software development agreement signed"
    },
    {
      "date": "2023-03-20",
      "event": "Complaint filed",
      "description": "Plaintiff files breach of contract claim"
    }
  ]
}
```

### 🔧 Error Handling

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The requested document 'nonexistent.pdf' was not found",
    "details": {
      "filename": "nonexistent.pdf",
      "available_documents": ["contract_law_breach.pdf", "tort_law_basics.pdf"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

**Common Error Codes:**
- `DOCUMENT_NOT_FOUND`: Requested document doesn't exist
- `INVALID_FILENAME`: Filename format is invalid
- `GROQ_API_ERROR`: External AI service error
- `EMBEDDING_ERROR`: Document processing failed
- `QUERY_TOO_SHORT`: Search query is too short
- `RATE_LIMIT_EXCEEDED`: Too many requests

### 📊 Rate Limiting

API endpoints have the following rate limits:
- **Search**: 60 requests per minute
- **Analysis**: 10 requests per minute  
- **Q&A**: 30 requests per minute
- **Health**: 120 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642248000
```

## 💼 Usage Workflows

### 🔍 Workflow 1: Legal Research & Document Discovery

**Step 1: Semantic Search**
```bash
# Navigate to the main search page
http://localhost:5173/

# Enter your legal query
"contract breach remedies in software development agreements"

# View ranked results with similarity scores
# Each result shows:
# - Document title and metadata
# - Similarity percentage (0-100%)
# - Key snippet from the document
# - Court, date, and case type information
```

**Step 2: Result Filtering & Selection**
- Use similarity thresholds to filter relevant results
- Sort by date, court, or relevance
- Preview document snippets before full analysis
- Access document metadata for context

**Step 3: Document Access**
- Click on any result to view the full PDF
- Download documents for offline review
- Share document links with team members

### 🤖 Workflow 2: AI-Powered Document Analysis

**Step 1: Initiate Analysis**
```bash
# Click "AI Analysis" button on any search result
# Navigate to: http://localhost:5173/analyze/contract_law_breach.pdf
```

**Step 2: Comprehensive Analysis**
The AI agent automatically generates:

**Document Overview:**
- Document type identification (case law, contract, brief, etc.)
- Executive summary with key points
- Document structure analysis

**Legal Analysis:**
- **Key Parties**: Names, roles, and descriptions of all involved parties
- **Legal Issues**: Main legal questions and disputes addressed
- **Key Facts**: Chronological timeline of important events
- **Legal Principles**: Relevant laws, regulations, and precedents cited
- **Conclusions**: Court findings, decisions, and outcomes
- **Significance**: Legal precedent value and implications

**Step 3: Analysis Review**
- Review AI-generated summary for accuracy
- Identify areas needing deeper investigation
- Note any missing information or context
- Prepare for targeted Q&A session

### 💬 Workflow 3: Interactive Legal Q&A

**Step 1: Context Setup**
```bash
# Use the Q&A panel on the analysis page
# The system automatically loads document-specific context
# Previous conversation history is maintained
```

**Step 2: Question Types**

**Quick Questions (Pre-built Templates):**
- "What were the main legal arguments?"
- "Who were the key parties involved?"
- "What was the court's decision?"
- "What legal precedents were cited?"

**Custom Questions:**
- "How does this case relate to [specific legal principle]?"
- "What evidence supported the plaintiff's claims?"
- "Were there any dissenting opinions?"
- "How might this case apply to [your specific situation]?"

**Step 3: Advanced Querying**
```bash
# Multi-part questions
"What were the defendant's three main arguments and how did the court respond to each?"

# Comparative analysis
"How does this case differ from [Case Name] in terms of damages calculation?"

# Procedural questions
"What was the timeline of events leading to the breach?"
```

**Step 4: Answer Analysis**
- Review AI responses with source citations
- Check confidence scores for answer reliability
- Follow suggested follow-up questions
- Maintain conversation context across multiple questions

### 🔄 Workflow 4: Multi-Document Research

**Step 1: Cross-Document Analysis**
```bash
# Search for related cases
"software development contract disputes"

# Analyze multiple documents
# Compare findings across cases
# Identify patterns and trends
```

**Step 2: Comparative Research**
- Identify common legal principles across cases
- Compare court decisions and reasoning
- Track evolution of legal precedents
- Build comprehensive understanding of legal landscape

**Step 3: Synthesis & Documentation**
- Combine insights from multiple documents
- Create comprehensive legal briefs
- Develop arguments based on multiple precedents
- Document research methodology and findings

### 🛠️ Workflow 5: System Management

**Memory Management:**
```bash
# Check document statistics
GET /api/document-stats/{filename}

# Clean up temporary embeddings
DELETE /api/cleanup-embeddings/{filename}

# Monitor system health
GET /api/health
```

**Resource Optimization:**
- Regular cleanup of temporary embeddings
- Monitor memory usage and performance
- Archive completed research sessions
- Maintain organized document collections

### 📊 Advanced Usage Patterns

**Legal Research Patterns:**
1. **Broad Discovery**: Start with general queries to find relevant documents
2. **Focused Analysis**: Deep-dive into specific documents with AI analysis
3. **Targeted Q&A**: Ask specific questions about legal principles or facts
4. **Comparative Study**: Compare multiple documents for comprehensive understanding
5. **Synthesis**: Combine insights into actionable legal advice

**Collaborative Workflows:**
- Share document analysis links with team members
- Export AI-generated summaries for reports
- Create research trails with question-answer pairs
- Build knowledge bases from document collections

**Quality Assurance:**
- Cross-reference AI summaries with original documents
- Verify legal citations and precedents
- Validate factual claims against source material
- Update analysis as new information becomes available

## Technology Stack

### Frontend
- **React 18**: Modern JavaScript framework with hooks
- **React Router**: Client-side routing for multi-page application
- **TailwindCSS**: Utility-first CSS framework for rapid UI development
- **Axios**: HTTP client for API requests
- **Lucide React**: Modern icon library

### Backend & AI
- **FastAPI**: High-performance Python web framework
- **LangChain**: Advanced AI agent framework for document processing
- **Groq AI**: High-speed inference with llama3-70b-8192 model
- **FAISS**: Efficient vector similarity search
- **HuggingFace Embeddings**: Text embedding generation
- **PyMuPDF**: Advanced PDF text extraction

### AI Models & Services
- **Embeddings**: `sentence-transformers/all-mpnet-base-v2`
- **Language Model**: `llama3-70b-8192` via Groq API
- **Vector Store**: FAISS for similarity search
- **Text Splitting**: Recursive character text splitter for chunking

## File Structure

```
Legal_Case/
├── frontend/                     # Frontend React (Vite) application
│   ├── index.html                # Vite HTML entry
│   ├── package.json              # Frontend dependencies and scripts
│   ├── vite.config.ts            # Vite configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── eslint.config.js          # ESLint config
│   └── (src/, etc.)              # App source files (not fully listed here)
├── api/                          # Backend FastAPI application
│   ├── main.py                   # FastAPI app entry point
│   ├── routes.py                 # All API endpoints
│   ├── legal_agent.py            # LangChain AI agent (CORE)
│   ├── search_service.py         # Vector search operations
│   ├── generate_embeddings.py    # PDF processing & embedding generation
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Backend environment variables
│   ├── .env.example              # Backend environment template
│   ├── pdfs/                     # PDF documents (local)
│   └── faiss_store/              # Pre-generated embeddings
│       ├── legal_cases.index     # FAISS index file
│       └── id2name.json          # Document metadata
└── README.md                     # Project documentation
```

## Configuration

### Environment Variables
Create a `.env` file in the `api/` directory:

```env
# Groq API Configuration
GROQ_API_KEY="your_groq_api_key_here"

# Model Configuration
GROQ_MODEL=llama3-70b-8192

# API Configuration
API_HOST=localhost
API_PORT=8000
```

Optionally, create a `.env` file in the `frontend/` directory for local dev:

```env
# Frontend Vite config
VITE_API_BASE_URL="http://localhost:8000/api"
```

### AI Model Configuration
The application uses optimized models for legal document analysis:

- **Embeddings**: `sentence-transformers/all-mpnet-base-v2` (High-quality embeddings)
- **Language Model**: `llama3-70b-8192` via Groq (Fast, powerful legal analysis)
- **Text Chunking**: 1000 character chunks with 200 character overlap
- **Vector Search**: FAISS with cosine similarity

### Frontend Configuration
- **React Router**: Handles navigation between search and analysis pages
- **API Base URL**: Defaults to `http://localhost:8000/api` (override with `VITE_API_BASE_URL` in `frontend/.env`)
- **Responsive Design**: Optimized for desktop and mobile use

## Development

### Adding New Features
1. **Backend AI Agents**: Extend `legal_agent.py` with new LangChain chains
2. **Frontend Pages**: Add routes in the frontend app and create page components
3. **API Endpoints**: Add new endpoints in `routes.py` with proper Pydantic models
4. **Prompt Engineering**: Modify chat templates in `legal_agent.py` for better AI responses

### Testing the Agentic AI System
- **Backend**: Visit `http://localhost:8000/docs` for interactive API testing
- **Agent Testing**: Test individual agent functions via FastAPI docs
- **Frontend**: Use browser developer tools for debugging React components
- **Integration**: Test the complete workflow from search → analysis → Q&A

### Customizing AI Behavior
- **Prompt Templates**: Modify summary and Q&A templates in `legal_agent.py`
- **Model Parameters**: Adjust temperature, max_tokens for different AI behavior
- **Chunking Strategy**: Modify text splitter parameters for different document types
- **Vector Search**: Adjust FAISS search parameters and similarity thresholds

## Troubleshooting

### Common Issues
1. **Groq API Errors**: Ensure GROQ_API_KEY is set correctly in `.env`
2. **Model Decommissioned**: Update to supported models (currently using llama3-70b-8192)
3. **LangChain Import Errors**: Ensure all LangChain packages are installed correctly
4. **PDF Processing**: Ensure PDFs contain extractable text (not scanned images)
5. **Memory Issues**: Clean up temporary embeddings regularly for large documents
6. **CORS Errors**: Ensure backend runs on port 8000 and frontend on 5173. If needed, set `VITE_API_BASE_URL` to match the backend URL.

### Path & Folder Tips
- **Frontend path**: All npm scripts run inside `frontend/` (e.g., `cd frontend && npm run dev`).
- **Backend path**: All Python commands run inside `api/` (e.g., `cd api && python main.py`).
- **Data directories**: Keep PDFs in `api/pdfs/`. Generated embeddings live in `api/faiss_store/`.
- **Env files**: Backend uses `api/.env`. Frontend can use `frontend/.env` for local overrides.

### Performance Tips
- **Document Analysis**: Large documents are automatically chunked for better processing
- **Memory Management**: Use cleanup endpoints to free temporary embeddings
- **Concurrent Requests**: Each document analysis creates isolated embeddings
- **Caching**: FAISS index is persistent across application restarts

### AI Agent Debugging
- **Agent Initialization**: Check logs for successful Groq client creation
- **Embedding Creation**: Verify temporary vector stores are created successfully
- **Prompt Engineering**: Monitor AI responses and adjust templates as needed
- **Token Limits**: Large documents are truncated to stay within model limits

## ❓ FAQ

### General Questions

**Q: What types of legal documents can Legal Bolt analyze?**
A: Legal Bolt can analyze various legal documents including:
- Court cases and judicial opinions
- Contracts and agreements
- Legal briefs and memoranda
- Statutes and regulations
- Legal research papers
- Any PDF document containing legal text

**Q: How accurate is the AI analysis?**
A: The AI analysis is highly accurate for:
- Document summarization and key point extraction
- Legal concept identification
- Party and issue identification
- However, always verify AI-generated content against original documents for critical legal work

**Q: Can I use Legal Bolt for client work?**
A: Legal Bolt is designed as a research and analysis tool. Always:
- Review AI-generated content for accuracy
- Cross-reference with original documents
- Follow your jurisdiction's professional responsibility rules
- Consider it a starting point for further research

### Technical Questions

**Q: How much does the Groq API cost?**
A: Groq offers a generous free tier with:
- Fast inference speeds
- Reasonable usage limits for development and testing
- Pay-as-you-go pricing for production use
- Check [Groq Pricing](https://console.groq.com/pricing) for current rates

**Q: Can I run Legal Bolt without an internet connection?**
A: No, Legal Bolt requires internet connectivity for:
- Groq AI inference services
- HuggingFace model downloads
- Real-time document analysis

**Q: How many documents can I analyze simultaneously?**
A: The system is designed to handle:
- Multiple concurrent searches
- One document analysis at a time (to ensure quality)
- Automatic cleanup of temporary embeddings
- Scalable architecture for growing document collections

### Performance Questions

**Q: How fast is document analysis?**
A: Typical processing times:
- Small documents (< 10 pages): 5-15 seconds
- Medium documents (10-50 pages): 15-60 seconds
- Large documents (50+ pages): 1-3 minutes
- Search queries: < 1 second

**Q: Can I customize the AI prompts?**
A: Yes, you can modify:
- Legal analysis templates in `legal_agent.py`
- Prompt parameters (temperature, max_tokens)
- Analysis focus areas
- Q&A conversation styles

## 🔒 Security & Privacy

### Data Handling

**Document Privacy:**
- Documents are processed locally on your machine
- Temporary embeddings are created in memory
- No documents are stored on external servers
- Automatic cleanup of temporary data

**API Security:**
- All API endpoints use HTTPS in production
- Rate limiting prevents abuse
- Input validation and sanitization
- Error handling without sensitive data exposure

**Best Practices:**
- Keep your Groq API key secure
- Use environment variables for sensitive configuration
- Regularly update dependencies for security patches
- Monitor API usage and costs

### Compliance Considerations

**Legal Professional Responsibility:**
- Always review AI-generated content
- Maintain client confidentiality
- Follow jurisdiction-specific rules
- Document your research methodology

**Data Retention:**
- Temporary embeddings are automatically cleaned up
- Original documents remain in your control
- No persistent storage of document content
- Configurable retention policies

## 🤝 Contributing

### How to Contribute

We welcome contributions from the legal tech community! Here's how you can help:

**1. Bug Reports**
- Use the GitHub issue tracker
- Include detailed reproduction steps
- Provide system information and logs
- Check existing issues before creating new ones

**2. Feature Requests**
- Describe the use case and benefits
- Provide mockups or examples when possible
- Consider implementation complexity
- Discuss with maintainers before major changes

**3. Code Contributions**
- Fork the repository
- Create a feature branch
- Follow the coding standards
- Add tests for new functionality
- Submit a pull request with clear description

### Development Guidelines

**Code Style:**
- Python: Follow PEP 8 guidelines
- JavaScript/React: Use ESLint and Prettier
- TypeScript: Strict type checking enabled
- Documentation: Update README for significant changes

**Testing:**
```bash
# Backend testing
cd api
python -m pytest tests/

# Frontend testing
cd frontend
npm test

# Integration testing
npm run test:integration
```

**Pull Request Process:**
1. Ensure all tests pass
2. Update documentation as needed
3. Add changelog entry
4. Request review from maintainers
5. Address feedback promptly

### Community Guidelines

**Communication:**
- Be respectful and professional
- Provide constructive feedback
- Help others learn and grow
- Follow the code of conduct

**Legal Considerations:**
- Respect intellectual property rights
- Don't include proprietary legal documents
- Ensure contributions comply with applicable laws
- Maintain professional standards

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**MIT License Summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ No warranty provided
- ⚠️ No liability assumed

## 🆘 Support & Community

### Getting Help

**Documentation:**
- This README provides comprehensive guidance
- API documentation at `http://localhost:8000/docs`
- Code comments and docstrings
- Example workflows and use cases

**Community Support:**
- GitHub Discussions for questions and ideas
- GitHub Issues for bug reports and feature requests
- Stack Overflow with `legal-bolt` tag
- Legal tech community forums

**Professional Support:**
- For enterprise deployments
- Custom integrations and features
- Training and consultation services
- Priority support and SLA

### Reporting Issues

When reporting issues, please include:

**System Information:**
```bash
# Backend environment
python --version
pip list | grep -E "(fastapi|langchain|groq)"

# Frontend environment
node --version
npm list --depth=0

# Operating system
uname -a  # Linux/macOS
systeminfo  # Windows
```

**Issue Details:**
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs and error messages
- Screenshots if applicable

**Contact Information:**
- GitHub: [Project Repository](https://github.com/your-repo/legal-bolt)
- Email: support@legal-bolt.com
- Documentation: [Project Wiki](https://github.com/your-repo/legal-bolt/wiki)

---

<div align="center">

**Legal Bolt** - Empowering Legal Professionals with AI


[![GitHub stars](https://img.shields.io/github/stars/your-repo/legal-bolt?style=social)](https://github.com/your-repo/legal-bolt)
[![GitHub forks](https://img.shields.io/github/forks/your-repo/legal-bolt?style=social)](https://github.com/your-repo/legal-bolt)
[![GitHub issues](https://img.shields.io/github/issues/your-repo/legal-bolt)](https://github.com/your-repo/legal-bolt/issues)

</div>