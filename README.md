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
- [Architecture](docs/architecture.md)
- [Quick Start](docs/installation.md)
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

Legal Bolt uses a microservices architecture with React frontend, FastAPI backend, and AI services. See [architecture.md](docs/architecture.md) for detailed system design and data flow.

## 🚀 Quick Start

Get started quickly with Legal Bolt. See [installation.md](docs/installation.md) for detailed setup instructions.

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

**JurisFind** - Empowering Legal Professionals with AI


[![GitHub stars](https://img.shields.io/github/stars/your-repo/legal-bolt?style=social)](https://github.com/your-repo/legal-bolt)
[![GitHub forks](https://img.shields.io/github/forks/your-repo/legal-bolt?style=social)](https://github.com/your-repo/legal-bolt)
[![GitHub issues](https://img.shields.io/github/issues/your-repo/legal-bolt)](https://github.com/your-repo/legal-bolt/issues)

</div>
