from django.test import TestCase, RequestFactory

from ..views import RankingExportAPIView
from ..models import RankingJob, RankingResult, Candidate


class ExportTests(TestCase):
    def setUp(self):
        # create candidates and a ranking job
        self.c1 = Candidate.objects.create(full_name="A One")
        self.c2 = Candidate.objects.create(full_name="B Two")
        self.job = RankingJob.objects.create(title="Export Test", job_description="x")
        RankingResult.objects.create(ranking_job=self.job, candidate=self.c1, rank=1, semantic_score=80, skill_score=70, experience_score=60, recruitability_score=90, llm_score=50, final_score=75, strengths=["s"], weaknesses=["w"], missing_skills=["m"], recruiter_summary="ok", payload={})
        RankingResult.objects.create(ranking_job=self.job, candidate=self.c2, rank=2, semantic_score=60, skill_score=50, experience_score=40, recruitability_score=60, llm_score=30, final_score=45, strengths=["s2"], weaknesses=["w2"], missing_skills=["m2"], recruiter_summary="ok2", payload={})

    def test_export_latest_defaults(self):
        rf = RequestFactory()
        req = rf.get("/fake")
        resp = RankingExportAPIView.as_view()(req)
        # render and check
        if hasattr(resp, "render"):
            resp.render()
        content = resp.content.decode()
        self.assertIn("candidate_id,full_name,semantic_score", content)
        self.assertIn("A One", content)
