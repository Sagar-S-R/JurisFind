# Ingestion Pipeline

## Overview

The ingestion pipeline processes PDF documents into searchable vector embeddings stored in FAISS.

## Process Flow

```
PDF Document → Text Extraction → Text Chunking → Embedding Generation → FAISS Index
```

## Text Extraction

- **Library**: PyMuPDF (fitz)
- **Input**: PDF files from `pdfs/` directory
- **Output**: Plain text content
- **Error Handling**: Graceful failure for corrupted PDFs

## Text Chunking

- **Strategy**: Fixed-size chunks with overlap
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Purpose**: Maintain context across chunks

## Embedding Generation

- **Model**: sentence-transformers/all-MiniLM-L6-v2
- **Input**: Text chunks
- **Output**: 384-dimensional vectors
- **Batch Processing**: Process multiple chunks efficiently

## Vector Storage

- **Database**: FAISS (Facebook AI Similarity Search)
- **Index Type**: IndexFlatIP (inner product)
- **Persistence**: Saved to `faiss_store/legal_cases.index`
- **Metadata**: ID-to-filename mapping in JSON

## Configuration

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
INDEX_PATH = "faiss_store/legal_cases.index"
```

## Usage

```bash
# Run ingestion
python helpers/generate_embeddings.py

# Output: FAISS index and metadata files
```