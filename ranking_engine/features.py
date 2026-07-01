"""Feature engineering for hybrid ranking."""
from __future__ import annotations

import math
import re
from datetime import date
from typing import Dict, List, Tuple

from .config import (
    AI_TITLE_KEYWORDS,
    CONSULTING_FIRMS,
    GOOD_LOCATIONS,
    IDEAL_EXP_MAX,
    IDEAL_EXP_MIN,
    NON_TECH_TITLES,
    PREFERRED_LOCATIONS,
    PRODUCT_INDICATORS,
)
from .jd import REQUIRED_SKILL_CLUSTERS, PREFERRED_SKILL_CLUSTERS

PROFICIENCY_MAP = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.82, "expert": 0.95}
TIER_MAP = {"tier_1": 1.0, "tier_2": 0.85, "tier_3": 0.65, "tier_4": 0.45, "unknown": 0.50}
REFERENCE_DATE = date(2026, 6, 25)


def _norm_skill(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def _candidate_skill_index(skills: List[Dict]) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for s in skills:
        key = _norm_skill(str(s.get("name", "")))
        if key:
            out[key] = s
    return out


def _cluster_match(skill_index: Dict[str, Dict], aliases: List[str]) -> Tuple[bool, float, str | None]:
    best_score = 0.0
    best_name = None
    for alias in aliases:
        alias_l = alias.lower()
        for name, info in skill_index.items():
            if alias_l == name or alias_l in name or name in alias_l:
                prof = PROFICIENCY_MAP.get(str(info.get("proficiency", "")).lower(), 0.5)
                dur = int(info.get("duration_months", 0) or 0)
                dur_bonus = min(1.0, dur / 24.0) * 0.15
                endorse = min(1.0, math.tanh(math.log1p(int(info.get("endorsements", 0) or 0)) / 3))
                score = prof * 0.7 + dur_bonus + endorse * 0.15
                if score > best_score:
                    best_score = score
                    best_name = name
    return best_score > 0.2, best_score, best_name


def compute_skill_features(candidate: Dict, job_struct: Dict, signals: Dict, fast_mode: bool = False) -> Dict:
    from .embeddings import get_cached_engine
    from .skills import match_skill, normalize_skill, is_alias
    
    engine = get_cached_engine()
    assessments = signals.get("skill_assessment_scores", {}) or {}

    matched_required: List[str] = []
    missing_required: List[str] = []
    required_scores: List[float] = []

    for cluster in job_struct.get("required_skills", []):
        hit, score, matched_name = match_skill(cluster, candidate, engine, fast_mode=fast_mode)
        if hit:
            matched_required.append(matched_name or cluster)
            # Assessment score boost if the skill matches
            assess_boost = 0.0
            cluster_norm = normalize_skill(cluster)
            matched_norm = normalize_skill(matched_name) if matched_name else ""
            for ak, av in assessments.items():
                ak_norm = normalize_skill(ak)
                if ak_norm == cluster_norm or is_alias(ak_norm, cluster_norm) or (matched_norm and (ak_norm == matched_norm or is_alias(ak_norm, matched_norm))):
                    assess_boost = max(assess_boost, float(av) / 100.0)
            required_scores.append(min(1.0, score + assess_boost * 0.2))
        else:
            missing_required.append(cluster)

    preferred_hits = 0
    for cluster in job_struct.get("preferred_skills", []):
        hit, _, _ = match_skill(cluster, candidate, engine, fast_mode=fast_mode)
        if hit:
            preferred_hits += 1

    n_req = max(1, len(job_struct.get("required_skills", [])))
    base = len(matched_required) / n_req
    prof_avg = sum(required_scores) / max(1, len(required_scores))
    preferred_bonus = min(0.15, preferred_hits * 0.04)
    
    # Required skills match prioritization penalty - use ratio ** 4.0 for steeper drop on missing required skills
    ratio = len(matched_required) / n_req
    penalty_mult = ratio ** 4.0
    score = min(1.0, (base * 0.55 + prof_avg * 0.40) * penalty_mult + preferred_bonus)

    return {
        "score": score * 100.0,
        "matched_skills": matched_required,
        "missing_skills": missing_required,
        "preferred_hits": preferred_hits,
    }



def compute_publication_features(candidate: Dict, job_struct: Dict) -> Dict:
    # Gather candidate's text
    profile = candidate.get("profile", {})
    text_parts = [
        profile.get("summary", "") or "",
        profile.get("headline", "") or "",
        profile.get("current_title", "") or "",
    ]
    for job in candidate.get("career_history", []):
        text_parts.append(job.get("title", "") or "")
        text_parts.append(job.get("description", "") or "")
    for edu in candidate.get("education", []):
        text_parts.append(edu.get("field_of_study", "") or "")
        text_parts.append(edu.get("degree", "") or "")
        text_parts.append(edu.get("institution", "") or "")
    for skill in candidate.get("skills", []):
        text_parts.append(skill.get("name", "") or "")
        
    full_text = " ".join(text_parts).lower()
    
    # Check for publications keywords
    keywords_canonical = {"neurips": "NeurIPS", "icml": "ICML", "acl": "ACL", "cvpr": "CVPR", "iclr": "ICLR", "eccv": "ECCV"}
    found = [keywords_canonical[kw] for kw in keywords_canonical if re.search(rf"\b{re.escape(kw)}\b", full_text)]
    
    preferred_pubs = [p.lower() for p in job_struct.get("preferred_publications", [])]
    if preferred_pubs:
        matched = [p for p in found if p in preferred_pubs]
        score = 100.0 if matched else 0.0
    else:
        score = 100.0 if found else 0.0
        
    return {
        "score": score,
        "found_publications": found,
    }


def compute_title_relevance(candidate_title: str, job_title: str, engine) -> float:
    from .text_builder import normalize_title
    c_title = normalize_title(candidate_title)
    j_title = normalize_title(job_title)
    if not c_title or not j_title:
        return 0.25
    c_vec = engine.encode_one(c_title)
    j_vec = engine.encode_one(j_title)
    sim = float(c_vec @ j_vec)
    # Cosine sim usually ranges from 0.2 to 0.9. Map 0.2-0.9 to 0.1-1.0
    return max(0.1, min(1.0, (sim - 0.2) / 0.7))


def compute_title_relevance_fast(candidate_title: str, job_title: str) -> float:
    from .text_builder import normalize_title
    c_words = set(normalize_title(candidate_title).lower().split())
    j_words = set(normalize_title(job_title).lower().split())
    if not c_words or not j_words:
        return 0.25
    overlap = len(c_words & j_words) / len(j_words)
    return 0.25 + 0.75 * overlap


def _title_relevance(title: str) -> float:
    return compute_title_relevance_fast(title, "Senior AI Engineer")


def compute_experience_features(
    candidate: Dict, 
    job_struct: Dict, 
    engine = None, 
    fast_mode: bool = False
) -> Dict:
    profile = candidate.get("profile", {})
    years = float(profile.get("years_of_experience", 0) or 0)
    title = profile.get("current_title", "")
    career = candidate.get("career_history", [])

    exp_min = float(job_struct.get("experience_min", IDEAL_EXP_MIN))
    exp_max = float(job_struct.get("experience_max", IDEAL_EXP_MAX))

    if years < exp_min:
        years_score = max(0.2, years / exp_min)
    elif years <= exp_max:
        years_score = 1.0
    elif years <= exp_max + 4:
        years_score = max(0.55, 1.0 - (years - exp_max) * 0.08)
    else:
        years_score = 0.35

    # Calculate title score dynamically
    job_title = job_struct.get("title", "")
    title_score = compute_title_relevance_fast(title, job_title)

    if fast_mode:
        combined = years_score * 0.40 + title_score * 0.60
        return {
            "score": combined * 100.0,
            "years": years,
            "title_score": title_score,
            "product_hits": 0,
            "production_score": 0.0,
            "leadership": False,
            "consulting_penalty": 0.0,
        }

    # 1. Seniority, Tech vs Non-tech dynamic inference
    exp_min_float = float(exp_min)
    is_leadership = any(k in job_title.lower() for k in ("lead", "manager", "director", "head", "vp", "chief", "cto", "architect")) or exp_min_float >= 8.0
    is_tech = not any(k in job_title.lower() for k in ("marketing", "sales", "hr", "human resource", "recruiter", "people", "designer", "illustrator", "creative", "product manager", "project manager", "scrum master"))
    
    if engine is None:
        from .embeddings import get_cached_engine
        engine = get_cached_engine()
    title_score = compute_title_relevance(title, job_title, engine)

    product_hits = 0
    consulting_hits = 0
    for job in career:
        comp = (job.get("company") or "").lower()
        if any(p in comp for p in PRODUCT_INDICATORS):
            product_hits += 1
        if any(c in comp for c in CONSULTING_FIRMS):
            consulting_hits += 1

    industry_score = min(1.0, product_hits / max(1, len(career)))
    
    # Consulting penalty is lighter for non-technical roles
    consulting_penalty = 0.0
    if career and consulting_hits == len(career):
        consulting_penalty = 0.40 if is_tech else 0.15
    elif consulting_hits > product_hits:
        consulting_penalty = 0.15 if is_tech else 0.05

    # Target success keywords tailored to technical vs non-technical roles
    if is_tech:
        success_keywords = ("production", "deploy", "ship", "users", "scale", "serving", "pipeline", "architecture", "system")
    else:
        success_keywords = ("campaign", "manage", "hire", "leads", "revenue", "strategy", "ops", "recruiting", "sales", "budget", "client", "business")
        
    production_signals = 0
    for job in career:
        desc = (job.get("description") or "").lower()
        if any(k in desc for k in success_keywords):
            production_signals += 1
    production_score = min(1.0, production_signals / max(1, len(career)))

    # Leadership score relative to job requirements
    has_leadership_exp = any(
        any(k in (j.get("title") or "").lower() for k in ("senior", "lead", "principal", "staff", "manager", "director", "head"))
        for j in career
    )
    if is_leadership:
        leadership_score = 1.0 if has_leadership_exp else 0.3
    else:
        leadership_score = 1.0 if has_leadership_exp else 0.8

    combined = (
        years_score * 0.30
        + title_score * 0.40
        + industry_score * 0.12
        + production_score * 0.13
        + leadership_score * 0.05
        - consulting_penalty
    )
    combined = max(0.0, min(1.0, combined))

    return {
        "score": combined * 100.0,
        "years": years,
        "title_score": title_score,
        "product_hits": product_hits,
        "production_score": production_score,
        "leadership": has_leadership_exp,
        "consulting_penalty": consulting_penalty,
    }


def compute_career_features(candidate: Dict) -> Dict:
    career = candidate.get("career_history", [])
    if not career:
        return {"score": 40.0, "trajectory": "unknown"}

    tenures: List[float] = []
    title_levels: List[int] = []
    industries: List[str] = []

    level_rank = {
        "intern": 1, "junior": 2, "associate": 2, "engineer": 3,
        "senior": 4, "lead": 5, "staff": 5, "principal": 6, "manager": 5, "director": 6,
    }

    for job in career:
        start_s = job.get("start_date")
        end_s = job.get("end_date")
        try:
            start = date.fromisoformat(start_s) if start_s else None
            end = date.fromisoformat(end_s) if end_s else REFERENCE_DATE
            if start:
                tenures.append(max(0.0, (end - start).days / 30.4375))
        except ValueError:
            pass

        title = (job.get("title") or "").lower()
        level = 3
        for key, val in level_rank.items():
            if key in title:
                level = max(level, val)
        title_levels.append(level)
        industries.append((job.get("industry") or "").lower())

    avg_tenure = sum(tenures) / max(1, len(tenures))
    stability = min(1.0, avg_tenure / 30.0)

    progression = 0.0
    if len(title_levels) >= 2:
        progression = (title_levels[0] - title_levels[-1]) / max(1, len(title_levels) - 1)
        progression = max(0.0, min(1.0, progression / 2.0))

    # Penalize title-chasing (very short tenures repeatedly)
    short_jobs = sum(1 for t in tenures if t < 12)
    hop_penalty = min(0.4, short_jobs * 0.08)

    domain_consistency = 0.0
    if industries:
        top = max(set(industries), key=industries.count)
        domain_consistency = industries.count(top) / len(industries)

    combined = (
        stability * 0.35
        + progression * 0.35
        + domain_consistency * 0.20
        + (1.0 - hop_penalty) * 0.20
    )
    trajectory = "ascending" if progression > 0.35 else ("stable" if stability > 0.5 else "mixed")

    return {
        "score": max(0.0, min(1.0, combined)) * 100.0,
        "avg_tenure_months": avg_tenure,
        "progression": progression,
        "stability": stability,
        "trajectory": trajectory,
        "hop_penalty": hop_penalty,
    }


def compute_education_features(candidate: Dict) -> Dict:
    education = candidate.get("education", [])
    cert_f = compute_certification_features(candidate)
    if not education:
        return {
            "score": max(45.0, cert_f["score"] * 0.6),
            "tier": "unknown",
            "certifications": cert_f,
        }

    tiers = [TIER_MAP.get(str(e.get("tier", "unknown")), 0.5) for e in education]
    tier_score = max(tiers)

    tech_fields = 0
    for e in education:
        field = (e.get("field_of_study") or "").lower()
        degree = (e.get("degree") or "").lower()
        if any(k in field for k in ("computer", "software", "data", "machine", "electrical", "information")):
            tech_fields += 1
        if any(k in degree for k in ("b.e", "b.tech", "m.tech", "m.s", "phd", "bachelor", "master")):
            tech_fields += 0.5

    field_score = min(1.0, tech_fields / max(1, len(education)))
    edu_core = (tier_score * 0.6 + field_score * 0.4) * 100.0
    score = edu_core * 0.82 + cert_f["score"] * 0.18
    best_tier = max(education, key=lambda e: TIER_MAP.get(str(e.get("tier", "unknown")), 0.5))

    return {
        "score": score,
        "tier": best_tier.get("tier", "unknown"),
        "degree": best_tier.get("degree", ""),
        "field": best_tier.get("field_of_study", ""),
        "institution": best_tier.get("institution", ""),
        "certifications": cert_f,
    }


def compute_assessment_features(candidate: Dict, job_struct: Dict) -> Dict:
    from .skills import normalize_skill, is_alias
    
    signals = candidate.get("redrob_signals", {})
    assessments = signals.get("skill_assessment_scores", {}) or {}
    if not assessments:
        return {"score": 50.0, "hits": []}

    target_terms = []
    for cluster in job_struct.get("required_skills", []):
        target_terms.append(cluster)

    # Pre-normalize targets
    normalized_targets = [normalize_skill(t) for t in target_terms]

    hits: List[Tuple[str, float]] = []
    for skill_name, val in assessments.items():
        sn_norm = normalize_skill(skill_name)
        if any(t == sn_norm or is_alias(t, sn_norm) for t in normalized_targets):
            hits.append((skill_name, float(val)))

    if not hits:
        avg = sum(float(v) for v in assessments.values()) / len(assessments)
        return {"score": avg, "hits": []}

    avg_hit = sum(v for _, v in hits) / len(hits)
    return {"score": avg_hit, "hits": hits}



def compute_location_score(candidate: Dict) -> float:
    profile = candidate.get("profile", {})
    loc = (profile.get("location") or "").lower()
    signals = candidate.get("redrob_signals", {})
    relocate = bool(signals.get("willing_to_relocate", False))

    if any(p in loc for p in PREFERRED_LOCATIONS):
        return 1.0
    if any(g in loc for g in GOOD_LOCATIONS):
        return 0.75
    if relocate:
        return 0.65
    return 0.35


def compute_behavior_features(candidate: Dict) -> Dict:
    signals = candidate.get("redrob_signals", {})
    if not signals:
        return {"score": 40.0, "summary_parts": []}

    def _rate(key: str, default: float = 0.0) -> float:
        v = signals.get(key, default)
        if v is None:
            return default
        if isinstance(v, (int, float)) and v < 0:
            return 0.5
        return float(v)

    completeness = _rate("profile_completeness_score", 50) / 100.0
    response = min(1.0, _rate("recruiter_response_rate", 0))
    interview = min(1.0, _rate("interview_completion_rate", 0))
    offer = _rate("offer_acceptance_rate", 0.5)
    if offer < 0:
        offer = 0.5
    offer = min(1.0, offer)

    open_to_work = 1.0 if signals.get("open_to_work_flag") else 0.35
    github = signals.get("github_activity_score", -1)
    github_score = 0.0 if github is None or float(github) < 0 else min(1.0, float(github) / 100.0)

    search_app = min(1.0, math.tanh(math.log1p(int(signals.get("search_appearance_30d", 0) or 0)) / 4))
    saves = min(1.0, math.tanh(math.log1p(int(signals.get("saved_by_recruiters_30d", 0) or 0)) / 3))
    views = min(1.0, math.tanh(math.log1p(int(signals.get("profile_views_received_30d", 0) or 0)) / 4))
    apps = min(1.0, math.tanh(math.log1p(int(signals.get("applications_submitted_30d", 0) or 0)) / 3))
    connections = min(1.0, math.tanh(math.log1p(int(signals.get("connection_count", 0) or 0)) / 4))

    resp_hours = float(signals.get("avg_response_time_hours", 48) or 48)
    resp_time_score = max(0.0, 1.0 - min(resp_hours, 120) / 120.0)

    notice = int(signals.get("notice_period_days", 90) or 90)
    notice_score = 1.0 if notice <= 30 else (0.75 if notice <= 60 else (0.5 if notice <= 90 else 0.3))

    verified = sum([
        1.0 if signals.get("verified_email") else 0.0,
        1.0 if signals.get("verified_phone") else 0.0,
        1.0 if signals.get("linkedin_connected") else 0.0,
    ]) / 3.0

    last_active = signals.get("last_active_date")
    recency = 0.5
    if last_active:
        try:
            active = date.fromisoformat(str(last_active))
            days = (REFERENCE_DATE - active).days
            recency = max(0.1, 1.0 - min(days, 365) / 365.0)
        except ValueError:
            pass

    work_mode = str(signals.get("preferred_work_mode", "")).lower()
    mode_score = 1.0 if work_mode in ("hybrid", "flexible", "remote") else 0.7

    combined = (
        completeness * 0.10
        + response * 0.14
        + interview * 0.12
        + offer * 0.06
        + open_to_work * 0.10
        + github_score * 0.08
        + search_app * 0.06
        + saves * 0.06
        + views * 0.05
        + apps * 0.04
        + connections * 0.04
        + resp_time_score * 0.05
        + notice_score * 0.05
        + verified * 0.04
        + recency * 0.06
        + mode_score * 0.03
    )

    lang_f = compute_language_features(candidate)
    combined = combined * 0.96 + (lang_f["score"] / 100.0) * 0.04

    parts = []
    if open_to_work >= 0.9:
        parts.append("open to work")
    if recency >= 0.7:
        parts.append("recently active")
    if response >= 0.6:
        parts.append(f"response rate {response:.0%}")
    if saves > 0.3:
        parts.append("saved by recruiters")

    return {"score": min(1.0, combined) * 100.0, "summary_parts": parts, "recency": recency, "notice_days": notice}


def compute_recruiter_features(candidate: Dict) -> Dict:
    """Recruiter-facing availability and market signals."""
    signals = candidate.get("redrob_signals", {})
    behavior = compute_behavior_features(candidate)
    location_score = compute_location_score(candidate)

    salary = signals.get("expected_salary_range_inr_lpa", {}) or {}
    sal_min = float(salary.get("min", 0) or 0)
    sal_max = float(salary.get("max", 0) or 0)
    salary_mid = (sal_min + sal_max) / 2 if sal_max else sal_min
    salary_score = 0.7
    if 25 <= salary_mid <= 55:
        salary_score = 1.0
    elif salary_mid < 20 or salary_mid > 70:
        salary_score = 0.45

    combined = (
        behavior["score"] / 100.0 * 0.55
        + location_score * 0.25
        + salary_score * 0.20
    )
    return {
        "score": combined * 100.0,
        "location_score": location_score,
        "salary_mid_lpa": salary_mid,
        "notice_days": behavior.get("notice_days", 90),
    }


CERT_RELEVANCE_TERMS = [
    "machine learning", "deep learning", "aws", "azure", "google cloud", "gcp",
    "nlp", "tensorflow", "pytorch", "ml", "ai", "data", "python", "kubernetes",
]


def compute_certification_features(candidate: Dict, job_struct: Dict | None = None) -> Dict:
    certs = candidate.get("certifications", []) or []
    if not certs:
        return {"score": 45.0, "count": 0, "relevant": []}

    relevant = []
    for cert in certs:
        name = (cert.get("name") or "").lower()
        issuer = (cert.get("issuer") or "").lower()
        blob = f"{name} {issuer}"
        if any(term in blob for term in CERT_RELEVANCE_TERMS):
            relevant.append(cert.get("name", ""))

    relevance = len(relevant) / max(1, len(certs))
    count_score = min(1.0, len(certs) / 4.0)
    score = (relevance * 0.65 + count_score * 0.35) * 100.0
    return {"score": score, "count": len(certs), "relevant": relevant[:5]}


LANG_PROFICIENCY = {"basic": 0.4, "conversational": 0.65, "professional": 0.85, "native": 1.0}


def compute_language_features(candidate: Dict) -> Dict:
    languages = candidate.get("languages", []) or []
    if not languages:
        return {"score": 55.0, "english_proficiency": "unknown"}

    english_prof = "unknown"
    english_score = 0.5
    scores = []
    for lang in languages:
        name = (lang.get("language") or "").lower()
        prof = LANG_PROFICIENCY.get(str(lang.get("proficiency", "")).lower(), 0.5)
        scores.append(prof)
        if name == "english":
            english_prof = str(lang.get("proficiency", "unknown"))
            english_score = prof

    avg = sum(scores) / len(scores)
    combined = english_score * 0.7 + avg * 0.3
    return {
        "score": combined * 100.0,
        "english_proficiency": english_prof,
        "count": len(languages),
    }
