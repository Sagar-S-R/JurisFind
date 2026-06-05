"""
Embedding Service — single consolidated SentenceTransformer wrapper.

Replaces the duplicate embedding code that existed in both:
  - legal_agent.py (via LangChain HuggingFaceEmbeddings)
  - document_processing_service.py (direct SentenceTransformer)

Both now import from here.

Model: sentence-transformers/all-mpnet-base-v2 (768-dim, L2-normalized output)
"""
import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
_EMBEDDING_DIM = 768
_model: Optional[SentenceTransformer] = None


def get_model() -> SentenceTransformer:
    """Lazy-load the model once per process."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
        logger.info("Embedding model loaded (%d-dim).", _EMBEDDING_DIM)
    return _model


def embed_texts(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Encode a list of strings into 768-dim float32 vectors.

    Returns np.ndarray of shape (N, 768).
    Vectors are NOT normalised here — normalisation is done at storage time
    by pgvector when using cosine distance operators.
    """
    model = get_model()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )
    return vectors.astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    """
    Encode a single query string into a 768-dim float32 vector.

    Returns np.ndarray of shape (768,).
    """
    return embed_texts([text])[0]


EMBEDDING_DIM = _EMBEDDING_DIM
