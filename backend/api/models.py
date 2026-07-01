from django.db import models


class Candidate(models.Model):
    full_name = models.CharField(max_length=255, db_index=True)
    profile_text = models.TextField(blank=True, default="")
    skills = models.TextField(blank=True, default="")
    years_experience = models.FloatField(default=0.0)
    github_url = models.URLField(blank=True, null=True)
    open_to_work = models.BooleanField(default=False)
    recruiter_response_rate = models.FloatField(default=0.0)
    interview_completion_rate = models.FloatField(default=0.0)
    offer_acceptance_rate = models.FloatField(default=0.0)
    profile_completeness = models.FloatField(default=0.0)
    salary_expectation = models.CharField(max_length=128, blank=True, default="")
    relocation_preference = models.CharField(max_length=128, blank=True, default="")
    certifications = models.TextField(blank=True, default="")
    education_level = models.CharField(max_length=128, blank=True, default="")
    location = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
            models.Index(fields=["years_experience"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Candidate({self.pk}) {self.full_name}"


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    required_skills = models.TextField(blank=True, default="")
    preferred_skills = models.TextField(blank=True, default="")
    min_experience = models.FloatField(default=0.0)
    industry = models.CharField(max_length=128, blank=True, default="")
    behavioral_expectations = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Job({self.pk}) {self.title}"


class CandidateEmbedding(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="embedding")
    vector = models.JSONField()  # store list[float] for portability
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Embedding({self.candidate_id}) len={len(self.vector)}"


class CandidateJob(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="jobs")
    company = models.CharField(max_length=255, blank=True, default="")
    title = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, default="")

    def __str__(self) -> str:  # pragma: no cover
        return f"Job({self.pk}) {self.title} @ {self.company}"


class RankingJob(models.Model):
    title = models.CharField(max_length=255, blank=True, default="")
    job_description = models.TextField(blank=True, default="")
    job_analysis = models.JSONField(default=dict)
    role_type = models.CharField(max_length=64, blank=True, default="general")
    weights_used = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"RankingJob({self.pk}) {self.title or 'Unnamed'}"


class RankingResult(models.Model):
    RISK_LEVELS = [
        ("low", "Low Risk"),
        ("medium", "Medium Risk"),
        ("high", "High Risk"),
    ]

    ranking_job = models.ForeignKey(RankingJob, on_delete=models.CASCADE, related_name="results")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField()
    semantic_score = models.FloatField(default=0.0)
    skill_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    recruitability_score = models.FloatField(default=0.0)
    llm_score = models.FloatField(default=0.0)
    final_score = models.FloatField(default=0.0)
    potential_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    risk_level = models.CharField(max_length=16, choices=RISK_LEVELS, default="medium")
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    learning_path = models.JSONField(default=list)
    interview_questions = models.JSONField(default=list)
    future_roles = models.JSONField(default=list)
    growth_forecast = models.JSONField(default=dict)
    salary_fit = models.JSONField(default=dict)
    why_selected = models.TextField(blank=True, default="")
    why_rejected = models.TextField(blank=True, default="")
    role_fit_analysis = models.TextField(blank=True, default="")
    recruiter_recommendation = models.TextField(blank=True, default="")
    recruiter_summary = models.TextField(blank=True, default="")
    payload = models.JSONField(default=dict)

    class Meta:
        indexes = [
            models.Index(fields=["ranking_job", "rank"]),
            models.Index(fields=["final_score"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"RankingResult({self.pk}) {self.candidate.full_name} rank={self.rank}"
