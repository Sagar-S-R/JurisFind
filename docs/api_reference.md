# API Reference

## Overview

JurisFind provides a REST API built with FastAPI. Interactive documentation available at `/docs` when running locally or in production.

## Base URL

Local development:
```
http://localhost:8000/api
```

Production:
```
http://20.186.113.106/api
```

Interactive Swagger UI (production): `http://20.186.113.106/docs`
Interactive Swagger UI (local): `http://localhost:8000/docs`

## Endpoints

### Health Check
- **GET** `/health`
- **Response**:
  ```json
  {"status": "healthy", "message": "Legal case search service is running", "total_cases": 46456}
  ```

### Search
- **POST** `/search`
- **Body**:
  ```json
  {"query": "breach of contract", "top_k": 5}
  ```
- **Response**:
  ```json
  {
    "success": true,
    "query": "breach of contract",
    "results": [
      {"filename": "case_001.pdf", "score": 0.94, "similarity_percentage": 94.3}
    ],
    "total_results": 5
  }
  ```

### Unified Document Analysis
- **POST** `/unified/analyze`
- **Body**:
  ```json
  {"filename": "case_001.pdf", "source": "database"}
  ```
  `source` is `"database"` for PDFs from the main index or `"uploaded"` for a confidential upload.
- **Response**: `{success, filename, text_length, embedding_status, summary, message}`

### Unified Document Q&A
- **POST** `/unified/ask`
- **Body**:
  ```json
  {"filename": "case_001.pdf", "question": "What was the ruling?", "source": "database"}
  ```
- **Response**: `{success, filename, question, answer}`

### Serve PDF
- **GET** `/pdf/{filename}`
- **Response**: PDF binary stream (`application/pdf`). Downloads from Azure Blob Storage, or falls back to local `api/data/pdfs/`.

### Document Statistics
- **GET** `/document-stats/{filename}`
- **Response**: `{success, filename, stats}` with embedding metadata for the analyzed document.

### Upload Confidential PDF
- **POST** `/upload-confidential-pdf`
- **Body**: `multipart/form-data` with a `file` field containing the PDF
- **Response**: `{success, filename, message}`
- The file is saved to the ephemeral `confidential_tmp` Docker volume and never reaches Blob Storage.

### Retrieve Similar Cases
- **POST** `/retrieve-similar-cases?filename={name}&top_k=5`
- Finds cases in the main FAISS index semantically similar to the uploaded confidential PDF.
- **Response**: `{success, filename, similar_cases, total_found}`

### Cleanup Confidential Session
- **DELETE** `/cleanup-confidential/{filename}`
- **Response**: `{success, message}` — deletes the uploaded PDF and its embeddings.

### Legal Chatbot
- **POST** `/legal-chat`
- **Body**:
  ```json
  {"question": "What constitutes fair use under copyright law?"}
  ```
- **Response**: `{success, response, is_legal, domain_filtered}`
  - `is_legal`: `false` if the question was detected as non-legal and filtered.

### Additional Utility Endpoints
- **GET** `/list-pdfs` — list all available PDFs in Blob or local storage
- **POST** `/analyze-document?filename={name}` — analyze a single database PDF (legacy route)
- **POST** `/ask-question` `{filename, question}` — Q&A on a database PDF (legacy route)
- **DELETE** `/cleanup-embeddings/{filename}` — remove cached embeddings for a document
- **DELETE** `/legal-chat/clear` — reset chatbot conversation history
- **GET** `/legal-chat/stats` — chatbot session statistics
- **POST** `/upload-pdf-to-azure` `multipart/form-data` — upload a PDF to Blob Storage directly
- **POST** `/generate-embeddings-from-azure` — rebuild FAISS index from Blob PDFs (admin operation)

## Authentication

Currently no authentication required. For production, implement API keys.

## Error Handling

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses include:
```json
{
  "detail": "Error description"
}
```

## Rate Limiting

Nginx enforces 30 requests per minute per IP by default. Requests exceeding this limit receive HTTP 429. The limit is configured in `nginx.conf` and can be adjusted on the VM.

## CORS

Configured to allow requests from frontend origin.