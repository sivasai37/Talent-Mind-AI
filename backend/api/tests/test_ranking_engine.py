"""Ranking engine regression and integration tests."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from django.test import SimpleTestCase, TestCase

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ranking_engine.config import DEFAULT_CANDIDATES_PATH
from ranking_engine.domain_semantics import compute_domain_alignment
from ranking_engine.explain import build_full_explanation
from ranking_engine.honeypot import detect_honeypot
from ranking_engine.index_manager import index_status
from ranking_engine.jd import analyze_job_description, load_job_description
from ranking_engine.pipeline import rank_candidates_online, write_submission_csv


class JDUnderstandingTests(SimpleTestCase):
    def test_analyze_job_description_extracts_experience_band(self):
        struct = load_job_description()
        self.assertGreaterEqual(struct.get("experience_min", 0), 5)
        self.assertIn("required_skills", struct)


class DomainSemanticsTests(SimpleTestCase):
    def test_domain_alignment_on_sample_candidate(self):
        import json

        sample = PROJECT_ROOT / "data" / "challenge_dataset" / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge" / "sample_candidates.json"
        if not sample.exists():
            self.skipTest("sample_candidates.json missing")
        candidates = json.loads(sample.read_text(encoding="utf-8"))
        score = compute_domain_alignment(candidates[0])
        self.assertIn("score", score)


class RankingPipelineTests(SimpleTestCase):
    def test_online_ranking_produces_100_rows(self):
        if not DEFAULT_CANDIDATES_PATH.exists():
            self.skipTest("candidates file missing")
        results = rank_candidates_online(
            candidates_path=DEFAULT_CANDIDATES_PATH,
            job_struct=load_job_description(),
            prefilter_k=400,
            retrieval_k=80,
            top_k=20,
        )
        self.assertEqual(len(results), 20)
        self.assertGreaterEqual(results[0]["score"], results[-1]["score"])


class DjangoAdapterTests(TestCase):
    def test_adapter_imports(self):
        from api.services.ranking import detect_role_type, get_role_weights

        struct = load_job_description()
        role = detect_role_type(struct, title="Senior AI Engineer")
        self.assertIn("semantic", get_role_weights(role))
