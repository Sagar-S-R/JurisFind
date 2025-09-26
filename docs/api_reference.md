# API Reference

## Overview

Legal Case provides a REST API built with FastAPI. Interactive documentation available at `/docs` when running locally.

## Base URL
```
http://localhost:8000/api
```

## Endpoints

### Health Check
- **GET** `/health`
- **Response**: `{"status": "healthy"}`

### Search
- **POST** `/search`
- **Body**:
  ```json
  {
    "query": "contract terms",
    "top_k": 5
  }
  ```
- **Response**: Array of search results with scores and metadata

### Document Analysis
- **POST** `/analyze`
- **Body**:
  ```json
  {
    "filename": "document.pdf",
    "query": "summarize key points"
  }
  ```
- **Response**: AI-generated analysis

### Chat
- **POST** `/chat`
- **Body**:
  ```json
  {
    "message": "What are the main arguments?",
    "context": "document.pdf"
  }
  ```
- **Response**: Conversational response

### Document Statistics
- **GET** `/document-stats/{filename}`
- **Response**: Document metadata and statistics

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

- Default: 100 requests per minute per IP
- Configurable in environment variables

## CORS

Configured to allow requests from frontend origin.