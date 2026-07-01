from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from api.models import Candidate


def _mock_rank_result(candidate_id: int = 1, full_name: str = "Test Recruiter Candidate"):
    return [{
        "candidate_id": candidate_id,
        "full_name": full_name,
        "semantic_score": 82.0,
        "skill_score": 78.0,
        "experience_score": 75.0,
        "recruitability_score": 70.0,
        "llm_score": 82.0,
        "final_score": 79.5,
        "potential_score": 83.0,
        "confidence_score": 72.0,
        "risk_level": "low",
        "strengths": ["Strong Python alignment"],
        "weaknesses": [],
        "missing_skills": ["vector_search"],
        "matching_skills": ["python", "django"],
        "learning_path": ["Deepen vector search experience"],
        "interview_questions": ["Describe a Django API you shipped."],
        "future_roles": [],
        "growth_forecast": {},
        "salary_fit": {},
        "why_selected": "Strong backend fit.",
        "why_rejected": "",
        "role_fit_analysis": "",
        "recruiter_recommendation": "Strong Fit — prioritize for technical screen",
        "recruiter_summary": "Response rate 90%",
        "payload": {},
    }]


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Candidate.objects.create(
            full_name="Test Recruiter Candidate",
            profile_text="Experienced backend engineer with Python and Django.",
            skills="python,django,rest,postgresql",
            years_experience=6,
            github_url="https://github.com/testuser",
            open_to_work=True,
            recruiter_response_rate=90,
            interview_completion_rate=95,
            offer_acceptance_rate=85,
            profile_completeness=90,
        )

    def test_candidates_endpoint(self):
        response = self.client.get("/api/candidates/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertTrue(len(response.json()) >= 1)

    @patch("api.services.ranking.search_job", return_value=_mock_rank_result())
    def test_rank_endpoint_and_rankings_list(self, _mock_search):
        payload = {
            "title": "Senior Python Developer",
            "job_description": "Senior role requiring Python, Django, REST APIs, and PostgreSQL.",
            "top_k": 5,
        }
        rank_response = self.client.post("/api/rank/", payload, format="json")
        self.assertEqual(rank_response.status_code, 200)
        body = rank_response.json()
        self.assertIn("job_structure", body)
        self.assertIn("results", body)
        self.assertTrue(len(body["results"]) >= 1)

        rankings_response = self.client.get("/api/rankings/")
        self.assertEqual(rankings_response.status_code, 200)
        self.assertTrue(len(rankings_response.json()) >= 1)

    @patch("api.services.ranking.search_job", return_value=_mock_rank_result())
    def test_rankings_export(self, _mock_search):
        rank_response = self.client.post(
            "/api/rank/",
            {
                "title": "Senior Python Developer",
                "job_description": "Senior role requiring Python, Django, REST APIs, and PostgreSQL.",
                "top_k": 2,
            },
            format="json",
        )
        job_id = rank_response.json().get("id")
        response = self.client.get(f"/api/rankings/export/?job_id={job_id}")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn("candidate_id", content)
        self.assertIn("full_name", content)
