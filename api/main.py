from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import os
import uvicorn

def create_app():
    """Create and configure the FastAPI app."""
    app = FastAPI(
        title="LegalSearch API",
        description="Legal Case Search Service using semantic similarity",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Enable CORS for all routes
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(router, prefix="/api")
    
    # Root route
    @app.get("/")
    async def home():
        return {
            'message': 'LegalSearch API - Legal Case Search Service',
            'version': '1.0.0',
            'endpoints': {
                'health_check': '/api/health',
                'search_cases_post': '/api/search (POST)',
                'search_cases_get': '/api/search?q=your_query&top_k=5 (GET)',
                'case_details': '/api/case/{filename}',
                'docs': '/docs',
                'redoc': '/redoc'
            },
            'documentation': {
                'search_post': 'Send POST request with JSON: {"query": "your search query", "top_k": 5}',
                'search_get': 'Send GET request with query parameter: ?q=your_query&top_k=5',
                'case_details': 'Get details about a specific case file',
                'health': 'Check service health and total number of indexed cases',
                'interactive_docs': 'Visit /docs for interactive API documentation'
            }
        }
    
    return app

def main():
    """Main function to run the FastAPI server."""
    app = create_app()
    
    # Get configuration from environment variables
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '127.0.0.1')
    reload = os.environ.get('RELOAD', 'False').lower() == 'true'
    
    print("=" * 50)
    print("🚀 Starting LegalSearch FastAPI Server")
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
