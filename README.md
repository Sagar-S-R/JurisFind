# Legal Bolt - Agentic AI Legal Document Analysis

A comprehensive full-stack agentic AI application for legal document analysis using advanced AI agents, LangChain, and Groq. The system provides semantic search, intelligent document summarization, and context-aware question-answering capabilities for legal documents.

## 🚀 Key Features

### Agentic AI Architecture
- **LangChain Integration**: Advanced prompt engineering and chain-based processing
- **Groq AI Models**: Powered by `llama3-70b-8192` for superior legal analysis
- **Intelligent Agents**: Context-aware document analysis with memory management
- **Temporary Embeddings**: Dynamic vector stores for individual document analysis

### Frontend (React + Router)
- **Multi-Page Application**: Search interface and dedicated PDF analysis pages
- **Real-time AI Interaction**: Instant document summarization and Q&A
- **Professional Design**: Clean, responsive interface optimized for legal professionals
- **Smart Navigation**: Seamless routing between search and analysis workflows

### Backend (FastAPI + AI Agents)
- **Agentic Architecture**: Intelligent document processing with LangChain agents
- **PDF Processing**: Advanced text extraction with PyMuPDF
- **Vector Search**: Semantic similarity search using FAISS
- **AI Summarization**: Comprehensive document analysis using Groq AI
- **Context-aware Q&A**: Intelligent question answering with document-specific embeddings

## Features

### Core Agentic AI Functionality
- **Document Ingestion**: Intelligent PDF processing with text extraction
- **Semantic Search**: FAISS-powered similarity search with relevance scoring
- **AI Agent Analysis**: Complete document analysis using LangChain agents
- **Dynamic Summarization**: Context-aware summaries using Groq's llama3-70b-8192
- **Interactive Q&A**: Document-specific question answering with temporary embeddings
- **Memory Management**: Efficient cleanup of temporary vector stores

### Advanced Features
- **Prompt Engineering**: Sophisticated prompt templates for legal analysis
- **Chain Processing**: LangChain-based document processing pipelines
- **Multi-Modal Interface**: Search page + dedicated analysis pages
- **Real-time Processing**: Live document analysis with progress tracking
- **Error Handling**: Comprehensive error management and user feedback
- **API Documentation**: Automatic OpenAPI documentation with agent endpoints

## Quick Start

### Prerequisites
- Node.js 16+ 
- Python 3.9+
- Groq API Key (Get from: https://console.groq.com/keys)
- Git

### 1. Setup Backend Environment
```bash
# Navigate to api directory
cd api

# Create conda environment with Python 3.9 (if not exists)
conda create -p ./venv python=3.9
conda activate ./venv

# Install Python dependencies (includes LangChain + Groq)
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 2. Setup Frontend
```bash
# Navigate back to root and install React dependencies
cd ..
npm install

# Start development server (includes React Router)
npm run dev
```
The frontend will be available at `http://localhost:5173`

### 3. Start the Agentic AI Backend
```bash
# In the api directory
cd api
python main.py
```
The backend will be available at `http://localhost:8000`

## API Endpoints

### Health & Status
- **GET** `/api/health` - Check system status and document count

### Traditional Search
- **POST** `/api/search` - Semantic search with FAISS similarity scoring
- **GET** `/api/pdf/{filename}` - Serve PDF files directly

### Agentic AI Endpoints
- **POST** `/api/analyze-document?filename={filename}` - Complete AI document analysis
- **POST** `/api/ask-question` - Context-aware Q&A with document embeddings
- **GET** `/api/document-stats/{filename}` - Get embedding statistics
- **DELETE** `/api/cleanup-embeddings/{filename}` - Clean up temporary embeddings

### Document Management
- **GET** `/api/case/{filename}` - Get case details and metadata

## Usage Workflow

### 1. Document Search
- Navigate to the main search page (`/`)
- Enter legal queries or topics in the search interface
- View ranked results with similarity percentages and scores
- Access document metadata and download options

### 2. AI-Powered Document Analysis
- Click "AI Analysis" on any search result
- Navigate to the dedicated analysis page (`/analyze/{filename}`)
- View comprehensive AI-generated summary covering:
  - Document type and overview
  - Key parties involved
  - Main legal issues
  - Key facts and legal principles
  - Conclusions and significance

### 3. Interactive Q&A with Document Context
- Use the Q&A panel on the analysis page
- Ask specific questions about the document
- Get context-aware answers based on document embeddings
- Use quick question templates or ask custom questions
- Maintain conversation context for the session

### 4. Memory Management
- View document statistics (chunk count, embedding dimensions)
- Clean up temporary embeddings when done
- Efficient resource management for multiple documents

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
Legal_Bolt/
├── src/                          # Frontend React application
│   ├── App.jsx                   # Main app with React Router
│   ├── main.jsx                  # Application entry point
│   ├── index.css                 # Global styles
│   ├── pages/                    # React pages
│   │   ├── SearchPage.jsx        # Main search interface
│   │   └── PdfAnalysis.jsx       # AI document analysis page
│   ├── components/               # Reusable React components
│   └── utils/                    # Utility functions
├── api/                          # Backend FastAPI application
│   ├── main.py                   # FastAPI app entry point
│   ├── routes.py                 # All API endpoints
│   ├── legal_agent.py            # LangChain AI agent (CORE)
│   ├── search_service.py         # Vector search operations
│   ├── generate_embeddings.py    # PDF processing & embedding generation
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Environment variables (Groq API key)
│   ├── .env.example              # Environment template
│   ├── pdfs/                     # PDF documents
│   └── faiss_store/              # Pre-generated embeddings
│       ├── legal_cases.index     # FAISS index file
│       └── id2name.json          # Document metadata
├── package.json                  # Frontend dependencies
├── vite.config.ts                # Vite configuration
├── tailwind.config.js            # Tailwind CSS configuration
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

### AI Model Configuration
The application uses optimized models for legal document analysis:

- **Embeddings**: `sentence-transformers/all-mpnet-base-v2` (High-quality embeddings)
- **Language Model**: `llama3-70b-8192` via Groq (Fast, powerful legal analysis)
- **Text Chunking**: 1000 character chunks with 200 character overlap
- **Vector Search**: FAISS with cosine similarity

### Frontend Configuration
- **React Router**: Handles navigation between search and analysis pages
- **API Base URL**: Configured for `http://localhost:8000/api`
- **Responsive Design**: Optimized for desktop and mobile use

## Development

### Adding New Features
1. **Backend AI Agents**: Extend `legal_agent.py` with new LangChain chains
2. **Frontend Pages**: Add new routes in `App.jsx` and create page components
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
6. **CORS Errors**: Ensure backend is running on port 8000 and frontend on 5173

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

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review console logs for detailed error messages
3. Ensure all dependencies are properly installed