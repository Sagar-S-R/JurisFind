from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from routes.routes import router
except ImportError:
    import sys, os
    _API_DIR = os.path.abspath(os.path.dirname(__file__))
    if _API_DIR not in sys.path:
        sys.path.insert(0, _API_DIR)
    from routes.routes import router  # type: ignore
from pathlib import Path
from dotenv import load_dotenv
import os
import uvicorn

def create_app():
    """Create and configure the FastAPI app."""
    # Load env from api/.env early so imports downstream can see it
    _dotenv_path = Path(__file__).with_name('.env')
    try:
        load_dotenv(dotenv_path=_dotenv_path, override=False)
        groq = os.environ.get('GROQ_API_KEY', '')
        masked = (f"{groq[:4]}...{groq[-4:]}" if groq and len(groq) >= 8 else "(missing or too short)")
        print(f"Env loaded from: {_dotenv_path} | GROQ_API_KEY: {masked}")
    except Exception as _e:
        print(f"Warning: Could not load .env from {_dotenv_path}: {_e}")
    app = FastAPI(
        title="JurisFind API",
        description="Legal Case Search Service using semantic similarity",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Enable CORS for all routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # React dev server  
            "https://jurisfind.vercel.app",  # Production frontend
            "https://jurisfind.netlify.app",  # Alternative frontend
            "http://your-vm-public-ip",  # Your VM IP
            "*"  # Allow all for development (remove in production)
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router, prefix="/api")
    
    # Root route
    @app.get("/")
    async def home():
        storage_info = "Azure Blob Storage" if os.getenv("AZURE_STORAGE_CONNECTION_STRING") else "Local Files"
        
        return {
            'message': 'JurisFind API - Legal Case Search Service',
            'version': '2.0.0',
            'storage_backend': storage_info,
            'endpoints': {
                'health_check': '/api/health',
                'search_cases_post': '/api/search (POST)',
                'search_cases_get': '/api/search?q=your_query&top_k=5 (GET)',
                'case_details': '/api/case/{filename}',
                'pdf_files': '/api/pdf/{filename}',
                'list_pdfs': '/api/list-pdfs',
                'upload_pdf_azure': '/api/upload-pdf-to-azure (POST)',
                'generate_embeddings': '/api/generate-embeddings-from-azure (POST)',
                'confidential_upload': '/api/upload-confidential-pdf (POST)',
                'confidential_retrieve': '/api/retrieve-similar-cases (POST)',
                'confidential_analyze': '/api/analyze-document (POST)',
                'confidential_question': '/api/ask-question (POST)',
                'docs': '/docs',
                'redoc': '/redoc'
            },
            'documentation': {
                'search_post': 'Send POST request with JSON: {"query": "your search query", "top_k": 5}',
                'search_get': 'Send GET request with query parameter: ?q=your_query&top_k=5',
                'case_details': 'Get details about a specific case file',
                'pdf_files': 'Serve PDF files from Azure Blob Storage or local storage',
                'list_pdfs': 'List all available PDF files',
                'upload_pdf_azure': 'Upload PDF files to Azure Blob Storage',
                'generate_embeddings': 'Generate FAISS embeddings from Azure PDFs',
                'health': 'Check service health and total number of indexed cases',
                'interactive_docs': 'Visit /docs for interactive API documentation'
            },
            'azure_features': {
                'enabled': bool(os.getenv("AZURE_STORAGE_CONNECTION_STRING")),
                'container': os.getenv("AZURE_DATA_CONTAINER", "data"),
                'pdf_storage': 'pdfs/ directory in Azure container',
                'index_storage': 'faiss_store/ directory in Azure container'
            }
        }
    
    return app

def main():
    """Main function to run the FastAPI server."""
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '127.0.0.1')
    reload = os.environ.get('RELOAD', 'False').lower() == 'true'
    
    print("=" * 50)
    print("🚀 Starting JurisFind FastAPI Server")
    print("=" * 50)
    print(f"📍 Server running on: http://{host}:{port}")
    print(f"🔍 API endpoints available at: http://{host}:{port}/api")
    print(f"📚 Interactive docs at: http://{host}:{port}/docs")
    print(f"📖 ReDoc docs at: http://{host}:{port}/redoc")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:create_app",
            factory=True,
            host=host,
            port=port,
            reload=reload
        )
    except KeyboardInterrupt:
        print("\n👋 Server shutting down...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == '__main__':
    main()
