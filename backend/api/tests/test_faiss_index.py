"""FAISS index lifecycle tests."""
from __future__ import annotations

import sys
from pathlib import Path

from django.test import SimpleTestCase

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ranking_engine.index_manager import index_status, is_index_ready


class FaissIndexTests(SimpleTestCase):
    def test_index_status_shape(self):
        status = index_status()
        self.assertIn("embeddings_ready", status)
        self.assertIn("faiss_ready", status)
        self.assertIn("checkpoint", status)

    def test_is_index_ready_matches_artifacts(self):
        status = index_status()
        expected = status["embeddings_ready"] and status["faiss_ready"]
        self.assertEqual(is_index_ready(), expected)

    def test_faiss_search_when_ready(self):
        if not is_index_ready():
            self.skipTest("FAISS index not built yet")
        from ranking_engine.embeddings import faiss_search, load_faiss_index, load_query_vector

        index = load_faiss_index()
        query = load_query_vector()
        scores, idxs = faiss_search(index, query, 10)
        self.assertEqual(len(scores), 10)
        self.assertTrue((idxs >= 0).all())
