"""Semantic domain alignment without hardcoded keyword lists."""
from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np

from .embeddings import EmbeddingEngine
from .text_builder import build_retrieval_document, normalize_title


def compute_domain_alignment(
    candidate: Dict,
    job_struct: Dict | None = None,
    engine: EmbeddingEngine | None = None,
    cand_vec: np.ndarray | None = None,
) -> Dict:
    """
    Returns semantic alignment to the requested job domain.
    Uses embeddings dynamically — no hardcoded anchors.
    """
    if job_struct is None:
        try:
            from .jd import load_job_description
            job_struct = load_job_description()
        except Exception:
            job_struct = {
                "title": "Senior AI Engineer",
                "required_skills": ["python", "embeddings_retrieval", "vector_search", "ranking_evaluation"]
            }

    job_title = job_struct.get("title", "")
    job_skills = ", ".join(job_struct.get("required_skills", []))
    # We construct a domain anchor description based on the actual JD
    job_desc = f"{job_title} role with skills {job_skills}"

    if engine is None:
        from .embeddings import get_cached_engine
        engine = get_cached_engine()
        
    if cand_vec is None:
        text = build_retrieval_document(candidate)
        cand_vec = engine.encode_one(text)
        
    job_vec = engine.encode_one(job_desc)
    
    sim = float(job_vec @ cand_vec)
    
    # Map similarity (typically 0.15 to 0.8) to a score between 0 and 1.0
    normalized = max(0.0, min(1.0, (sim - 0.15) / 0.55))

    profile = candidate.get("profile", {})
    c_title = normalize_title(profile.get("current_title") or "")
    career_titles = " ".join(
        normalize_title(j.get("title", ""))
        for j in candidate.get("career_history", [])[:4]
    )
    combined_titles = f"{c_title} {career_titles}".strip()
    
    # Dynamically check for matching words between the job title and candidate titles
    title_words = set(normalize_title(job_title).lower().split())
    noise_words = {
        "engineer", "developer", "scientist", "specialist", "analyst", "senior", "lead", 
        "junior", "associate", "staff", "principal", "manager", "director", "head", "vp", 
        "chief", "cto", "expert", "intern", "executive", "role", "position"
    }
    meaningful_title_words = title_words - noise_words
    
    title_hint = 0.0
    if meaningful_title_words:
        matched_words = sum(1 for w in meaningful_title_words if w in combined_titles.lower())
        if matched_words >= 2:
            title_hint = 0.14
        elif matched_words == 1:
            title_hint = 0.08

    combined = max(0.0, min(1.0, normalized + title_hint))
    return {
        "job_similarity": sim,
        "score": combined * 100.0,
        "tier": "strong" if combined >= 0.72 else ("moderate" if combined >= 0.55 else "adjacent"),
    }


def domain_score_multiplier(domain: Dict) -> float:
    """Bounded multiplier for final ranking — avoids overfitting."""
    s = domain.get("score", 50.0) / 100.0
    if s >= 0.78:
        return 1.24
    if s >= 0.65:
        return 1.14
    if s >= 0.52:
        return 1.03
    if s >= 0.42:
        return 0.93
    return 0.85


def domain_score_bonus(
    domain: Dict, 
    title: str, 
    job_title: str | None = None, 
    engine: EmbeddingEngine | None = None
) -> float:
    """Flat bonus on 0-100 scale for strong title alignment."""
    bonus = 0.0
    if domain.get("tier") == "strong":
        bonus += 12.0
    elif domain.get("tier") == "moderate":
        bonus += 5.0
        
    if not job_title:
        try:
            from .jd import load_job_description
            job_struct = load_job_description()
            job_title = job_struct.get("title", "")
        except Exception:
            job_title = "Senior AI Engineer"
            
    c_title = normalize_title(title)
    j_title = normalize_title(job_title)
    if c_title and j_title:
        if engine is None:
            from .embeddings import get_cached_engine
            engine = get_cached_engine()
        c_vec = engine.encode_one(c_title)
        j_vec = engine.encode_one(j_title)
        sim = float(c_vec @ j_vec)
        if sim >= 0.72:
            bonus += 7.0
            
    return bonus

