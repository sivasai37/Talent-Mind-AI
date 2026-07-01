from rest_framework import serializers

from .models import Candidate, Job, CandidateJob, RankingJob, RankingResult


class CandidateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateJob
        fields = ["id", "company", "title", "start_date", "end_date", "description"]


class CandidateSerializer(serializers.ModelSerializer):
    jobs = CandidateJobSerializer(many=True, read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "profile_text",
            "skills",
            "years_experience",
            "github_url",
            "open_to_work",
            "recruiter_response_rate",
            "interview_completion_rate",
            "offer_acceptance_rate",
            "profile_completeness",
            "salary_expectation",
            "relocation_preference",
            "jobs",
        ]


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["id", "title", "description", "required_skills", "preferred_skills", "min_experience"]


class RankingResultSerializer(serializers.ModelSerializer):
    candidate = CandidateSerializer(read_only=True)

    class Meta:
        model = RankingResult
        fields = [
            "id",
            "candidate",
            "rank",
            "semantic_score",
            "skill_score",
            "experience_score",
            "recruitability_score",
            "llm_score",
            "final_score",
            "strengths",
            "weaknesses",
            "missing_skills",
            "recruiter_summary",
            "payload",
        ]


class RankingJobSerializer(serializers.ModelSerializer):
    results = RankingResultSerializer(many=True, read_only=True)

    class Meta:
        model = RankingJob
        fields = ["id", "title", "job_description", "job_analysis", "created_at", "results"]
