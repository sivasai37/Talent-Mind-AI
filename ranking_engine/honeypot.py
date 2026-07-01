"""Honeypot and trap-candidate detection."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

from .config import CONSULTING_FIRMS

REFERENCE_DATE = date(2026, 6, 25)

RETRIEVAL_KEYWORDS = [
    "faiss", "embedding", "vector", "ndcg", "map", "mrr", "pinecone", "milvus",
    "weaviate", "qdrant", "sentence-transformer", "rag", "retrieval", "ranking",
    "elasticsearch", "opensearch", "hybrid search",
]

ENGINEERING_TITLE_HINTS = [
    "engineer", "scientist", "research", "developer", "architect", "ml", "ai", "nlp", "data",
]


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def detect_honeypot(candidate: Dict, fast_mode: bool = False) -> Tuple[bool, List[str], float]:
    """
    Return (is_hard_honeypot, reasons, penalty_score).
    Hard honeypots are excluded from retrieval pool; soft traps get heavy penalty.
    """
    reasons: List[str] = []
    penalty = 0.0

    profile = candidate.get("profile", {})
    years_exp = float(profile.get("years_of_experience", 0) or 0)
    title = (profile.get("current_title") or "").lower()
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])
    education = candidate.get("education", [])

    expert_zero = sum(
        1 for s in skills
        if s.get("proficiency") in ("expert", "advanced") and int(s.get("duration_months", 0) or 0) == 0
    )
    if expert_zero >= 1:
        reasons.append("expert_skill_zero_duration")
        return True, reasons, 1.0

    for cert in candidate.get("certifications", []):
        year = int(cert.get("year", 0) or 0)
        if year > 2026:
            reasons.append(f"future_certification_{year}")
            return True, reasons, 1.0

    if not fast_mode:
        for job in career:
            dur_months = int(job.get("duration_months", 0) or 0)
            if dur_months / 12.0 > years_exp + 0.5:
                reasons.append("job_duration_exceeds_total_experience")
                return True, reasons, 1.0

            start = _parse_date(job.get("start_date"))
            end = _parse_date(job.get("end_date")) or REFERENCE_DATE
            if start:
                elapsed_months = round((end - start).days / 30.4375)
                if dur_months > elapsed_months + 3:
                    reasons.append("duration_exceeds_elapsed_time")
                    return True, reasons, 1.0

        if career and education:
            edu_years = [e.get("start_year") for e in education if e.get("start_year")]
            job_years = []
            for job in career:
                sd = _parse_date(job.get("start_date"))
                if sd:
                    job_years.append(sd.year)
            if edu_years and job_years and min(edu_years) - min(job_years) > 6:
                reasons.append("employment_before_education")
                return True, reasons, 1.0

        # Overlapping full-time roles spanning implausible total months
        intervals: List[Tuple[date, date]] = []
        for job in career:
            start = _parse_date(job.get("start_date"))
            if not start:
                continue
            end = _parse_date(job.get("end_date")) or REFERENCE_DATE
            intervals.append((start, end))
        if len(intervals) >= 2:
            total_job_days = sum((e - s).days for s, e in intervals)
            span_start = min(s for s, _ in intervals)
            span_end = max(e for _, e in intervals)
            span_days = max(1, (span_end - span_start).days)
            if total_job_days > span_days * 1.55 and span_days > 400:
                reasons.append("impossible_overlapping_jobs")
                penalty = max(penalty, 0.85)

    skill_names = [str(s.get("name", "")).lower() for s in skills]
    ai_keyword_hits = sum(1 for name in skill_names if any(k in name for k in RETRIEVAL_KEYWORDS))
    if ai_keyword_hits >= 6 and not any(h in title for h in ENGINEERING_TITLE_HINTS):
        reasons.append("keyword_stuffer")
        penalty = max(penalty, 0.95)

    if not fast_mode:
        if career and all(
            any(firm in (j.get("company") or "").lower() for firm in CONSULTING_FIRMS)
            for j in career
        ):
            reasons.append("consulting_only_career")
            penalty = max(penalty, 0.70)

    # Implausible total skill duration vs experience
    total_skill_months = sum(int(s.get("duration_months", 0) or 0) for s in skills)
    if years_exp > 0 and total_skill_months > years_exp * 12 * 2.5 and len(skills) > 8:
        reasons.append("implausible_skill_durations")
        penalty = max(penalty, 0.80)

    is_hard = penalty >= 0.99
    return is_hard, reasons, penalty

