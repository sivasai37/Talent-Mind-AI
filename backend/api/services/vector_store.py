"""
vector_store.py — Semantic Retrieval Layer (STEP 3).

Stores candidate embeddings and retrieves Top-K most semantically relevant
candidates. Uses FAISS (IndexFlatIP on normalized vectors == cosine) when
available, otherwise a numpy brute-force cosine index. No keyword matching.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from .embeddings import EMBED_DIM


def _normalize(mat: np.ndarray) -> np.ndarray:
    mat = np.asarray(mat, dtype="float32")
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


class VectorStore:
    """Top-K semantic retrieval with FAISS or numpy fallback."""

    def __init__(self, dim: int = EMBED_DIM):
        self.dim = dim
        self.backend = "numpy"
        self.ids: List[int] = []
        self._vectors: np.ndarray | None = None
        self._faiss_index = None
        self._try_faiss()

    def _try_faiss(self):
        try:
            import faiss  # type: ignore

            self._faiss_index = faiss.IndexFlatIP(self.dim)
            self.backend = "faiss"
        except Exception:
            self._faiss_index = None
            self.backend = "numpy"

    def reset(self):
        self.ids = []
        self._vectors = None
        if self.backend == "faiss":
            self._try_faiss()

    def add(self, ids: List[int], vectors: np.ndarray):
        vectors = _normalize(vectors)
        self.ids.extend(list(ids))
        if self.backend == "faiss" and self._faiss_index is not None:
            self._faiss_index.add(vectors)
        else:
            if self._vectors is None:
                self._vectors = vectors
            else:
                self._vectors = np.vstack([self._vectors, vectors])

    def search(self, query_vec: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        if not self.ids:
            return []
        q = _normalize(np.asarray(query_vec, dtype="float32").reshape(1, -1))
        top_k = min(top_k, len(self.ids))
        if self.backend == "faiss" and self._faiss_index is not None:
            scores, idxs = self._faiss_index.search(q, top_k)
            results = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx == -1:
                    continue
                results.append((self.ids[idx], float(score)))
            return results
        # numpy brute force cosine (vectors already normalized)
        sims = (self._vectors @ q[0])
        order = np.argsort(-sims)[:top_k]
        return [(self.ids[i], float(sims[i])) for i in order]

    @property
    def size(self) -> int:
        return len(self.ids)


# Singleton store for the running process
_STORE: VectorStore | None = None


def get_store() -> VectorStore:
    global _STORE
    if _STORE is None:
        _STORE = VectorStore()
    return _STORE


def rebuild_store(id_vector_pairs: List[Tuple[int, np.ndarray]]) -> VectorStore:
    store = get_store()
    store.reset()
    if id_vector_pairs:
        ids = [i for i, _ in id_vector_pairs]
        vecs = np.vstack([v for _, v in id_vector_pairs])
        store.add(ids, vecs)
    return store
