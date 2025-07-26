# Legal Bolt API - Legal Case Search Service

A FastAPI-based API service for searching legal cases using semantic similarity with FAISS and sentence transformers.

## Project Structure

```
api/
├── main.py                   # Main server file with FastAPI app
├── routes.py                 # API route definitions with Pydantic models
├── search_service.py         # Search service with FAISS integration
├── generate_embeddings.py    # Standalone script to generate embeddings
├── requirements.txt          # Python dependencies
├── faiss_store/             # Generated FAISS index and metadata
│   ├── legal_cases.index    # FAISS index file
│   └── id2name.json         # File name mapping
└── pdfs/                    # PDF files directory
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Embeddings (First Time Setup)

Before running the server, you need to generate embeddings from your PDF files:

```bash
cd api
python generate_embeddings.py
```

This will:
- Extract text from all PDF files in the `pdfs/` directory
- Generate embeddings using sentence-transformers
- Create a FAISS index for fast similarity search
- Save the index and metadata to `faiss_store/`

### 3. Start the Server

```bash
cd api
python main.py
```

The server will start on `http://127.0.0.1:8000` by default.

## API Endpoints

### 1. Home/Documentation
- **GET** `/`
- Returns API information and available endpoints

### 2. Interactive API Documentation
- **GET** `/docs` - Swagger UI documentation
- **GET** `/redoc` - ReDoc documentation

### 3. Health Check
- **GET** `/api/health`
- Check service status and total indexed cases

### 4. Search Cases (POST)
- **POST** `/api/search`
- **Body**: JSON
```json
{
    "query": "Woman killed her daughter",
    "top_k": 5
}
```
- **Response**: JSON with similar cases and similarity scores

### 5. Search Cases (GET)
- **GET** `/api/search?q=your_query&top_k=5`
- Simple GET endpoint for search queries

### 6. Case Details
- **GET** `/api/case/{filename}`
- Get details about a specific case file

## Usage Examples

### Using curl:

```bash
# Health check
curl http://127.0.0.1:8000/api/health

# Search with POST
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "murder case", "top_k": 3}'

# Search with GET
curl "http://127.0.0.1:8000/api/search?q=murder%20case&top_k=3"

# Get case details
curl http://127.0.0.1:8000/api/case/case_filename.pdf

# Interactive API docs
curl http://127.0.0.1:8000/docs
```

### Using Python requests:

```python
import requests

# Search for cases
response = requests.post('http://127.0.0.1:8000/api/search', 
                        json={'query': 'murder case', 'top_k': 5})
results = response.json()
print(results)
```

### Using FastAPI's Interactive Documentation:

Visit `http://127.0.0.1:8000/docs` in your browser for:
- Interactive API testing
- Request/response schema documentation
- Try-it-out functionality

## Environment Variables

- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload during development (default: False)

## FastAPI Features

- **Automatic API Documentation**: Available at `/docs` and `/redoc`
- **Type Validation**: Automatic request/response validation with Pydantic
- **High Performance**: Built on Starlette and Uvicorn for fast async performance
- **OpenAPI Schema**: Automatic OpenAPI schema generation

## Response Format

### Search Response:
```json
{
    "success": true,
    "query": "murder case",
    "results": [
        {
            "filename": "case_001.pdf",
            "score": 0.8542,
            "similarity_percentage": 85.42
        }
    ],
    "total_results": 1
}
```

### Error Response:
```json
{
    "error": "Search failed",
    "message": "Detailed error message"
}
```

## Regenerating Embeddings

To update the search index with new PDF files:

1. Add new PDF files to the `pdfs/` directory
2. Run the embedding generation script:
```bash
python generate_embeddings.py
```
3. Restart the server to load the updated index

## Notes

- The service uses `sentence-transformers/all-mpnet-base-v2` model for embeddings
- FAISS IndexFlatIP is used for cosine similarity search
- PDF text extraction is done using PyMuPDF (fitz)
- Built with FastAPI for high performance and automatic documentation
- Pydantic models ensure type safety and validation
- CORS is enabled for web applications
- Interactive API documentation available at `/docs` and `/redoc`
