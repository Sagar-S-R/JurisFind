"""
FAISS vector store service for JurisFind.

Wraps a FAISS IndexFlatIP (inner product = cosine similarity on normalized vectors)
for 768-dimensional embeddings matching the all-mpnet-base-v2 model output.

Thread-safe for concurrent reads; uses a threading.Lock for mutations.
This is a singleton in-memory store — suitable for single-instance deployments.
"""

import threading
import uuid
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False


EMBEDDING_DIM = 768  # all-mpnet-base-v2 output dimension


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""
    pass


class VectorStoreService:
    """
    In-memory FAISS vector store for document chunk embeddings.

    Uses IndexFlatIP (inner product) with L2-normalized vectors so that
    inner product == cosine similarity.

    Maintains a bidirectional mapping:
      - embedding_reference (str UUID) → FAISS internal integer ID
      - FAISS internal ID → embedding_reference

    This allows us to:
    1. Add embeddings and tag them with a string reference
    2. Retrieve top-k similar chunks by cosine similarity
    3. Remove embeddings by their string reference
    """

    def __init__(self, dim: int = EMBEDDING_DIM):
        if not _FAISS_AVAILABLE:
            raise VectorStoreError(
                "faiss-cpu is not installed. Run: pip install faiss-cpu"
            )

        self._dim = dim
        self._lock = threading.Lock()

        # FAISS index: IndexIDMap wraps IndexFlatIP so we can use custom int IDs
        flat_index = faiss.IndexFlatIP(dim)
        self._index = faiss.IndexIDMap(flat_index)

        # Mapping: string embedding_reference → int64 FAISS ID
        self._ref_to_id: Dict[str, int] = {}
        # Reverse mapping: int64 FAISS ID → string embedding_reference
        self._id_to_ref: Dict[int, str] = {}

        # Counter for generating unique int64 IDs (FAISS requires int64)
        self._next_id: int = 0

    # ── Internal helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        """L2-normalize vectors so that inner product == cosine similarity."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)  # prevent division by zero
        return vectors / norms

    def _allocate_ids(self, n: int) -> np.ndarray:
        """Allocate n sequential int64 IDs for FAISS."""
        start = self._next_id
        self._next_id += n
        return np.arange(start, start + n, dtype=np.int64)

    # ── Public API ───────────────────────────────────────────────────────────

    def add_embeddings(
        self,
        embedding_refs: List[str],
        vectors: np.ndarray,
    ) -> None:
        """
        Add embeddings to the vector store.

        Args:
            embedding_refs: List of unique string references (UUID strings)
            vectors: numpy array of shape (N, 768) in float32

        Raises:
            VectorStoreError: If dimensions mismatch or refs already exist
        """
        if len(embedding_refs) != len(vectors):
            raise VectorStoreError(
                f"Mismatch: {len(embedding_refs)} refs vs {len(vectors)} vectors"
            )
        if vectors.ndim != 2 or vectors.shape[1] != self._dim:
            raise VectorStoreError(
                f"Expected shape (N, {self._dim}), got {vectors.shape}"
            )

        vectors = vectors.astype(np.float32)
        normalized = self._normalize(vectors)

        with self._lock:
            ids = self._allocate_ids(len(embedding_refs))
            self._index.add_with_ids(normalized, ids)
            for ref, faiss_id in zip(embedding_refs, ids.tolist()):
                self._ref_to_id[ref] = faiss_id
                self._id_to_ref[faiss_id] = ref

    def search_similar(
        self,
        query_vector: np.ndarray,
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Find the top-k most similar chunks by cosine similarity.

        Args:
            query_vector: 1-D numpy array of shape (768,) in float32
            k: Number of results to return (default 5)

        Returns:
            List of (embedding_reference, cosine_similarity_score) tuples,
            sorted by descending similarity. Score is in [-1, 1].

        Raises:
            VectorStoreError: On dimension mismatch
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        if query_vector.shape[1] != self._dim:
            raise VectorStoreError(
                f"Query vector dim {query_vector.shape[1]} != expected {self._dim}"
            )

        query_vector = query_vector.astype(np.float32)
        normalized = self._normalize(query_vector)

        with self._lock:
            total = self._index.ntotal
            if total == 0:
                return []
            actual_k = min(k, total)
            scores, faiss_ids = self._index.search(normalized, actual_k)

        results = []
        for score, faiss_id in zip(scores[0], faiss_ids[0]):
            if faiss_id == -1:  # FAISS returns -1 for padding
                continue
            ref = self._id_to_ref.get(int(faiss_id))
            if ref:
                results.append((ref, float(score)))

        return results

    def remove_embeddings(self, embedding_refs: List[str]) -> int:
        """
        Remove embeddings by their string references.

        Args:
            embedding_refs: List of embedding_reference strings to remove

        Returns:
            int: Number of embeddings actually removed

        Note:
            FAISS IndexIDMap supports remove_ids() via IDSelectorBatch.
        """
        with self._lock:
            ids_to_remove = []
            for ref in embedding_refs:
                faiss_id = self._ref_to_id.pop(ref, None)
                if faiss_id is not None:
                    del self._id_to_ref[faiss_id]
                    ids_to_remove.append(faiss_id)

            if ids_to_remove:
                id_array = np.array(ids_to_remove, dtype=np.int64)
                selector = faiss.IDSelectorArray(len(id_array), faiss.swig_ptr(id_array))
                self._index.remove_ids(selector)

            return len(ids_to_remove)

    def get_embedding_count(self) -> int:
        """Return the total number of embeddings currently stored."""
        with self._lock:
            return self._index.ntotal

    def get_refs_count(self) -> int:
        """Return the number of tracked embedding references."""
        with self._lock:
            return len(self._ref_to_id)

    def clear(self) -> None:
        """Remove all embeddings. Use with caution."""
        with self._lock:
            self._index.reset()
            self._ref_to_id.clear()
            self._id_to_ref.clear()
            self._next_id = 0


# Module-level singleton shared across the entire application process
vector_store_service = VectorStoreService()
