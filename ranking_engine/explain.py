"""Explainable reasoning generation from candidate facts only."""
from __future__ import annotations

from typing import Dict, List


def _sanitize_csv(text: str) -> str:
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def _interview_questions(missing: List[str], matched: List[str], title: str, job_title: str | None = None) -> List[str]:
    if job_title is None:
        job_title = "requested role"
        
    questions: List[str] = []
    # Generic questions based on missing skills
    for m in missing[:2]:
        m_name = m.replace("_", " ")
        questions.append(f"Can you walk us through your experience with {m_name} and how you've applied it in past projects?")
        
    # Generic questions based on matched skills
    for m in matched[:1]:
        m_name = m.replace("_", " ")
        questions.append(f"You list {m_name} in your profile — describe a concrete challenge you solved using this technology.")
        
    # Default fallback
    if len(questions) < 3:
        questions.append(f"What key achievements in your career as a {title} make you a strong fit for this {job_title} role?")
        
    return questions[:3]


def build_full_explanation(
    candidate: Dict,
    rank: int,
    features: Dict,
    semantic_pct: float,
    job_struct: Dict | None = None,
) -> Dict:
    if job_struct is None:
        try:
            from .jd import load_job_description
            job_struct = load_job_description()
        except Exception:
            job_struct = {}
            
    job_title = job_struct.get("title", "requested role")
    
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    years = float(profile.get("years_of_experience", 0) or 0)
    title = profile.get("current_title", "Engineer")
    company = profile.get("current_company", "")
    location = profile.get("location", "")

    skill_f = features.get("skill", {})
    exp_f = features.get("experience", {})
    beh_f = features.get("behavior", {})
    rec_f = features.get("recruiter", {})
    career_f = features.get("career", {})
    domain_f = features.get("domain", {})
    edu_f = features.get("education", {})

    matched = skill_f.get("matched_skills", [])
    missing = skill_f.get("missing_skills", [])

    strengths: List[str] = []
    weaknesses: List[str] = []
    risks: List[str] = []

    if matched:
        strengths.append(f"Matches required stack areas: {', '.join(matched[:4])}")
    if exp_f.get("production_score", 0) >= 0.6:
        strengths.append("Career history shows strong relevant execution signals")
    if domain_f.get("tier") == "strong":
        strengths.append(f"Semantic profile aligns with {job_title}")
    if rec_f.get("location_score", 0) >= 0.85:
        strengths.append(f"Location fit: {location}")
    if signals.get("open_to_work_flag"):
        strengths.append("Marked open to work on Redrob")
    if beh_f.get("summary_parts"):
        strengths.append("Active recruiter engagement signals")

    if missing:
        weaknesses.append(f"Gaps vs JD: {', '.join(missing[:3])}")
    if exp_f.get("consulting_penalty", 0) > 0.1:
        weaknesses.append("Consulting-heavy career background")
    notice = rec_f.get("notice_days", signals.get("notice_period_days", 0))
    if notice and notice > 60:
        weaknesses.append(f"{notice}-day notice period")
    if beh_f.get("recency", 1) < 0.4:
        weaknesses.append("Low recent platform activity")

    if features.get("honeypot_penalty", 0) > 0.3:
        risks.append("Profile consistency flags detected")
    if domain_f.get("tier") == "adjacent":
        risks.append(f"Adjacent career profile — verify depth for {job_title}")
    if not signals.get("verified_email") or not signals.get("verified_phone"):
        risks.append("Incomplete verification on Redrob")

    confidence = 55.0
    confidence += min(20, len(matched) * 4)
    confidence += min(10, semantic_pct / 10)
    confidence += 8 if domain_f.get("tier") == "strong" else 0
    confidence -= len(weaknesses) * 4
    confidence -= len(risks) * 5
    confidence = max(35.0, min(95.0, confidence))

    risk_level = "low" if confidence >= 75 and not risks else ("medium" if confidence >= 55 else "high")

    why_selected = (
        f"{title} with {years:.1f} years experience"
        + (f" at {company}" if company else "")
        + f"; semantic fit {semantic_pct:.0f}/100"
        + (f"; domain alignment {domain_f.get('tier', 'moderate')}" if domain_f else "")
        + "."
    )

    career_growth = (
        "Ascending career with increasing responsibility"
        if career_f.get("trajectory") == "ascending"
        else f"Career pattern: {career_f.get('trajectory', 'stable')} (avg tenure {career_f.get('avg_tenure_months', 0):.0f} months)"
    )

    behaviour_summary = (
        f"Response rate {signals.get('recruiter_response_rate', 0):.0%}, "
        f"interview completion {signals.get('interview_completion_rate', 0):.0%}, "
        f"profile completeness {signals.get('profile_completeness_score', 0):.0f}/100"
    )
    if beh_f.get("summary_parts"):
        behaviour_summary += "; " + ", ".join(beh_f["summary_parts"])

    if rank <= 25:
        interview_rec = "Strong Fit — prioritize for recruiter screen"
    elif rank <= 60:
        interview_rec = "Moderate Fit — screen if pipeline allows"
    else:
        interview_rec = "Weak Fit — backup candidate"

    summary = generate_reasoning(candidate, rank, features, semantic_pct, job_struct)

    cert_f = edu_f.get("certifications", {})
    learning_path = []
    for gap in missing[:2]:
        learning_path.append(f"Deepen hands-on experience with {gap.replace('_', ' ')}")

    return {
        "why_selected": why_selected,
        "why_rejected": "; ".join(weaknesses[:2]) if rank > 50 and weaknesses else "",
        "strengths": strengths[:6],
        "weaknesses": weaknesses[:6],
        "matching_skills": matched[:8],
        "missing_skills": missing[:6],
        "career_growth": career_growth,
        "behaviour_summary": behaviour_summary,
        "recruiter_signals": {
            "response_rate": signals.get("recruiter_response_rate"),
            "saved_by_recruiters_30d": signals.get("saved_by_recruiters_30d"),
            "search_appearance_30d": signals.get("search_appearance_30d"),
            "notice_period_days": signals.get("notice_period_days"),
        },
        "risk_factors": risks[:4],
        "risk_level": risk_level,
        "confidence_score": round(confidence, 1),
        "interview_questions": _interview_questions(missing, matched, title, job_title),
        "interview_recommendation": interview_rec,
        "learning_path": learning_path,
        "domain_alignment": domain_f,
        "certifications": cert_f.get("relevant", []) if isinstance(cert_f, dict) else [],
        "summary": summary,
    }


