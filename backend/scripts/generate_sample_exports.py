import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
# ensure parent (backend) directory is on sys.path so 'core' package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from api.models import RankingJob, RankingResult, Candidate


def create_sample_job():
    # create a sample RankingJob using existing candidates
    candidates = list(Candidate.objects.all()[:5])
    if not candidates:
        print("No candidates found in DB to generate sample exports.")
        return
    job = RankingJob.objects.create(title="Sample export run", job_description="Generated sample export.")
    for idx, c in enumerate(candidates, start=1):
        # create simple synthetic scores
        semantic_score = 80.0 - idx * 5
        skill_score = 75.0 - idx * 4
        experience_score = 70.0 - idx * 3
        recruitability_score = 60.0 + idx * 2
        llm_score = (semantic_score * 0.35 + skill_score * 0.25 + experience_score * 0.15 + recruitability_score * 0.15) / 0.9
        final_score = semantic_score * 0.35 + skill_score * 0.25 + experience_score * 0.15 + recruitability_score * 0.15 + llm_score * 0.1
        result = RankingResult.objects.create(
            ranking_job=job,
            candidate=c,
            rank=idx,
            semantic_score=semantic_score,
            skill_score=skill_score,
            experience_score=experience_score,
            recruitability_score=recruitability_score,
            llm_score=llm_score,
            final_score=final_score,
            strengths=["Sample strength"],
            weaknesses=["Sample weakness"],
            missing_skills=["skill-x"],
            recruiter_summary="Auto-generated sample summary",
            payload={"sample": True},
        )
    print(f"Created sample RankingJob id={job.id} with {len(candidates)} results")
    return job


if __name__ == "__main__":
    job = create_sample_job()
    if job:
        out_dir = os.path.join(os.getcwd(), "..", "exports")
        os.makedirs(out_dir, exist_ok=True)
        csv_path = os.path.join(out_dir, f"ranked_candidates_{job.id}.csv")
        submission_path = os.path.join(out_dir, f"submission_candidates_{job.id}.csv")
        # reuse view logic lightly
        from api.views import RankingExportAPIView
        from django.test import RequestFactory

        rf = RequestFactory()
        # full export
        req = rf.get(f"/fake?job_id={job.id}")
        resp = RankingExportAPIView.as_view()(req)
        with open(csv_path, "wb") as fh:
            if hasattr(resp, "render"):
                resp.render()
            fh.write(resp.content)
        # submission export
        req2 = rf.get(f"/fake?job_id={job.id}&format=submission")
        resp2 = RankingExportAPIView.as_view()(req2)
        with open(submission_path, "wb") as fh:
            if hasattr(resp2, "render"):
                resp2.render()
            fh.write(resp2.content)
        print(f"Wrote sample exports to {csv_path} and {submission_path}")
