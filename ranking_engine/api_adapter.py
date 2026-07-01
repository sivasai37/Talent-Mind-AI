"""Unified production API — Django backend and offline ranker entry point."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import DEFAULT_CANDIDATES_PATH, ROLE_WEIGHTS
from .explain import build_full_explanation, generate_reasoning
from .index_manager import ensure_index, is_index_ready
from .jd import analyze_job_description
from .pipeline import rank_candidates, rank_candidates_online
from .text_builder import build_candidate_id


def detect_role_type(job_struct: dict, title: str = "") -> str:
    combined = (
        (title or "").lower()
        + " "
        + str(job_struct.get("title", "")).lower()
        + " "
        + " ".join(job_struct.get("required_skills", [])).lower()
    )
    if any(k in combined for k in ("research", "embedding", "retrieval", "ranking", "nlp", "llm")):
        return "research"
    if any(k in combined for k in ("manager", "director", "leadership", "head of")):
        return "leadership"
    if any(k in combined for k in ("backend", "django", "api", "server")):
        return "backend"
    if any(k in combined for k in ("data scientist", "analytics", "etl")):
        return "data"
    return job_struct.get("role", "research")


def get_role_weights(role_type: str) -> dict:
    return ROLE_WEIGHTS.get(role_type, ROLE_WEIGHTS.get("research", {}))


def build_index(force: bool = False) -> None:
    ensure_index(force_rebuild=force, auto_build=True)


def _normalize_submission_scores(ranked_debug: List[dict], top_k: int) -> List[dict]:
    results = []
    prev_score = 1.0
    raw_vals = [r["score_raw"] for r in ranked_debug[:top_k]]
    if not raw_vals:
        return results
    min_v, max_v = min(raw_vals), max(raw_vals)
    span = max(max_v - min_v, 1e-6)

    for rank_pos, item in enumerate(ranked_debug[:top_k], start=1):
        norm = 0.1 + 0.899 * (item["score_raw"] - min_v) / span
        if rank_pos > 1:
            norm = min(norm, prev_score - 0.0001)
        norm = max(0.1, round(norm, 4))
        prev_score = norm
        explanation = build_full_explanation(
            item["candidate"], rank_pos, item["features"], item.get("semantic_sim", 0) * 100
        )
        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank_pos,
            "score": norm,
            "reasoning": generate_reasoning(
                item["candidate"], rank_pos, item["features"], item["features"]["components"]["semantic"]
            ),
            "explanation": explanation,
            "debug": item,
        })
    return results


def rank(
    job_text: str,
    title: str = "",
    job_struct: Optional[dict] = None,
    candidates_path: Optional[Path] = None,
    top_k: int = 100,
    retrieval_k: int = 500,
    prefer_index: bool = True,
    explain_top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Primary ranking entry — prefers FAISS, falls back to online mode."""
    job_struct = job_struct or analyze_job_description(job_text, title=title)
    job_struct["title"] = title or job_struct.get("title", "")
    path = Path(candidates_path or DEFAULT_CANDIDATES_PATH)

    use_index = prefer_index and is_index_ready()
    if prefer_index and not use_index:
        # Do not auto-build during API/submission calls — too slow; explicit build only
        use_index = False

    if use_index:
        # Interactive API mode / Submission mode index-based pipeline path
        raw = rank_candidates(
            candidates_path=path,
            job_struct=job_struct,
            retrieval_k=retrieval_k,
            top_k=top_k,
            use_index=True,
            explain_top_k=explain_top_k,
        )
        return raw

    # Interactive API mode / Submission mode online fallback path
    return rank_candidates_online(
        candidates_path=path,
        job_struct=job_struct,
        retrieval_k=retrieval_k,
        top_k=top_k,
        explain_top_k=explain_top_k,
    )


