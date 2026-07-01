#!/usr/bin/env python3
"""
Pre-compute candidate embeddings and FAISS index (memmap + checkpoint resume).
"""
import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ranking_engine.config import (
    DEFAULT_CANDIDATES_PATH,
    DEFAULT_JD_PATH,
    EMBED_BATCH_SIZE,
    EMBEDDINGS_DIR,
)
from ranking_engine.embeddings import (
    EmbeddingEngine,
    build_faiss_index,
    save_embeddings,
    save_query_vector,
)
from ranking_engine.honeypot import detect_honeypot
from ranking_engine.jd import load_job_description
from ranking_engine.text_builder import build_candidate_id, build_retrieval_document

CHECKPOINT_FILE = "build_checkpoint.json"
VECTORS_MMAP = "vectors.mmap"
IDS_FILE = "ids.partial.npy"


def _open_candidates(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def count_valid(candidates_path: Path) -> tuple[int, int]:
    valid = 0
    skipped = 0
    with _open_candidates(candidates_path) as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            if detect_honeypot(cand)[0]:
                skipped += 1
            else:
                valid += 1
    return valid, skipped


def load_checkpoint(out_dir: Path) -> dict:
    path = out_dir / CHECKPOINT_FILE
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"encoded": 0, "skipped_honeypots": 0}


def save_checkpoint(out_dir: Path, encoded: int, skipped: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / CHECKPOINT_FILE).write_text(
        json.dumps({"encoded": encoded, "skipped_honeypots": skipped}),
        encoding="utf-8",
    )


def stream_encode_memmap(
    candidates_path: Path,
    engine: EmbeddingEngine,
    batch_size: int,
    out_dir: Path,
    resume: bool = True,
):
    out_dir.mkdir(parents=True, exist_ok=True)
    checkpoint = load_checkpoint(out_dir) if resume else {"encoded": 0, "skipped_honeypots": 0}
    start_encoded = int(checkpoint.get("encoded", 0))

    print("Counting valid candidates...", flush=True)
    total_valid, skipped_total = count_valid(candidates_path)
    print(f"  {total_valid} valid, {skipped_total} honeypots excluded", flush=True)

    ids_path = out_dir / IDS_FILE
    npz_path = out_dir / "embeddings.npz"

    if resume and start_encoded >= total_valid and npz_path.exists():
        data = np.load(npz_path)
        ids = [int(x) for x in data["ids"]]
        return ids, data["vectors"].astype("float32"), skipped_total

    # Pre-allocate in RAM (~150MB for 100K x 384) — avoids Windows memmap issues
    vectors = np.zeros((total_valid, 384), dtype="float32")
    ids: list[int] = list(np.load(ids_path)) if resume and ids_path.exists() else []
    if resume and start_encoded > 0 and len(ids) > start_encoded:
        ids = ids[:start_encoded]

    batch_ids: list[int] = []
    batch_texts: list[str] = []
    seen = 0
    written = start_encoded

    with _open_candidates(candidates_path) as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            if detect_honeypot(cand)[0]:
                continue
            if seen < start_encoded:
                seen += 1
                continue

            batch_ids.append(build_candidate_id(cand))
            batch_texts.append(build_retrieval_document(cand))

            if len(batch_texts) >= batch_size:
                vecs = engine.encode(batch_texts, batch_size=batch_size)
                end = written + len(batch_ids)
                vectors[written:end] = vecs
                ids.extend(batch_ids)
                written = end
                print(f"  encoded {written}/{total_valid}...", flush=True)
                save_checkpoint(out_dir, written, skipped_total)
                np.save(ids_path, np.array(ids, dtype=np.int32))
                batch_ids, batch_texts = [], []

    if batch_texts:
        vecs = engine.encode(batch_texts, batch_size=batch_size)
        end = written + len(batch_ids)
        vectors[written:end] = vecs
        ids.extend(batch_ids)
        written = end
        print(f"  encoded {written}/{total_valid} (final batch).", flush=True)

    save_checkpoint(out_dir, written, skipped_total)
    np.save(ids_path, np.array(ids, dtype=np.int32))
    vectors = vectors[:written]
    ids = ids[:written]
    return ids, vectors, skipped_total


def main():
    parser = argparse.ArgumentParser(description="Build embeddings + FAISS index")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES_PATH)
    parser.add_argument("--jd", type=Path, default=DEFAULT_JD_PATH)
    parser.add_argument("--batch-size", type=int, default=EMBED_BATCH_SIZE)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    start = time.time()
    print("Loading embedding model...", flush=True)
    engine = EmbeddingEngine()
    print(f"Model ready. Streaming {args.candidates}...", flush=True)

    ids, vectors, skipped = stream_encode_memmap(
        args.candidates,
        engine,
        args.batch_size,
        EMBEDDINGS_DIR,
        resume=not args.no_resume,
    )
    print(f"Skipped {skipped} hard honeypots. Valid vectors: {len(ids)}", flush=True)

    npz_path = save_embeddings(ids, vectors)
    print(f"Saved embeddings: {npz_path}", flush=True)

    faiss_path = build_faiss_index(vectors)
    print(f"Saved FAISS index: {faiss_path}", flush=True)

    job_struct = load_job_description(args.jd)
    query_vec = engine.encode_one(job_struct.get("full_text", ""))
    qpath = save_query_vector(query_vec)
    print(f"Saved JD query vector: {qpath}", flush=True)

    print(f"Done in {time.time() - start:.1f}s", flush=True)


if __name__ == "__main__":
    main()