def generate_reasoning(
    candidate: Dict,
    rank: int,
    features: Dict,
    semantic_pct: float,
    job_struct: Dict | None = None,
) -> str:
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    years = float(profile.get("years_of_experience", 0) or 0)
    title = profile.get("current_title", "Engineer")
    company = profile.get("current_company", "")
    location = profile.get("location", "")

    skill_f = features.get("skill", {})
    exp_f = features.get("experience", {})
    beh_f = features.get("behavior", {})
    rec_f = features.get("recruiter", {})
    career_f = features.get("career", {})

    matched = skill_f.get("matched_skills", [])[:4]
    missing = skill_f.get("missing_skills", [])[:2]

    parts1 = f"{title} with {years:.1f} years of experience"
    if company:
        parts1 += f" at {company}"
    parts1 += "."

    if matched:
        parts2 = f"Strong alignment on {', '.join(matched[:3])}"
        if exp_f.get("production_score", 0) >= 0.6:
            parts2 += " with strong execution signals in career history"
        parts2 += "."
    else:
        parts2 = "Partial technical overlap with JD requirements."

    concerns: List[str] = []
    if missing:
        concerns.append(f"gaps in {', '.join(missing)}")
    notice = rec_f.get("notice_days", signals.get("notice_period_days", 0))
    if notice and notice > 60:
        concerns.append(f"{notice}-day notice period")
    if exp_f.get("consulting_penalty", 0) > 0.1:
        concerns.append("heavy consulting background")
    if beh_f.get("recency", 1) < 0.4:
        concerns.append("low recent platform activity")

    parts3 = ""
    if location:
        loc_note = location
        if rec_f.get("location_score", 0) >= 0.9:
            loc_note += " (preferred location)"
        elif signals.get("willing_to_relocate"):
            loc_note += "; willing to relocate"
        parts3 = f"Located in {loc_note}."

    if career_f.get("trajectory") == "ascending":
        growth = "Career trajectory shows progression into senior responsibilities."
    else:
        growth = f"Career pattern: {career_f.get('trajectory', 'stable')}."

    if concerns:
        concern_text = "Concerns: " + "; ".join(concerns) + "."
    else:
        concern_text = f"Recruiter signals solid (response {signals.get('recruiter_response_rate', 0):.0%}, semantic fit {semantic_pct:.0f}/100)."

    if rank <= 10:
        tone = concern_text
    elif rank <= 50:
        tone = concern_text if concerns else f"Good fit overall; semantic similarity {semantic_pct:.0f}/100."
    else:
        tone = concern_text if concerns else "Adjacent fit — included based on partial skill and engagement signals."

    reasoning = f"{parts1} {parts2} {parts3} {growth} {tone}"
    return _sanitize_csv(" ".join(reasoning.split()))
