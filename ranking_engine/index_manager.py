"""FAISS index lifecycle: load, resume build, cache."""
from __future__ import annotations

import json
import subprocess
import sys
import threading
from pathlib import Path

from .config import DEFAULT_CANDIDATES_PATH, DEFAULT_JD_PATH, EMBEDDINGS_DIR, FAISS_DIR

_build_lock = threading.Lock()
_index_ready = False

NPZ_PATH = EMBEDDINGS_DIR / "embeddings.npz"
FAISS_PATH = FAISS_DIR / "index.faiss"
QUERY_PATH = EMBEDDINGS_DIR / "query.npy"
CHECKPOINT_PATH = EMBEDDINGS_DIR / "build_checkpoint.json"


def _verify_index_alignment() -> bool:
    """Spot-check that embedding row order matches candidate stream order."""
    try:
        import json
        import numpy as np
        from .config import DEFAULT_CANDIDATES_PATH
        from .honeypot import detect_honeypot
        from .text_builder import build_candidate_id

        data = np.load(NPZ_PATH)
        stored_ids = [int(x) for x in data["ids"][:5]]
        expected_ids: list[int] = []
        import gzip
        if str(DEFAULT_CANDIDATES_PATH).endswith(".gz"):
            f = gzip.open(DEFAULT_CANDIDATES_PATH, "rt", encoding="utf-8")
        else:
            f = open(DEFAULT_CANDIDATES_PATH, encoding="utf-8")
        with f:
            for line in f:
                if not line.strip():
                    continue
                cand = json.loads(line)
                if detect_honeypot(cand)[0]:
                    continue
                expected_ids.append(build_candidate_id(cand))
                if len(expected_ids) >= len(stored_ids):
                    break
        return stored_ids == expected_ids
    except Exception:
        return False


def index_status() -> dict:
    checkpoint = {}
    if CHECKPOINT_PATH.exists():
        try:
            checkpoint = json.loads(CHECKPOINT_PATH.read_text(encoding="utf-8"))
        except Exception:
            checkpoint = {}
    return {
        "embeddings_ready": NPZ_PATH.exists(),
        "faiss_ready": FAISS_PATH.exists(),
        "query_ready": QUERY_PATH.exists(),
        "checkpoint": checkpoint,
    }


def is_index_ready() -> bool:
    if not (NPZ_PATH.exists() and FAISS_PATH.exists()):
        return False
    try:
        import numpy as np
        data = np.load(NPZ_PATH)
        ids = data["ids"]
        vectors = data["vectors"]
        if len(ids) != vectors.shape[0]:
            return False
        meta_path = EMBEDDINGS_DIR / "meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("count") != len(ids):
                return False
        if not _verify_index_alignment():
            return False
    except Exception:
        return False
    return True


def ensure_index(force_rebuild: bool = False, auto_build: bool = True) -> bool:
    """Load or build FAISS artifacts. Returns True when index is ready."""
    global _index_ready

    if not force_rebuild and is_index_ready():
        _index_ready = True
        return True

    if not auto_build:
        return False

    with _build_lock:
        if not force_rebuild and is_index_ready():
            _index_ready = True
            return True

        project_root = Path(__file__).resolve().parent.parent
        script = project_root / "scripts" / "build_index.py"
        if not script.exists():
            return False

        cmd = [sys.executable, str(script), "--batch-size", "128"]
        if force_rebuild:
            cmd.append("--no-resume")

        proc = subprocess.run(cmd, cwd=str(project_root), capture_output=False)
        _index_ready = proc.returncode == 0 and is_index_ready()
        return _index_ready
