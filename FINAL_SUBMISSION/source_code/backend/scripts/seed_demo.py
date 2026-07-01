import os
import sys
import django


def main():
    # ensure backend path is on sys.path so Django settings can be imported
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()
    from api.models import Candidate

    samples = [
        {
            "full_name": "Alice Johnson",
            "profile_text": "Senior Python engineer with deep ML and data experience. Worked with pandas, scikit-learn, and PyTorch.",
            "skills": "python, machine learning, pytorch, pandas, scikit-learn",
            "years_experience": 7,
            "open_to_work": True,
            "recruiter_response_rate": 85,
            "interview_completion_rate": 90,
            "offer_acceptance_rate": 80,
            "profile_completeness": 95,
        },
        {
            "full_name": "Bob Smith",
            "profile_text": "Backend engineer focused on Django and PostgreSQL. Strong API design and system architecture.",
            "skills": "django, postgresql, api, rest, docker",
            "years_experience": 5,
            "open_to_work": False,
            "recruiter_response_rate": 60,
            "interview_completion_rate": 70,
            "offer_acceptance_rate": 50,
            "profile_completeness": 80,
        },
        {
            "full_name": "Carol Lee",
            "profile_text": "Frontend developer skilled in React, TypeScript, and Tailwind. Excellent UI/UX sense.",
            "skills": "react, typescript, tailwind, css, frontend",
            "years_experience": 4,
            "open_to_work": True,
            "recruiter_response_rate": 75,
            "interview_completion_rate": 85,
            "offer_acceptance_rate": 70,
            "profile_completeness": 90,
        },
    ]

    for s in samples:
        Candidate.objects.update_or_create(full_name=s["full_name"], defaults=s)
    # add simple career history for Alice and Bob
    from api.models import CandidateJob
    alice = Candidate.objects.filter(full_name__icontains="alice").first()
    bob = Candidate.objects.filter(full_name__icontains="bob").first()
    if alice:
        CandidateJob.objects.update_or_create(candidate=alice, title="ML Engineer", company="DataCorp", defaults={"description": "Worked on ML models", "start_date": "2016-01-01", "end_date": "2020-12-31"})
        CandidateJob.objects.update_or_create(candidate=alice, title="Senior ML Engineer", company="AI Labs", defaults={"description": "Led ML initiatives", "start_date": "2021-01-01", "end_date": None})
    if bob:
        CandidateJob.objects.update_or_create(candidate=bob, title="Backend Engineer", company="WebApps", defaults={"description": "APIs and DBs", "start_date": "2018-06-01", "end_date": None})
    print("Seeded sample candidates.")


if __name__ == "__main__":
    main()
