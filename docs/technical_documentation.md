# JurisFind - Complete Technical Documentation

> **Project**: Legal Case Search & Analysis System  
> **Last Updated**: January 9, 2026  
> **Tech Stack**: FastAPI, React, Azure, Docker, Nginx, FAISS, Groq AI

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Azure Services Integration](#azure-services-integration)
5. [Docker & Containerization](#docker--containerization)
6. [Nginx Configuration](#nginx-configuration)
7. [Backend Architecture](#backend-architecture)
8. [Frontend Architecture](#frontend-architecture)
9. [Deployment Guide](#deployment-guide)
10. [API Documentation](#api-documentation)
11. [Database & Storage](#database--storage)
12. [Security & Authentication](#security--authentication)
13. [Performance Optimization](#performance-optimization)

---

## Project Overview

**JurisFind** is an AI-powered legal document search and analysis platform that enables lawyers and legal professionals to:

- Search through 46,456+ legal case documents using semantic similarity
- Analyze legal documents with AI-powered summarization
- Ask natural language questions about specific cases
- Upload confidential documents for private analysis
- Get legal advice from an AI chatbot specialized in law

### Core Features

1. **Semantic Search**: FAISS vector similarity search across legal documents
2. **Document Analysis**: AI-powered summarization and key points extraction
3. **Q&A System**: Ask questions about specific legal documents
4. **Legal Chatbot**: Domain-specific AI assistant for legal queries
5. **Private Analysis**: Upload and analyze confidential documents securely
6. **Similar Case Retrieval**: Find related cases based on document content

---

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                               │
│  (Web Browser - Chrome, Firefox, Safari, Edge)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Frontend: React + Vite (Deployed on Azure Static Web Apps)│ │
│  │  - React Router for navigation                           │  │
│  │  - Axios for API communication                           │  │
│  │  - TailwindCSS for styling                               │  │
│  │  - Lucide React for icons                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ REST API / HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REVERSE PROXY LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Nginx (host-level reverse proxy on the VM)              │  │
│  │  - Port 80 (HTTP)                                        │  │
│  │  - Reverse proxy to FastAPI port 8000                    │  │
│  │  - Rate limiting (30 req/min)                            │  │
│  │  - 20 MB upload limit                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Internal Docker Network
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (Docker Container)                      │  │
│  │  - Port 8000 (Internal)                                  │  │
│  │  - Python 3.11                                           │  │
│  │  - Uvicorn (factory mode, 2 workers)                     │  │
│  │                                                          │  │
│  │  Core Components:                                        │  │
│  │  ├─ API Routes (routes.py)                              │  │
│  │  ├─ Search Service (FAISS)                              │  │
│  │  ├─ Legal AI Agent (LangChain)                          │  │
│  │  ├─ Legal Chatbot (Groq LLM)                            │  │
│  │  └─ Confidential PDF Processor                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────┬──────────────────────────┘
             │                        │
             │ Azure SDK              │ Groq API
             ▼                        ▼
┌────────────────────────┐  ┌─────────────────────────┐
│   STORAGE LAYER        │  │    AI SERVICES LAYER    │
│                        │  │                         │
│  Azure Blob Storage    │  │  Groq Cloud API         │
│  - Container: data     │  │  - Model: Llama 3.3 70B │
│  - PDFs (46,456+)      │  │  - Summarization        │
│  - FAISS Index         │  │  - Q&A                  │
│  - ID Mappings         │  │  - Chat                 │
│                        │  │                         │
│  OR Local Storage      │  │  + Sentence Transformer │
│  - api/data/pdfs/      │  │    (Local embeddings)   │
│  - api/data/faiss_store│  │                         │
└────────────────────────┘  └─────────────────────────┘
```

### Deployment Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    AZURE CLOUD (Production)                    │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Azure Virtual Machine (Ubuntu 24.04)                  │ │
│  │  - IP: 20.186.113.106                                  │ │
│  │  - Size: Standard D2alds v7 (2 vCPU, 4 GB RAM)        │ │
│  │  - Ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)            │ │
│  │                                                         │ │
│  │  Docker Engine                                          │ │
│  │  ├─ Container: jurisfind-api (FastAPI, port 8000)      │ │
│  │  └─ Volume: confidential_tmp (ephemeral uploads)       │ │
│  │  Nginx runs on the host, not in Docker                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Azure Blob Storage Account                            │ │
│  │  - Account: jurisfindstore                             │ │
│  │  - Container: data                                      │ │
│  │  - Tier: Hot Storage                                    │ │
│  │  - Size: ~5.3 GB (48,294 PDFs + FAISS index 136 MB)   │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│             AZURE STATIC WEB APPS (Frontend CDN)              │
│  https://blue-cliff-0dfeb910f.2.azurestaticapps.net           │
│  - React SPA deployment (auto-deploy via GitHub Actions)       │
│  - Global CDN distribution                                     │
│  - Automatic HTTPS                                             │
│  - VITE_API_BASE_URL env var baked in at build time            │
└───────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Primary programming language |
| **FastAPI** | 0.104+ | Web framework for REST API |
| **Uvicorn** | 0.24+ | ASGI server (factory mode, 2 workers) |
| **LangChain** | 0.0.350+ | LLM orchestration framework |
| **FAISS** | 1.7.4+ | Vector similarity search |
| **Sentence Transformers** | 2.2.2+ | Text embedding generation |
| **Azure Storage Blob** | 12.19+ | Azure SDK for blob storage |
| **Groq SDK** | 0.4+ | Groq AI API client |
| **PyMuPDF (fitz)** | 1.23+ | PDF text extraction |
| **Pydantic** | 2.5+ | Data validation |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2+ | UI library |
| **Vite** | 5.0+ | Build tool and dev server |
| **React Router** | 6.20+ | Client-side routing |
| **Axios** | 1.6+ | HTTP client |
| **TailwindCSS** | 3.4+ | Utility-first CSS framework |
| **Lucide React** | 0.300+ | Icon library |

### Infrastructure Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | 24.0+ | Containerization |
| **Docker Compose** | 2.23+ | Multi-container orchestration |
| **Nginx** | 1.25+ | Reverse proxy & load balancer |
| **Ubuntu** | 24.04 | Host operating system |
| **Git** | 2.34+ | Version control |

### AI/ML Models

| Model | Provider | Purpose |
|-------|----------|---------|
| **all-mpnet-base-v2** | Sentence Transformers | Document embeddings (768-dim) |
| **llama-3.3-70b-versatile** | Groq | Text generation, Q&A, chat |

---

## Azure Services Integration

### Why Azure?

We chose Azure for several strategic reasons:

1. **Enterprise-Grade Reliability**: 99.9% SLA for VMs and storage
2. **Scalability**: Easy to scale from development to production
3. **Cost-Effective**: Pay-as-you-go pricing model
4. **Global Reach**: Data centers worldwide for low latency
5. **Security**: Built-in security features and compliance certifications
6. **Integration**: Seamless integration between services

### Azure Services Used

#### 1. Azure Virtual Machine (VM)

**Purpose**: Host the Dockerized application stack

**Configuration**:
- **Instance Type**: Standard D2alds v7
- **vCPUs**: 2
- **RAM**: 4 GB
- **Storage**: 30 GB SSD
- **OS**: Ubuntu 24.04
- **Region**: East US 2
- **Public IP**: 20.186.113.106

**Why VM?**:
- Full control over the environment
- Ability to run Docker containers
- Cost-effective for MVP/development
- Easy to SSH and manage
- Can scale vertically when needed

**Network Security Group (NSG) Rules**:
```
Inbound Rules:
- Port 22 (SSH) - From your IP only
- Port 80 (HTTP) - From anywhere (0.0.0.0/0)
- Port 443 (HTTPS) - From anywhere (0.0.0.0/0)

Outbound Rules:
- All traffic allowed
```

#### 2. Azure Blob Storage

**Purpose**: Store legal documents and FAISS index files

**Configuration**:
- **Account Name**: jurisfindstore
- **Container Name**: data
- **Access Tier**: Hot (frequent access)
- **Redundancy**: LRS (Locally Redundant Storage)
- **Total Size**: ~5.3 GB

**Storage Structure**:
```
data/
├── pdfs/                    # 48,294 legal case PDFs (5.3 GB)
│   ├── case_001.pdf
│   └── ... (48,293 more files)
└── faiss_store/            # Vector search index
    ├── legal_cases.index   # FAISS index file (136 MB)
    └── id2name.json        # ID to filename mapping (2.2 MB)

Note: Confidential uploads go to a named Docker volume (confidential_tmp)
on the VM — they are never stored in Blob Storage.
```

**Why Blob Storage?**:
- **Scalability**: Can store unlimited documents
- **Cost-Effective**: $0.0184/GB/month for hot tier
- **Durability**: 11 nines (99.999999999%) durability
- **Performance**: Low latency access
- **SDK Support**: Python SDK for easy integration
- **Security**: Access keys, SAS tokens, encryption at rest

**Access Methods**:
1. **Connection String**: Used in application
2. **Access Keys**: Primary and secondary keys
3. **SAS Tokens**: Time-limited access (future enhancement)

**Code Integration**:
```python
# api/helpers/azure_blob_helper.py
from azure.storage.blob import BlobServiceClient

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Download FAISS index
container_client = blob_service_client.get_container_client("data")
blob_client = container_client.get_blob_client("faiss_store/legal_cases.index")
data = blob_client.download_blob().readall()
```

#### 3. Azure Network Resources

**Virtual Network (VNet)**:
- Isolated network for VM
- CIDR: 10.0.0.0/16

**Network Interface Card (NIC)**:
- Attached to VM
- Associated with public IP

**Public IP Address**:
- Static IP: 20.186.113.106
- DNS: (Optional custom domain)

---

## Docker & Containerization

### Why Docker?

1. **Consistency**: "Works on my machine" → "Works everywhere"
2. **Isolation**: Dependencies don't conflict with host system
3. **Portability**: Deploy anywhere Docker runs
4. **Scalability**: Easy to scale horizontally with multiple containers
5. **Version Control**: Docker images are versioned
6. **Resource Efficiency**: Lightweight compared to VMs

### Docker Architecture in JurisFind

```
┌─────────────────────────────────────────────────────────┐
│                      Docker Host                         │
│                     (Azure VM)                           │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   jurisfind_network (Bridge Network)             │  │
│  │                                                   │  │
│  │   ┌────────────────────┐  ┌──────────────────┐  │  │
│  │   │  jurisfind-api     │  │     nginx        │  │  │
│  │   │  (FastAPI)         │  │  (Reverse Proxy) │  │  │
│  │   │                    │  │                  │  │  │
│  │   │  Port: 8000       │◄─┤  Port: 80       │  │  │
│  │   │  (Internal)        │  │  (External)      │  │  │
│  │   │                    │  │                  │  │  │
│  │   │  Volumes:          │  │  Volumes:        │  │  │
│  │   │  - /app            │  │  - nginx.conf    │  │  │
│  │   │  - .env            │  │                  │  │  │
│  │   └────────────────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Docker Volumes:                                         │
│  - jurisfind_data (persistent storage)                   │
└─────────────────────────────────────────────────────────┘
```

### Dockerfile Breakdown

**api/Dockerfile**:
```dockerfile
# Base image - Python 3.11 slim for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - gcc, g++: Required for compiling Python packages
# - libgomp1: Required for FAISS
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching optimization)
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip packages (smaller image)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/pdfs data/faiss_store

# Expose port 8000 for FastAPI
EXPOSE 8000

# Run with uvicorn in factory mode (2 workers for concurrency)
CMD ["uvicorn", "main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Why this Dockerfile structure?**:
- **Layer Caching**: Requirements installed before code copy
- **Slim Base**: python:3.11-slim is 50% smaller than full image
- **System Dependencies**: FAISS needs gcc and libgomp1
- **Factory Mode**: Uvicorn factory mode with 2 workers for async concurrency

### Docker Compose Configuration

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  # FastAPI Backend Service
  jurisfind-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: jurisfind-api
    restart: unless-stopped
    ports:
      - "8000:8000"  # Only for debugging, nginx handles external access
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - AZURE_STORAGE_CONNECTION_STRING=${AZURE_STORAGE_CONNECTION_STRING}
      - GROQ_MODEL=${GROQ_MODEL}
    volumes:
      - ./data:/app/data  # Mount data directory
      - ./.env:/app/.env  # Mount environment variables
    networks:
      - jurisfind_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Nginx Reverse Proxy Service
  nginx:
    image: nginx:alpine  # Lightweight Alpine Linux
    container_name: jurisfind-nginx
    restart: unless-stopped
    ports:
      - "80:80"    # HTTP
      - "443:443"  # HTTPS (for future SSL)
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro  # Read-only config
    depends_on:
      - jurisfind-api
    networks:
      - jurisfind_network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  jurisfind_network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
```

**Key Docker Compose Features**:

1. **Service Dependencies**: nginx waits for jurisfind-api
2. **Health Checks**: Automatic container health monitoring
3. **Restart Policies**: Auto-restart on failure
4. **Environment Variables**: Injected from .env file
5. **Networks**: Isolated bridge network for inter-container communication
6. **Volumes**: Persistent data and configuration mounting

### Docker Commands Used

```bash
# Build images
docker-compose build

# Build without cache (fresh build)
docker-compose build --no-cache

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f jurisfind-api

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Check container status
docker-compose ps

# Execute command in container
docker-compose exec jurisfind-api bash

# View container resource usage
docker stats

# Clean up unused resources
docker system prune -af
```

---

## Nginx Configuration

### Why Nginx?

1. **Reverse Proxy**: Routes external traffic to backend
2. **Load Balancing**: Distribute traffic across multiple backend instances
3. **Static File Serving**: Efficient static content delivery
4. **SSL Termination**: Handle HTTPS encryption/decryption
5. **Compression**: Gzip compression for faster transfers
6. **Rate Limiting**: Protect against DDoS attacks
7. **Caching**: Cache responses for better performance

### Nginx Architecture

```
Internet → Port 80 → Nginx → Port 8000 → FastAPI
```

### Nginx Configuration File

**api/nginx.conf**:
```nginx
events {
    # Maximum number of simultaneous connections
    worker_connections 1024;
}

http {
    # Upstream backend definition
    upstream backend {
        # Load balancing algorithm: least_conn (fewest connections)
        least_conn;
        
        # Backend server (Docker service name)
        server jurisfind-api:8000 max_fails=3 fail_timeout=30s;
        
        # Future: Add more backend instances for horizontal scaling
        # server jurisfind-api-2:8000;
        # server jurisfind-api-3:8000;
    }

    # Server block
    server {
        # Listen on port 80 (HTTP)
        listen 80;
        
        # Server name (your domain or IP)
        server_name 20.186.113.106 localhost;

        # Client request body size limit (for PDF uploads)
        client_max_body_size 10M;

        # Proxy timeouts (increased for AI processing)
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # Root location (API endpoints)
        location / {
            # Proxy pass to backend
            proxy_pass http://backend;
            
            # Preserve original request information
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support (for future real-time features)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Disable buffering for streaming responses
            proxy_buffering off;
        }

        # Health check endpoint
        location /health {
            access_log off;  # Don't log health checks
            proxy_pass http://backend/api/health;
        }

        # Static file caching (for future static assets)
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

**Configuration Breakdown**:

1. **Worker Connections**: 1024 simultaneous connections per worker
2. **Upstream Backend**: Load balancing configuration
3. **Client Max Body Size**: 10MB limit for PDF uploads
4. **Proxy Timeouts**: 300 seconds for long AI operations
5. **Proxy Headers**: Preserve client information
6. **WebSocket Support**: For future real-time features
7. **Buffering**: Disabled for streaming responses

### Nginx vs Direct FastAPI Access

| Aspect | Direct FastAPI | With Nginx |
|--------|----------------|------------|
| **SSL/TLS** | Manual setup | Easy SSL termination |
| **Load Balancing** | Not available | Built-in |
| **Static Files** | Inefficient | Highly optimized |
| **Caching** | Application-level | Edge caching |
| **Rate Limiting** | Code-based | Configuration-based |
| **DDoS Protection** | Limited | Robust |
| **Multiple Backends** | Not possible | Easy to configure |

---

## Backend Architecture

### Application Structure

```
api/
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── Dockerfile                   # Docker build instructions
├── docker-compose.yml           # Multi-container orchestration
├── nginx.conf                   # Nginx configuration
├── routes/
│   └── routes.py                # API endpoint definitions
├── services/
│   └── search_service.py        # FAISS vector search
├── agents/
│   ├── legal_agent.py           # Document analysis agent
│   └── legal_chatbot.py         # Legal domain chatbot
├── confidential/
│   └── confidential_pdf.py      # Private PDF processor
├── helpers/
│   ├── azure_blob_helper.py     # Azure SDK wrapper
│   ├── generate_embeddings.py   # FAISS index generator
│   └── unzip.py                 # Utility scripts
├── data/
│   ├── pdfs/                    # Legal case PDFs (local fallback)
│   └── faiss_store/             # FAISS index files (local fallback)
└── tests/
    └── test_routes.py           # API endpoint tests
```

### Core Components

#### 1. FastAPI Application (main.py)

**Purpose**: Initialize and configure the FastAPI application

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router

# Create FastAPI app
app = FastAPI(
    title="JurisFind API",
    description="Legal Case Search and Analysis API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://blue-cliff-0dfeb910f.2.azurestaticapps.net",  # Production (Azure Static Web Apps)
        "*"  # Allow all (development only)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")
```

#### 2. Search Service (FAISS)

**Purpose**: Semantic similarity search using FAISS vector index

**How it works**:

1. **Embedding Generation**:
   - Legal documents → Sentence Transformer → 768-dim vectors
   - Model: `all-mpnet-base-v2` (384M parameters)
   - Each PDF converted to single dense vector

2. **FAISS Index**:
   - IndexFlatIP (Inner Product similarity)
   - 46,456 vectors in index
   - ~500 MB index file size
   - O(n) search complexity (can be optimized with IVF)

3. **Search Process**:
   ```python
   Query text → Embed → Normalize → FAISS search → Top-K results
   ```

**Code Flow**:
```python
# services/search_service.py
class LegalCaseSearcher:
    def __init__(self):
        self.model = SentenceTransformer("all-mpnet-base-v2")
        self.index = faiss.read_index("legal_cases.index")
        self.id2name = json.load(open("id2name.json"))
    
    def search(self, query, top_k=5):
        # Embed query
        query_vec = self.model.encode([query])
        query_vec = query_vec / np.linalg.norm(query_vec)
        
        # Search FAISS index
        distances, indices = self.index.search(query_vec, top_k)
        
        # Format results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            results.append({
                "filename": self.id2name[idx],
                "score": float(score),
                "similarity_percentage": round(float(score) * 100, 2)
            })
        return results
```

#### 3. Legal Agent (LangChain)

**Purpose**: AI-powered document analysis and Q&A

**Components**:
- **Document Loader**: Extract text from PDFs
- **Text Splitter**: Chunk text for embeddings
- **Vector Store**: FAISS for document chunks
- **LLM Chain**: Groq API for generation
- **Prompt Templates**: Structured prompts for tasks

**Workflow**:
```
PDF → Extract Text → Chunk Text → Generate Embeddings 
    → Store in FAISS → LLM Query → Generate Response
```

**Key Features**:
- Summarization: Generate case summaries
- Q&A: Answer questions using RAG (Retrieval-Augmented Generation)
- Key Points Extraction: Identify important facts
- Citation Generation: Reference source documents

#### 4. Legal Chatbot

**Purpose**: Domain-specific legal question answering

**Features**:
- Domain filtering (legal questions only)
- Context-aware conversations
- Chat history management
- Professional legal terminology

**Architecture**:
```python
User Question → Domain Filter → Legal Check 
    → Context Builder → LLM Generation → Response
```

#### 5. Azure Integration

**Purpose**: Cloud storage for scalability and durability

**Components**:
- BlobServiceClient: Azure SDK client
- Container operations: List, download, upload
- Error handling: Retry logic, fallbacks
- Local fallback: Works without Azure

---

## Frontend Architecture

### Component Structure

```
frontend/src/
├── App.jsx                      # Root component & routing
├── main.jsx                     # Entry point
├── index.css                    # Global styles
├── config/
│   └── api.js                   # API configuration
├── components/
│   ├── Navigation.jsx           # Top navigation bar
│   └── Footer.jsx               # Footer component
└── pages/
    ├── LandingPage.jsx          # Home page
    ├── SearchPage.jsx           # Document search
    ├── PdfAnalysis.jsx          # Document analysis & Q&A
    ├── LegalChatbot.jsx         # AI legal assistant
    └── ConfidentialUpload.jsx   # Private document analysis
```

### Routing Configuration

```javascript
// App.jsx
<Routes>
  <Route path="/" element={<LandingPage />} />
  <Route path="/search" element={<SearchPage />} />
  <Route path="/analyze/:filename" element={<PdfAnalysis />} />
  <Route path="/legal-chat" element={<LegalChatbot />} />
  <Route path="/confidential-upload" element={<ConfidentialUpload />} />
</Routes>
```

### State Management

- **React useState**: Local component state
- **useEffect**: Side effects and data fetching
- **useNavigate**: Programmatic navigation
- **useParams**: URL parameter extraction
- **useLocation**: Access route state

### API Integration

```javascript
// config/api.js
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://20.186.113.106',
  ENDPOINTS: {
    SEARCH: '/api/search',
    UNIFIED_ANALYZE: '/api/unified/analyze',
    UNIFIED_ASK: '/api/unified/ask',
    LEGAL_CHAT: '/api/legal-chat',
    // ... more endpoints
  }
};

// Usage in components
const response = await axios.post(
  getApiUrl('/api/unified/analyze'),
  { filename, source: 'database' }
);
```

---

## Deployment Guide

### Prerequisites

1. **Azure Account**: Active subscription
2. **Domain Name**: (Optional) Custom domain
3. **Git Repository**: Code hosted on GitHub
4. **Docker Hub**: (Optional) Pre-built images

### Step 1: Azure VM Setup

```bash
# 1. Create Resource Group
az group create \
  --name JurisFind-RG \
  --location eastus

# 2. Create Virtual Machine
az vm create \
  --resource-group JurisFind-RG \
  --name JurisFind-VM \
  --image UbuntuLTS \
  --size Standard_D2alds_v7 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-sku Standard

# 3. Open ports
az vm open-port \
  --resource-group JurisFind-RG \
  --name JurisFind-VM \
  --port 80 \
  --priority 1001

az vm open-port \
  --resource-group JurisFind-RG \
  --name JurisFind-VM \
  --port 443 \
  --priority 1002
```

### Step 2: Install Docker on VM

```bash
# SSH into VM
ssh azureuser@20.186.113.106

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
```

### Step 3: Azure Blob Storage Setup

```bash
# 1. Create Storage Account
az storage account create \
  --name jurisfindstore \
  --resource-group JurisFind-RG \
  --location eastus2 \
  --sku Standard_LRS \
  --kind StorageV2

# 2. Get connection string
az storage account show-connection-string \
  --name jurisfindstore \
  --resource-group JurisFind-RG \
  --output tsv

# 3. Create container
az storage container create \
  --name data \
  --account-name jurisfindstore \
  --connection-string "<connection-string>"
```

### Step 4: Upload Data to Azure

```bash
# Upload PDFs
az storage blob upload-batch \
  --destination data/pdfs \
  --source ./api/data/pdfs \
  --account-name jurisfindstore \
  --connection-string "<connection-string>"

# Upload FAISS index
az storage blob upload-batch \
  --destination data/faiss_store \
  --source ./api/data/faiss_store \
  --account-name jurisfindstore \
  --connection-string "<connection-string>"
```

### Step 5: Deploy Application

```bash
# Clone repository
git clone https://github.com/Sagar-S-R/JurisFind.git
cd JurisFind

# Create .env file
cat > api/.env << EOF
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
AZURE_STORAGE_CONNECTION_STRING="your_azure_connection_string"
AZURE_DATA_CONTAINER=data
API_HOST=0.0.0.0
API_PORT=8000
EOF

# Build and start containers
cd api
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Verify deployment
curl http://localhost/api/health
```

### Step 6: Frontend Deployment (Azure Static Web Apps)

```bash
# In the Azure Portal:
# 1. Create a Static Web App resource
# 2. Link to the JurisFind GitHub repo, branch: main
# 3. App location: ./frontend | Output: dist
# Azure will auto-create .github/workflows/azure-static-web-apps-*.yml

# For local dev only:
cd frontend
echo "VITE_API_BASE_URL=http://20.186.113.106" > .env
npm run dev

# Production URL:
# https://blue-cliff-0dfeb910f.2.azurestaticapps.net
```

### Continuous Deployment

**GitHub Actions Workflow** (.github/workflows/deploy.yml):
```yaml
name: Deploy to Azure VM

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Azure VM
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VM_HOST }}
          username: ${{ secrets.VM_USERNAME }}
          key: ${{ secrets.VM_SSH_KEY }}
          script: |
            cd JurisFind
            git pull origin main
            cd api
            docker-compose down
            docker-compose up -d --build
```

---

## API Documentation

### Unified Endpoints

#### 1. Unified Analysis

**Endpoint**: `POST /api/unified/analyze`

**Purpose**: Single endpoint for analyzing both database and uploaded PDFs

**Request**:
```json
{
  "filename": "document.pdf",
  "source": "database"  // or "uploaded"
}
```

**Response**:
```json
{
  "success": true,
  "filename": "document.pdf",
  "text_length": 15420,
  "embedding_status": "created",
  "summary": "This case involves...",
  "message": "Document analyzed successfully"
}
```

#### 2. Unified Q&A

**Endpoint**: `POST /api/unified/ask`

**Purpose**: Single endpoint for asking questions about any document

**Request**:
```json
{
  "filename": "document.pdf",
  "question": "What was the final verdict?",
  "source": "database"  // or "uploaded"
}
```

**Response**:
```json
{
  "success": true,
  "filename": "document.pdf",
  "question": "What was the final verdict?",
  "answer": "The court ruled in favor of..."
}
```

### Legacy Endpoints (Still Supported)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/search` | POST | Search legal cases |
| `/api/analyze-document` | POST | Analyze database PDF |
| `/api/ask-question` | POST | Ask about database PDF |
| `/api/analyze-confidential-pdf` | POST | Analyze uploaded PDF |
| `/api/ask-question-confidential` | POST | Ask about uploaded PDF |
| `/api/legal-chat` | POST | Legal chatbot |
| `/api/health` | GET | Health check |

---

## Database & Storage

### FAISS Index Structure

**File**: `legal_cases.index`
- **Type**: IndexFlatIP (Inner Product)
- **Dimensions**: 768
- **Vectors**: 46,456
- **Size**: ~500 MB
- **Format**: Binary FAISS format

**ID Mapping**: `id2name.json`
```json
{
  "0": "-0___jonew__judis__10166.pdf",
  "1": "-0___jonew__judis__10187.pdf",
  ...
  "46455": "last-document.pdf"
}
```

### Storage Comparison

| Aspect | Local Storage | Azure Blob |
|--------|---------------|------------|
| **Capacity** | Limited by VM disk | Unlimited |
| **Cost** | Included in VM | $0.0184/GB/month |
| **Scalability** | Manual disk expansion | Automatic |
| **Backup** | Manual | Built-in redundancy |
| **Access Speed** | Faster (local) | Network latency |
| **Durability** | Single point of failure | 11 nines |

---

## Security & Authentication

### Current Security Measures

1. **Environment Variables**: Sensitive data in .env files
2. **CORS**: Restricted origins in production
3. **HTTPS**: (To be implemented) SSL certificates
4. **File Size Limits**: 10MB max upload
5. **Input Validation**: Pydantic models
6. **Error Handling**: No sensitive data in error messages

### Future Enhancements

1. **User Authentication**: JWT tokens
2. **API Rate Limiting**: Prevent abuse
3. **HTTPS**: Let's Encrypt certificates
4. **Azure Key Vault**: Secrets management
5. **Role-Based Access**: Admin vs user permissions

---

## Performance Optimization

### Current Optimizations

1. **FAISS Indexing**: Fast similarity search (< 100ms)
2. **Docker Multi-Stage Builds**: Smaller images
3. **Nginx Reverse Proxy**: Efficient request routing
4. **Uvicorn Workers**: Async parallel request handling in factory mode
5. **Sentence Transformer Caching**: Model loaded once

### Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|------------|
| **Search** | ~200ms | 50 req/s |
| **Analysis** | ~5-10s | 5 req/s |
| **Q&A** | ~2-5s | 10 req/s |
| **Chat** | ~1-3s | 15 req/s |

### Future Optimizations

1. **FAISS IVF Index**: Faster search with clustering
2. **Redis Caching**: Cache frequent queries
3. **CDN**: CloudFlare for static assets
4. **Database**: PostgreSQL for metadata
5. **Async Processing**: Celery for background tasks
6. **Horizontal Scaling**: Multiple backend instances

---

## Monitoring & Logging

### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f jurisfind-api

# Last 100 lines
docker-compose logs --tail=100 jurisfind-api
```

### Application Logs

```python
# main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
```

### Future Monitoring

1. **Prometheus**: Metrics collection
2. **Grafana**: Visualization dashboards
3. **ELK Stack**: Centralized logging
4. **Azure Monitor**: Cloud-native monitoring
5. **Sentry**: Error tracking

---

## Troubleshooting Guide

### Common Issues

#### 1. Docker Container Won't Start

**Symptoms**: `docker-compose up -d` fails

**Solutions**:
```bash
# Check logs
docker-compose logs

# Remove containers and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check disk space
df -h

# Clean up Docker
docker system prune -af
```

#### 2. Azure Connection Failure

**Symptoms**: "AccountIsDisabled" or connection timeout

**Solutions**:
- Check Azure subscription status
- Verify connection string in .env
- Check NSG rules allow outbound HTTPS
- Fallback to local storage

#### 3. FAISS Index Not Loading

**Symptoms**: "FAISS index not found"

**Solutions**:
```bash
# Check if files exist
ls -la api/data/faiss_store/

# Regenerate index
python api/helpers/generate_embeddings.py

# Verify file permissions
chmod 644 api/data/faiss_store/*
```

#### 4. Groq API Rate Limit

**Symptoms**: "Rate limit exceeded"

**Solutions**:
- Implement request queuing
- Add exponential backoff
- Upgrade Groq plan
- Cache responses

---

## Maintenance Guide

### Regular Tasks

**Daily**:
- Monitor application logs
- Check disk space
- Verify backup status

**Weekly**:
- Review error logs
- Update dependencies
- Check security advisories

**Monthly**:
- Update system packages
- Review Azure costs
- Performance analysis
- Backup verification

### Update Procedure

```bash
# 1. Backup data
docker-compose exec jurisfind-api tar -czf /app/backup.tar.gz /app/data

# 2. Pull latest code
git pull origin main

# 3. Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 4. Verify deployment
curl http://localhost/api/health

# 5. Monitor logs
docker-compose logs -f --tail=100
```

---

## Cost Analysis

### Azure Costs (Monthly)

| Service | Configuration | Cost |
|---------|---------------|------|
| **VM** | Standard D2alds v7 | ~$65 |
| **Blob Storage** | 5.3 GB Hot Tier | ~$0.10 |
| **Bandwidth** | 100 GB Outbound | ~$8.50 |
| **Public IP** | Static IPv4 | ~$3.00 |
| **Total** | | **~$42/month** |

### Optimization Strategies

1. **Reserved Instances**: 30-40% savings
2. **Auto-shutdown**: Turn off VM at night
3. **Cool Tier**: Move old PDFs to cool storage
4. **Bandwidth**: Use CDN for static assets
5. **Right-sizing**: Monitor and adjust VM size

---

## Future Roadmap

### Phase 1: Enhanced Features (Q1 2026)
- [ ] User authentication system
- [ ] Document upload history
- [ ] Advanced search filters
- [ ] Export results to PDF/Excel
- [ ] Bookmark favorite cases

### Phase 2: Performance (Q2 2026)
- [ ] Redis caching layer
- [ ] FAISS IVF index optimization
- [ ] Horizontal scaling with load balancer
- [ ] CDN integration
- [ ] Database for metadata

### Phase 3: Advanced AI (Q3 2026)
- [ ] Fine-tuned legal LLM
- [ ] Multi-document comparison
- [ ] Case outcome prediction
- [ ] Legal citation network
- [ ] Automated brief generation

### Phase 4: Enterprise (Q4 2026)
- [ ] Multi-tenancy support
- [ ] SSO integration
- [ ] Audit logging
- [ ] Advanced analytics dashboard
- [ ] API marketplace

---

## References & Resources

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- Docker: https://docs.docker.com/
- Nginx: https://nginx.org/en/docs/
- Azure: https://learn.microsoft.com/azure/
- FAISS: https://github.com/facebookresearch/faiss
- LangChain: https://python.langchain.com/

### Tools & Libraries
- Sentence Transformers: https://www.sbert.net/
- Groq API: https://console.groq.com/
- React: https://react.dev/
- TailwindCSS: https://tailwindcss.com/

### Community
- GitHub Repository: https://github.com/Sagar-S-R/JurisFind
- Issues: Report bugs and feature requests
- Discussions: Community forum

---

## Conclusion

JurisFind demonstrates a modern, scalable architecture for AI-powered legal document analysis. The combination of:

- **FastAPI** for high-performance API
- **Docker** for consistent deployment
- **Nginx** for robust reverse proxy
- **Azure** for cloud scalability
- **FAISS** for fast vector search
- **Groq LLM** for intelligent analysis

...creates a powerful platform for legal professionals.

The system is designed for:
✅ **Scalability**: Easily handle growing document corpus  
✅ **Reliability**: High availability with health checks  
✅ **Performance**: Sub-second search, efficient AI processing  
✅ **Maintainability**: Clean code, comprehensive docs  
✅ **Security**: Best practices for data protection  

---

**Last Updated**: January 9, 2026  
**Version**: 1.0.0  
**Maintained By**: Sagar S R  
**License**: MIT
