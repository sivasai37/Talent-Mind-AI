import os
import sys
import csv
import json

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base not in sys.path:
    sys.path.insert(0, base)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
from django.conf import settings

django.setup()
from api.services import ranking
from api.services.jd_understanding import analyze_job_description


def main():
    job_title = "Senior Python Backend Engineer"
    job_description = "We are hiring a Senior Python Backend Engineer with Django, REST APIs, PostgreSQL, and cloud deployment experience."
    top_k = 10
    jd_struct = analyze_job_description(job_description, title=job_title)
    ranking.build_index()
    results = ranking.search_job(job_description, top_k=top_k, job_struct=jd_struct)

    output_dir = settings.EXPORTS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "sample_ranked_candidates.json"
    csv_path = output_dir / "ranked_candidates.csv"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump({"job_title": job_title, "job_structure": jd_struct, "results": results}, f, indent=2)

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "candidate_id",
            "full_name",
            "semantic_score",
            "skill_score",
            "experience_score",
            "recruitability_score",
            "llm_score",
            "final_score",
            "recommendation",
            "strengths",
            "weaknesses",
            "missing_skills",
            "recruiter_summary",
        ])
        for item in results:
            recruiter_ai = item.get("recruiter_ai", {})
            writer.writerow([
                item.get("candidate_id"),
                item.get("full_name"),
                item.get("semantic_score"),
                item.get("skill_score"),
                item.get("experience_score"),
                item.get("recruitability_score"),
                item.get("llm_score"),
                item.get("final_score"),
                recruiter_ai.get("recommendation", ""),
                " | ".join(item.get("strengths", [])),
                " | ".join(item.get("weaknesses", [])),
                " | ".join(item.get("missing_skills", [])),
                recruiter_ai.get("recruiter_summary", ""),
            ])

    print(f"Sample ranked JSON saved to {json_path}")
    print(f"Sample ranked CSV saved to {csv_path}")


if __name__ == "__main__":
    main()
