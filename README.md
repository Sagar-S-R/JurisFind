# JurisFind - AI-Powered Legal Document Analysis

<div align="center">

![JurisFind Logo](https://img.shields.io/badge/JurisFind-AI%20Legal%20Search-blue?style=for-the-badge&logo=law)

**A comprehensive full-stack AI application for legal document analysis with Azure Blob Storage integration**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=white)](https://reactjs.org/)
[![Azure](https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/)
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white)](https://langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-AI%20Inference-00D4AA?style=flat&logo=groq&logoColor=white)](https://groq.com/)

</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features) 
- [Azure Integration](#azure-integration)
- [Architecture](docs/architecture.md)
- [Quick Start](#quick-start)
- [Azure Setup](docs/azure_integration.md)
- [API Documentation](docs/api_reference.md)
- [Ingestion Pipeline](docs/ingestion_pipeline.md)
- [Query Pipeline](docs/query_pipeline.md)
- [Deployment](docs/deployment.md)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [Development Guide](#development-guide)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

**JurisFind** is a state-of-the-art AI application designed for legal document analysis and search. Built with modern cloud-native architecture, it leverages Azure Blob Storage for scalable document management and advanced AI for semantic understanding of legal content.

### What Makes JurisFind Special?

- **Cloud-Native Architecture**: Full Azure Blob Storage integration for unlimited document storage
- **AI-Powered Analysis**: Intelligent document processing using LangChain and Groq AI
- **Lightning-Fast Search**: FAISS-powered semantic search that understands legal concepts
- **Modern UI**: Clean, responsive React interface for seamless user experience
- **Secure & Scalable**: Enterprise-ready with proper authentication and cloud security
- **Developer-Friendly**: Comprehensive APIs and management tools for easy integration

### Target Users

- **Legal Professionals**: Attorneys, paralegals, and legal researchers seeking efficient document analysis
- **Law Students**: Academic researchers and students studying legal precedents and case law
- **Legal Tech Teams**: Developers building legal technology solutions
- **Compliance Teams**: Organizations needing to analyze legal documents for compliance purposes

## Azure Integration

**Enterprise-Grade Cloud Storage**

JurisFind features comprehensive Azure Blob Storage integration for scalable, secure document management:

- **Cloud Document Storage**: Store thousands of legal documents in Azure Blob Storage
- **Automatic Sync**: Seamless synchronization between local development and cloud production
- **Fast Indexing**: Generate FAISS embeddings directly from Azure-stored PDFs
- **Global Access**: Access documents from anywhere with Azure's global infrastructure
- **Enterprise Security**: Azure's enterprise-grade security and compliance features

### Azure Features

- **Scalable Storage**: Handle millions of documents without local storage constraints
- **Cost-Effective**: Pay only for storage used with Azure's flexible pricing tiers
- **Backup & Recovery**: Built-in redundancy and disaster recovery capabilities
- **API Integration**: RESTful APIs for document upload, download, and management
- **Hybrid Deployment**: Works with both local files (development) and Azure (production)

### Quick Azure Setup

```bash
# 1. Run the Azure setup script
cd api
python setup_azure.py

# 2. Upload your PDFs to Azure
python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs

# 3. Generate FAISS index from Azure PDFs
python helpers/azure_data_manager.py generate-index

# 4. Test the integration
python tests/test_azure_integration.py
```

See [Azure Integration Guide](docs/azure_integration.md) for complete setup instructions.

## Key Features

### Agentic AI Architecture

**Intelligent Document Processing**
- **LangChain Integration**: Advanced prompt engineering and chain-based processing that enables complex reasoning workflows
- **Groq AI Models**: Powered by `llama3-70b-8192` for superior legal analysis with industry-leading inference speed
- **Intelligent Agents**: Context-aware document analysis with sophisticated memory management and reasoning capabilities
- **Temporary Embeddings**: Dynamic vector stores created for each document analysis session, ensuring isolated and secure processing

**Why Agentic AI?**
Unlike traditional document analysis tools, JurisFind uses AI agents that can:
- Plan multi-step analysis workflows
- Reason about document structure and legal concepts
- Maintain context across complex queries
- Adapt their approach based on document type and user needs

### Frontend (React + Router)

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

##  Architecture

JurisFind uses a microservices architecture with React frontend, FastAPI backend, and AI services. See [architecture.md](docs/architecture.md) for detailed system design and data flow.

##  Quick Start

Get started quickly with JurisFind. See [installation.md](docs/installation.md) for detailed setup instructions.

### Prerequisites

- Node.js 16+
- Python 3.9+
- Groq API key

### Basic Setup

```bash
git clone <repository-url>
cd Legal_Case
# Follow installation guide
```

## API Documentation

Complete API reference and endpoints. See [api_reference.md](docs/api_reference.md) for detailed specifications.

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

### Cloud & Storage
- **Azure Blob Storage**: Enterprise cloud document storage
- **Azure SDK**: Python SDK for Azure integration
- **Azure Identity**: Authentication and access management

### AI Models & Services
- **Embeddings**: `sentence-transformers/all-mpnet-base-v2`
- **Language Model**: `llama3-70b-8192` via Groq API
- **Vector Store**: FAISS for similarity search
- **Text Splitting**: Recursive character text splitter for chunking

##  Quick Start

### Option 1: Azure Cloud Setup (Recommended for Production)

```bash
# 1. Clone repository
git clone https://github.com/your-username/JurisFind.git
cd JurisFind

# 2. Setup backend with Azure
cd api
pip install -r requirements.txt
python setup_azure.py  # Interactive Azure setup

# 3. Upload PDFs and generate index
python helpers/azure_data_manager.py upload-pdfs --pdf-dir ./data/pdfs
python helpers/azure_data_manager.py generate-index

# 4. Start backend
python main.py

# 5. Setup frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

### Option 2: Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/JurisFind.git
cd JurisFind

# 2. Setup backend
cd api
pip install -r requirements.txt
python helpers/generate_embeddings.py  # Generate local FAISS index
python main.py

# 3. Setup frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

### Environment Configuration

Create `api/.env`:
```env
# Azure Blob Storage (for cloud setup)
AZURE_STORAGE_CONNECTION_STRING="your_azure_connection_string"
AZURE_DATA_CONTAINER="data"

# AI Configuration
GROQ_API_KEY="your_groq_api_key"
GROQ_MODEL="llama3-70b-8192"

# API Configuration
API_HOST="localhost"
API_PORT="8000"
```

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

##  Security & Privacy

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

## Contributing

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
-  Commercial use allowed
-  Modification allowed
-  Distribution allowed
-  Private use allowed
-  No warranty provided
-  No liability assumed


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



