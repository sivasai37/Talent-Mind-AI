"""
embeddings.py — Semantic embedding engine for TalentMind AI.

Primary backend: Sentence Transformers (all-MiniLM-L6-v2).
Fallback backend: Deterministic hashing-based embedding using numpy, so the
entire pipeline runs even without heavy ML dependencies installed.

The fallback produces stable 384-dim vectors with meaningful cosine similarity
based on token hashing + TF weighting (a lightweight semantic approximation).
"""
from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from typing import List

import numpy as np

EMBED_DIM = 384
_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]*")

# Lightweight synonym/cluster map so semantically related terms land near each
# other even in fallback mode (helps "non-keyword" matching feel intelligent).
_SEMANTIC_CLUSTERS = {
    "ml": ["machine", "learning", "ml", "ai", "deep", "neural", "model", "tensorflow", "pytorch", "scikit"],
    "backend": ["backend", "django", "flask", "fastapi", "api", "rest", "server", "node", "express"],
    "frontend": ["frontend", "react", "vue", "angular", "javascript", "typescript", "tailwind", "css", "ui"],
    "data": ["data", "sql", "postgresql", "mysql", "pandas", "etl", "warehouse", "analytics", "bigquery"],
    "cloud": ["cloud", "aws", "azure", "gcp", "docker", "kubernetes", "devops", "terraform", "ci"],
    "lead": ["lead", "leadership", "manager", "mentor", "architect", "principal", "team", "stakeholder"],
}


def _token_cluster_boosts(token: str) -> List[int]:
    boosts = []
    for i, (_k, words) in enumerate(_SEMANTIC_CLUSTERS.items()):
        if token in words:
            boosts.append(i)
    return boosts


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


class EmbeddingEngine:
    """Loads sentence-transformers if available, else falls back to numpy."""

    def __init__(self):
        self.backend = "fallback"
        self.model = None
        self._try_load_transformer()

    def _try_load_transformer(self):
        import os

        # Try offline loading first to avoid slow network checks/hangs
        os.environ["HF_HUB_OFFLINE"] = "1"
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self.model = SentenceTransformer(_MODEL_NAME)
            self.backend = "sentence-transformers"
        except Exception:
            # Fallback to online loading if model is not cached
            os.environ.pop("HF_HUB_OFFLINE", None)
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                self.model = SentenceTransformer(_MODEL_NAME)
                self.backend = "sentence-transformers"
            except Exception:
                self.model = None
                self.backend = "fallback"

    # ---- public API ----
    def encode(self, texts: List[str]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        if self.backend == "sentence-transformers" and self.model is not None:
            vecs = self.model.encode(texts, normalize_embeddings=True)
            return np.asarray(vecs, dtype="float32")
        return np.vstack([self._fallback_encode(t) for t in texts]).astype("float32")

    def encode_one(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    # ---- deterministic fallback ----
    def _fallback_encode(self, text: str) -> np.ndarray:
        vec = np.zeros(EMBED_DIM, dtype="float32")
        tokens = tokenize(text)
        if not tokens:
            return vec
        counts: dict[str, int] = {}
        for tok in tokens:
            counts[tok] = counts.get(tok, 0) + 1
        for tok, cnt in counts.items():
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBED_DIM
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            weight = 1.0 + np.log(cnt)
            vec[idx] += sign * weight
            # cluster boosts give semantic grouping
            for c in _token_cluster_boosts(tok):
                cidx = (c * 37 + 11) % EMBED_DIM
                vec[cidx] += 0.6 * weight
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec


@lru_cache(maxsize=1)
def get_engine() -> EmbeddingEngine:
    return EmbeddingEngine()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype="float32")
    b = np.asarray(b, dtype="float32")
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))
