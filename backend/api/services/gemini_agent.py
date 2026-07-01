from __future__ import annotations

import json
from typing import Any
from django.conf import settings


def _build_prompt(job_struct: dict, candidate: Any, scores: dict) -> str:
    return (
        f"You are an expert recruiter evaluating a candidate for a job.\n"
        f"Job requirements:\n{json.dumps(job_struct, indent=2)}\n"
        f"Candidate profile:\nName: {candidate.full_name}\n"
        f"Profile: {candidate.profile_text}\n"
        f"Skills: {candidate.skills}\n"
        f"Years experience: {candidate.years_experience}\n"
        f"GitHub: {candidate.github_url}\n"
        f"Open to work: {'yes' if candidate.open_to_work else 'no'}\n"
        f"Scores:\n{json.dumps(scores, indent=2)}\n"
        f"Output only valid JSON with keys: llm_score, recommendation, strengths, weaknesses, missing_skills, recruiter_summary.\n"
        f"Recommendation should be one of: Strong Fit, Moderate Fit, Weak Fit.\n"
    )


def _fallback_recruiter_analysis(job_struct: dict, candidate: Any, scores: dict) -> dict:
    llm_score = (scores["semantic_score"] * 0.35 + scores["skill_score"] * 0.25 + scores["experience_score"] * 0.15 + scores["recruitability_score"] * 0.15) / 0.9
    llm_score = max(0.0, min(100.0, llm_score))
    recommendation = "Moderate Fit"
    if llm_score >= 75:
        recommendation = "Strong Fit"
    elif llm_score < 45:
        recommendation = "Weak Fit"
    strengths = []
    weaknesses = []
    if scores["skill_score"] >= 75:
        strengths.append("Skill set closely matches the job requirements.")
    if scores["experience_score"] >= 70:
        strengths.append("Shows strong relevant experience.")
    if scores["recruitability_score"] >= 70:
        strengths.append("High recruiter engagement and availability.")
    if scores["semantic_score"] >= 65:
        strengths.append("Profile is semantically aligned with the job description.")
    if scores["skill_score"] < 50:
        weaknesses.append("Several required skills are missing or underdeveloped.")
    if scores["experience_score"] < 50:
        weaknesses.append("May lack sufficient relevant experience.")
    if scores["recruitability_score"] < 50:
        weaknesses.append("Recruitability signals are weak.")
    missing_skills = job_struct.get("required_skills", [])
    recruiter_summary = (
        f"Candidate {candidate.full_name} appears to be a {recommendation.lower()} for the role. "
        f"Skill score is {scores['skill_score']:.1f}, experience is {scores['experience_score']:.1f}, "
        f"recruitability is {scores['recruitability_score']:.1f}."
    )
    return {
        "llm_score": float(round(llm_score, 2)),
        "recommendation": recommendation,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "missing_skills": missing_skills,
        "recruiter_summary": recruiter_summary,
    }


def _parse_llm_output(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        # try to locate JSON substring
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    return {}


def call_gemini_recruiter(job_struct: dict, candidate: Any, scores: dict) -> dict:
    prompt = _build_prompt(job_struct, candidate, scores)
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            response = genai.generate_text(model="gemini-1.0", prompt=prompt, temperature=0.2)
            text = getattr(response, "text", None)
            if text is None:
                text = str(response)
            parsed = _parse_llm_output(text)
            if parsed and parsed.get("llm_score") is not None:
                return parsed
        except Exception:
            pass
    return _fallback_recruiter_analysis(job_struct, candidate, scores)
