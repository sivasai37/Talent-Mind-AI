from __future__ import annotations

from typing import List, Dict, Any

import numpy as np
from django.conf import settings

from ..models import Candidate, CandidateEmbedding
from .embeddings import get_engine
from .vector_store import rebuild_store, get_store
from .skill_engine import compute_skill_fit
from .experience_engine import compute_experience_fit
from .behavioral_engine import compute_recruitability_score
from .gemini_agent import call_gemini_recruiter
from .jd_understanding import analyze_job_description


def _candidate_text(candidate: Candidate) -> str:
    parts = [candidate.full_name, candidate.profile_text, candidate.skills or ""]
    if candidate.github_url:
        parts.append(candidate.github_url)
    return " \n ".join([p for p in parts if p])


def build_index() -> None:
    """Compute embeddings for all candidates and rebuild the in-memory FAISS store."""
    engine = get_engine()
    candidates = list(Candidate.objects.all())
    if not candidates:
        return
    texts = [_candidate_text(c) for c in candidates]
    vecs = engine.encode(texts)
    id_vec_pairs = []
    for c, v in zip(candidates, vecs):
        # persist embedding for portability
        CandidateEmbedding.objects.update_or_create(candidate=c, defaults={"vector": v.tolist()})
        id_vec_pairs.append((c.id, v))
    rebuild_store(id_vec_pairs)


def _skill_score(required: str, candidate_skills: str) -> float:
    if not required:
        return 0.5
    req = {t.strip().lower() for t in required.split(",") if t.strip()}
    cand = {t.strip().lower() for t in candidate_skills.split(",") if t.strip()}
    if not req:
        return 0.5
    matched = len(req & cand)
    return float(matched) / max(1.0, len(req))


def _experience_score(min_exp: float, cand_exp: float) -> float:
    if min_exp <= 0:
        return 0.5
    if cand_exp >= min_exp:
        return 1.0
    return max(0.0, cand_exp / min_exp)


def _recruitability_score(candidate: Candidate) -> float:
    parts = [
        candidate.recruiter_response_rate / 100.0,
        candidate.interview_completion_rate / 100.0,
        candidate.offer_acceptance_rate / 100.0,
        candidate.profile_completeness / 100.0,
        1.0 if candidate.open_to_work else 0.5,
    ]
    return float(sum(parts) / len(parts))


def search_job(job_text: str, job_required_skills: str | None = None, min_experience: float | None = None, top_k: int = 10, job_struct: dict | None = None) -> List[Dict[str, Any]]:
    """Return ranked candidate list with explainability and scores.

    Accepts either raw parameters or a `job_struct` as produced by `analyze_job_description`.
    """
    engine = get_engine()
    store = get_store()
    qvec = engine.encode_one(job_text)
    sem_results = store.search(qvec, top_k=top_k)
    # sem_results: List[(candidate_id, score)]
    candidates = {c.id: c for c in Candidate.objects.filter(id__in=[i for i, _ in sem_results])}
    results = []
    weights = getattr(settings, "RANKING_WEIGHTS", {})
    # normalize inputs from job_struct when provided
    if job_struct is not None:
        req_skills = job_struct.get("required_skills", [])
        try:
            min_exp = float(job_struct.get("experience_years") or 0.0)
        except Exception:
            min_exp = 0.0
    else:
        req_skills = [] if job_required_skills is None else [s.strip() for s in job_required_skills.split(",") if s.strip()]
        min_exp = 0.0 if min_experience is None else float(min_experience)

    for cid, sem_score in sem_results:
        cand = candidates.get(cid)
        if cand is None:
            continue
        # semantic score (map cosine ~[-1,1] to [0,100])
        sem_pct = max(0.0, float(sem_score)) * 100.0
        # skill engine returns score (0-100) and details
        skill_pct, skill_details = compute_skill_fit(req_skills, cand.skills or "")
        exp_res = compute_experience_fit(min_exp, cand.years_experience, career_history=[{
            "title": j.title,
            "company": j.company,
            "start_date": j.start_date.isoformat() if j.start_date else None,
            "end_date": j.end_date.isoformat() if j.end_date else None,
            "description": j.description,
        } for j in cand.jobs.all()])
        exp_pct = float(exp_res.get("score", 0.0))
        rec_res = compute_recruitability_score(cand)
        rec_pct = float(rec_res.get("score", 0.0))
        scores = {
            "semantic_score": sem_pct,
            "skill_score": skill_pct,
            "experience_score": exp_pct,
            "recruitability_score": rec_pct,
        }
        llm_analysis = call_gemini_recruiter(job_struct or {}, cand, scores)
        llm_pct = float(llm_analysis.get("llm_score", 0.0))
        # normalize LLM score to 0-100 if the model returned 0-1
        if llm_pct <= 1.0:
            llm_pct = llm_pct * 100.0

        final = (
            sem_pct * weights.get("semantic", 0.35)
            + skill_pct * weights.get("skill", 0.25)
            + exp_pct * weights.get("experience", 0.15)
            + rec_pct * weights.get("recruitability", 0.15)
            + llm_pct * weights.get("llm", 0.10)
        )

        strengths = []
        weaknesses = []
        if skill_pct >= 70:
            strengths.append("Strong skill fit")
        elif skill_pct >= 40:
            strengths.append("Partial skill match")
        else:
            weaknesses.append("Skill gap vs required")

        if exp_pct >= 70:
            strengths.append("Experience aligned")
        else:
            weaknesses.append("Experience mismatch or insufficient years")

        if rec_pct >= 60:
            strengths.append("High recruitability signals")
        else:
            weaknesses.append("Low recruitability signals")

        # combine LLM-driven explanations
        strengths.extend(llm_analysis.get("strengths", []))
        weaknesses.extend(llm_analysis.get("weaknesses", []))

        # build explainability text blocks
        semantic_explanation = f"Semantic similarity score {sem_pct:.1f} (higher indicates closer match to the job description)."
        skill_explanation = skill_details.get("explanation") if isinstance(skill_details, dict) else "Skill matching computed from required vs candidate skills."
        if not skill_explanation:
            skill_explanation = f"Skill score {skill_pct:.1f} based on matching required skills."
        experience_explanation = exp_res.get("summary") if isinstance(exp_res, dict) else f"Experience score {exp_pct:.1f}."
        if not experience_explanation:
            experience_explanation = f"Experience score {exp_pct:.1f}."
        behavioral_explanation = rec_res.get("summary") if isinstance(rec_res, dict) else f"Recruitability score {rec_pct:.1f}."
        gemini_explanation = llm_analysis.get("recruiter_summary", "")

        results.append(
            {
                "candidate_id": cid,
                "full_name": cand.full_name,
                "semantic_score": float(sem_pct),
                "skill_score": float(skill_pct),
                "experience_score": float(exp_pct),
                "recruitability_score": float(rec_pct),
                "llm_score": float(llm_pct),
                "final_score": float(final),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "missing_skills": llm_analysis.get("missing_skills", skill_details.get("missing", [])),
                "recruiter_ai": llm_analysis,
                "skill_details": skill_details,
                "experience_details": exp_res.get("details", {}),
                "recruitability_details": rec_res.get("details", {}),
                "semantic_explanation": semantic_explanation,
                "skill_explanation": skill_explanation,
                "experience_explanation": experience_explanation,
                "behavioral_explanation": behavioral_explanation,
                "gemini_explanation": gemini_explanation,
            }
        )
    # sort by final_score desc
    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results