def search_job(
    job_text: str,
    top_k: int = 10,
    job_struct: Optional[dict] = None,
    title: str = "",
    **_,
) -> List[Dict[str, Any]]:
    """Django-compatible ranked list with full explainability payload.
    Used by interactive API views.
    """
    job_struct = job_struct or analyze_job_description(job_text, title=title)
    role_type = detect_role_type(job_struct, title=title)
    weights = get_role_weights(role_type)

    # Interactive API mode: Use a smaller retrieval set for speed
    retrieval_k = min(100, max(50, top_k * 5))
    pipeline_results = rank(
        job_text=job_text,
        title=title,
        job_struct=job_struct,
        top_k=retrieval_k,
        retrieval_k=retrieval_k,
        explain_top_k=top_k, # Interactive API mode: explain ONLY top_k candidates
    )

    api_results: List[Dict[str, Any]] = []
    for idx, item in enumerate(pipeline_results[:top_k], start=1):
        debug = item.get("debug", {})
        features = debug.get("features", {})
        candidate = debug.get("candidate", {})
        explanation = item.get("explanation") or build_full_explanation(
            candidate, idx, features, features.get("components", {}).get("semantic", 0)
        )
        comps = features.get("components", {})
        final_score = debug.get("score_raw", item.get("score", 0) * 100)

        api_results.append({
            "candidate_id": build_candidate_id(candidate) if candidate else int(str(item.get("candidate_id", "CAND_0000001")).split("_")[1]),
            "full_name": candidate.get("profile", {}).get("anonymized_name", ""),
            "role_type": role_type,
            "weights_used": weights,
            "semantic_score": float(comps.get("semantic", 0)),
            "skill_score": float(comps.get("skill", 0)),
            "experience_score": float(comps.get("experience", 0)),
            "recruitability_score": float(comps.get("behavior", 0)),
            "recruiter_score": float(comps.get("recruiter", 0)),
            "career_score": float(comps.get("career", 0)),
            "education_score": float(comps.get("education", 0)),
            "assessment_score": float(comps.get("assessment", 0)),
            "llm_score": float(comps.get("semantic", 0)),
            "final_score": float(final_score),
            "potential_score": float(min(100, final_score * 1.05)),
            "confidence_score": float(explanation.get("confidence_score", 70)),
            "risk_level": explanation.get("risk_level", "medium"),
            "strengths": explanation.get("strengths", []),
            "weaknesses": explanation.get("weaknesses", []),
            "missing_skills": explanation.get("missing_skills", []),
            "matching_skills": explanation.get("matching_skills", []),
            "learning_path": explanation.get("learning_path", []),
            "interview_questions": explanation.get("interview_questions", []),
            "why_selected": explanation.get("why_selected", ""),
            "why_rejected": explanation.get("why_rejected", ""),
            "career_trajectory": explanation.get("career_growth", ""),
            "career_growth": explanation.get("career_growth", ""),
            "recruiter_summary": explanation.get("behaviour_summary", ""),
            "behaviour_summary": explanation.get("behaviour_summary", ""),
            "recruiter_signals": explanation.get("recruiter_signals", {}),
            "risk_factors": explanation.get("risk_factors", []),
            "recruiter_recommendation": explanation.get("interview_recommendation", "Moderate Fit"),
            "semantic_explanation": explanation.get("why_selected", ""),
            "skill_explanation": ", ".join(explanation.get("matching_skills", [])[:5]) or "Partial skill overlap",
            "experience_explanation": explanation.get("career_growth", ""),
            "behavioral_explanation": explanation.get("behaviour_summary", ""),
            "reasoning": item.get("reasoning", explanation.get("summary", "")),
            "explanation": explanation,
        })

    api_results.sort(key=lambda r: r["final_score"], reverse=True)
    return api_results


def rank_for_submission(
    candidates_path: Optional[Path] = None,
    job_text: Optional[str] = None,
    top_k: int = 100,
) -> List[Dict[str, Any]]:
    # Submission mode: Evaluates a large candidate pool for final validation
    from .jd import load_job_description

    job_struct = load_job_description() if not job_text else analyze_job_description(job_text)
    return rank(
        job_text=job_struct.get("full_text", job_text or ""),
        title=job_struct.get("title", ""),
        job_struct=job_struct,
        candidates_path=candidates_path,
        top_k=top_k,
        retrieval_k=500, # Large candidate pool for submission quality
        prefer_index=is_index_ready(),
        explain_top_k=None, # Explain all evaluated top candidates for submission completeness
    )
