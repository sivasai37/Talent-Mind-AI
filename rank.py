#!/usr/bin/env python3
"""
rank.py — Redrob offline submission ranker (uses unified ranking_engine).
"""
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ranking_engine.api_adapter import rank, rank_for_submission
from ranking_engine.config import DEFAULT_CANDIDATES_PATH, DEFAULT_JD_PATH
from ranking_engine.index_manager import ensure_index, is_index_ready
from ranking_engine.jd import load_job_description
from ranking_engine.pipeline import write_submission_csv


def main():
    import os
    os.environ["HF_HUB_OFFLINE"] = "1"
    parser = argparse.ArgumentParser(description="Rank candidates for Redrob JD")
    parser.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES_PATH)
    parser.add_argument("--jd", type=Path, default=DEFAULT_JD_PATH)
    parser.add_argument("--out", type=Path, default=ROOT / "submission.csv")
    parser.add_argument("--also-write", type=Path, default=ROOT / "FINAL_SUBMISSION" / "ranked_candidates.csv")
    parser.add_argument("--retrieval-k", type=int, default=500)
    parser.add_argument("--build-index", action="store_true", help="Force/resume FAISS index build")
    parser.add_argument("--online", action="store_true", help="Force online ranking (skip FAISS)")
    args = parser.parse_args()

    t0 = time.time()
    job_struct = load_job_description(args.jd)
    print(f"Ranking: {job_struct.get('title')} ({job_struct.get('role')} weights)")

    if args.build_index:
        print("Building/resuming FAISS index...")
        ensure_index(auto_build=True, force_rebuild=False)

    use_index = is_index_ready() and not args.online
    if use_index:
        print("Using precomputed FAISS index.")
        results = rank_for_submission(candidates_path=args.candidates, top_k=100)
    else:
        if args.online:
            print("Online ranking mode (--online).")
        else:
            print("FAISS index not ready — online ranking fallback (use --build-index to precompute).")
        results = rank(
            job_text=job_struct.get("full_text", ""),
            title=job_struct.get("title", ""),
            job_struct=job_struct,
            candidates_path=args.candidates,
            top_k=100,
            prefer_index=False,
        )

    write_submission_csv(results, args.out)
    if args.also_write:
        write_submission_csv(results, args.also_write)
    print(f"Wrote {len(results)} candidates to {args.out} in {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
