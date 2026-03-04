# Query Pipeline

## Overview

The query pipeline processes user search queries through embedding, similarity search, and AI response generation.

## Process Flow

```
User Query → Query Embedding → FAISS Search → Context Retrieval → AI Response
```

## Query Processing

- **Input**: Natural language search query
- **Preprocessing**: Basic cleaning and normalization
- **Embedding**: Same model as ingestion (`all-mpnet-base-v2`)
- **Output**: Query vector

## Similarity Search

- **Algorithm**: Cosine similarity via FAISS
- **Top-K**: Return top 5 most similar chunks
- **Threshold**: No strict cutoff, rank by similarity
- **Metadata**: Retrieve document filenames for results

## Context Retrieval

- **Input**: Top-K similar chunks
- **Aggregation**: Combine relevant text segments
- **Limit**: Maximum context length for LLM
- **Ranking**: Prioritize higher similarity scores

## AI Response Generation

- **Model**: Groq `llama-3.3-70b-versatile`
- **Prompt Engineering**: Legal-specific templates
- **Context Injection**: Retrieved chunks as context
- **Response Format**: Natural language with citations

## LangChain Integration

- **Chains**: Sequential processing pipeline
- **Memory**: Conversation context for follow-up queries
- **Agents**: Intelligent routing and reasoning
- **Templates**: Structured prompts for legal analysis

## Configuration

```python
TOP_K_RESULTS = 5
MAX_CONTEXT_LENGTH = 4000
LLM_MODEL = "llama-3.3-70b-versatile"
TEMPERATURE = 0.1
```

## API Endpoints

- `POST /api/search`: Semantic search
- `POST /api/unified/analyze`: Document analysis (database or uploaded PDF)
- `POST /api/unified/ask`: Conversational Q&A on an analyzed document
- `POST /api/legal-chat`: Legal domain chatbot