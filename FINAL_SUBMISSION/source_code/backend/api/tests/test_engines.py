from django.test import TestCase

from api.services.skill_engine import compute_skill_fit
from api.services.experience_engine import compute_experience_fit
from api.services.behavioral_engine import compute_recruitability_score as compute_recruit


class EnginesTests(TestCase):
    def test_skill_score(self):
        req = ["python", "ml"]
        cand = "python,java"
        s, details = compute_skill_fit(req, cand)
        self.assertTrue(0.0 <= s <= 100.0)

    def test_experience_score(self):
        res = compute_experience_fit(3, 5, career_history=None)
        self.assertTrue(50 <= res["score"] <= 100)
        res2 = compute_experience_fit(5, 2.5, career_history=None)
        self.assertTrue(0 <= res2["score"] <= 100)

    def test_recruitability(self):
        class C:
            pass

        c = C()
        c.recruiter_response_rate = 80
        c.interview_completion_rate = 90
        c.offer_acceptance_rate = 70
        c.profile_completeness = 100
        c.open_to_work = True
        res = compute_recruit(c)
        score = res.get("score")
        self.assertTrue(0 <= score <= 100)

    def test_ranking_integration(self):
        # lightweight integration smoke test: create a candidate then run ranking
        from api.services.ranking import build_index, search_job
        from api.models import Candidate
        Candidate.objects.create(full_name="Test User", profile_text="Python ML engineer", skills="python,machine learning", years_experience=6, recruiter_response_rate=80, interview_completion_rate=90, offer_acceptance_rate=80, profile_completeness=90, open_to_work=True)
        build_index()
        results = search_job("Senior Python machine learning engineer", job_struct={"required_skills": ["python", "machine learning"], "experience_years": "3"}, top_k=3)
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 1)
