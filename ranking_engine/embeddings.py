"""Sentence-transformer embeddings and FAISS index."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple

import numpy as np

from .config import EMBED_BATCH_SIZE, EMBED_MODEL, EMBEDDINGS_DIR, FAISS_DIR


_ENGINE = None


def get_cached_engine() -> "EmbeddingEngine":
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = EmbeddingEngine()
    return _ENGINE


class EmbeddingEngine:
    def __init__(self, model_name: str = EMBED_MODEL):
        self.model_name = model_name
        self.model = None
        self._cache = {}
        self._load()

    def _load(self):
        import os
        from sentence_transformers import SentenceTransformer

        # Try offline loading first to avoid slow network checks/hangs
        os.environ["HF_HUB_OFFLINE"] = "1"
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as e:
            print(f"OFFLINE LOAD EXCEPTION: {e}", flush=True)
            # Fallback to online loading if model is not cached
            os.environ.pop("HF_HUB_OFFLINE", None)
            self.model = SentenceTransformer(self.model_name)

    def encode(self, texts: List[str], batch_size: int = EMBED_BATCH_SIZE) -> np.ndarray:
        if not texts:
            return np.zeros((0, 384), dtype="float32")
        vecs = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vecs, dtype="float32")

    def encode_one(self, text: str) -> np.ndarray:
        if text not in self._cache:
            self._cache[text] = self.encode([text])[0]
        return self._cache[text]


def save_embeddings(ids: List[int], vectors: np.ndarray, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or EMBEDDINGS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    npz_path = out_dir / "embeddings.npz"
    np.savez_compressed(npz_path, ids=np.array(ids, dtype=np.int32), vectors=vectors)
    meta = {"model": EMBED_MODEL, "count": len(ids), "dim": vectors.shape[1]}
    (out_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    return npz_path

_CACHED_IDS = None
_CACHED_VECTORS = None


def load_embeddings(embeddings_dir: Path | None = None) -> Tuple[List[int], np.ndarray]:
    global _CACHED_IDS, _CACHED_VECTORS
    if _CACHED_IDS is None or _CACHED_VECTORS is None:
        embeddings_dir = embeddings_dir or EMBEDDINGS_DIR
        data = np.load(embeddings_dir / "embeddings.npz")
        _CACHED_IDS = [int(x) for x in data["ids"]]
        _CACHED_VECTORS = data["vectors"].astype("float32")
    return _CACHED_IDS, _CACHED_VECTORS


def build_faiss_index(vectors: np.ndarray, out_dir: Path | None = None) -> Path:
    import faiss

    out_dir = out_dir or FAISS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors.astype("float32"))
    faiss_path = out_dir / "index.faiss"
    faiss.write_index(index, str(faiss_path))
    return faiss_path


_CACHED_INDEX = None


def load_faiss_index(index_dir: Path | None = None):
    global _CACHED_INDEX
    if _CACHED_INDEX is None:
        import faiss

        index_dir = index_dir or FAISS_DIR
        _CACHED_INDEX = faiss.read_index(str(index_dir / "index.faiss"))
    return _CACHED_INDEX


def save_query_vector(vector: np.ndarray, out_dir: Path | None = None) -> Path:
    out_dir = out_dir or EMBEDDINGS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "query.npy"
    np.save(path, vector.astype("float32"))
    return path


def load_query_vector(out_dir: Path | None = None) -> np.ndarray:
    out_dir = out_dir or EMBEDDINGS_DIR
    return np.load(out_dir / "query.npy").astype("float32")


def faiss_search(index, query_vec: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
    q = query_vec.reshape(1, -1).astype("float32")
    scores, indices = index.search(q, top_k)
    return scores[0], indices[0]
