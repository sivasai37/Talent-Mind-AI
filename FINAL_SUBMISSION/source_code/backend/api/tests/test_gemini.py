from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from ..services.gemini_agent import call_gemini_recruiter
from ..models import Candidate


class GeminiAgentTests(TestCase):
    def setUp(self) -> None:
        self.candidate = Candidate.objects.create(
            full_name="Test Candidate",
            profile_text="Experienced product designer with focus on UX and web/mobile.",
            skills="product design, ux, figma, prototyping",
            years_experience=6.0,
            github_url="https://github.com/test",
            open_to_work=True,
            recruiter_response_rate=80.0,
            interview_completion_rate=90.0,
            offer_acceptance_rate=70.0,
            profile_completeness=85.0,
        )

    def test_fallback_recruiter_analysis_returns_expected_fields(self):
        # ensure fallback path when no API key is present
        scores = {"semantic_score": 60.0, "skill_score": 70.0, "experience_score": 65.0, "recruitability_score": 80.0}
        result = call_gemini_recruiter({}, self.candidate, scores)
        self.assertIsInstance(result, dict)
        for key in ("llm_score", "recommendation", "strengths", "weaknesses", "missing_skills", "recruiter_summary"):
            self.assertIn(key, result)
        self.assertGreaterEqual(result["llm_score"], 0.0)
        self.assertLessEqual(result["llm_score"], 100.0)

    @override_settings(GEMINI_API_KEY="FAKE_KEY_FOR_TEST")
    def test_parse_llm_output_from_wrapped_text(self):
        # simulate the Google generative API returning text with extra characters around JSON
        fake_payload = {
            "llm_score": 92.5,
            "recommendation": "Strong Fit",
            "strengths": ["Experienced in product design"],
            "weaknesses": [],
            "missing_skills": ["react"],
            "recruiter_summary": "Excellent fit based on product design background."
        }
        wrapped_text = f"Response:\nSome commentary\n{json.dumps(fake_payload)}\n--end"

        class FakeResponse(SimpleNamespace):
            pass

        fake_resp = FakeResponse(text=wrapped_text)

        # inject a fake google.generativeai module into sys.modules for the duration
        import sys
        import types

        fake_genai = types.ModuleType("google.generativeai")
        fake_genai.generate_text = lambda *a, **k: fake_resp
        fake_genai.configure = lambda **k: None
        fake_google = types.ModuleType("google")
        fake_google.generativeai = fake_genai

        with patch.dict(sys.modules, {"google": fake_google, "google.generativeai": fake_genai}):
            result = call_gemini_recruiter({}, self.candidate, {"semantic_score": 50, "skill_score": 50, "experience_score": 50, "recruitability_score": 50})
            self.assertIsInstance(result, dict)
            self.assertAlmostEqual(result.get("llm_score", 0), 92.5)
            self.assertEqual(result.get("recommendation"), "Strong Fit")
