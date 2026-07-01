"""
ranking.py — Django adapter for the unified ranking_engine package.

All ranking logic lives in ranking_engine/. This module exposes the same
API surface expected by views.py and tests.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root (parent of backend/) is on path for ranking_engine
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ranking_engine.api_adapter import (  # noqa: E402
    build_index,
    detect_role_type,
    get_role_weights,
    search_job,
)
from ranking_engine.index_manager import ensure_index, index_status, is_index_ready  # noqa: E402
from ranking_engine.jd import analyze_job_description  # noqa: E402


def invalidate_index() -> None:
    """Compatibility hook — index is file-backed; rebuild via build_index(force=True)."""
    build_index(force=True)


__all__ = [
    "analyze_job_description",
    "build_index",
    "detect_role_type",
    "ensure_index",
    "get_role_weights",
    "index_status",
    "invalidate_index",
    "is_index_ready",
    "search_job",
]
