import os
import sys


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django

    django.setup()
    from api.services import ranking

    print("Building index...")
    ranking.build_index()
    print("Searching for: 'Senior Python machine learning engineer'")
    results = ranking.search_job("Senior Python machine learning engineer", job_required_skills="python,machine learning", min_experience=3, top_k=5)
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
