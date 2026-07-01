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
            "certifications",
            "education_level",
            "location",
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
            "potential_score",
            "confidence_score",
            "risk_level",
            "strengths",
            "weaknesses",
            "missing_skills",
            "learning_path",
            "interview_questions",
            "future_roles",
            "growth_forecast",
            "salary_fit",
            "why_selected",
            "why_rejected",
            "role_fit_analysis",
            "recruiter_recommendation",
            "recruiter_summary",
            "payload",
        ]


class RankingJobSerializer(serializers.ModelSerializer):
    results = RankingResultSerializer(many=True, read_only=True)

    class Meta:
        model = RankingJob
        fields = [
            "id",
            "title",
            "job_description",
            "job_analysis",
            "role_type",
            "weights_used",
            "created_at",
            "results",
        ]


class RankingJobListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view — no nested results."""
    result_count = serializers.SerializerMethodField()
    top_candidate_name = serializers.SerializerMethodField()
    top_score = serializers.SerializerMethodField()

    class Meta:
        model = RankingJob
        fields = [
            "id",
            "title",
            "role_type",
            "created_at",
            "result_count",
            "top_candidate_name",
            "top_score",
        ]

    def get_result_count(self, obj):
        return obj.results.count()

    def get_top_candidate_name(self, obj):
        top = obj.results.order_by("rank").first()
        return top.candidate.full_name if top else None

    def get_top_score(self, obj):
        top = obj.results.order_by("rank").first()
        return round(top.final_score, 1) if top else None
