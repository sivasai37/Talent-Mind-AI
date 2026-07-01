from __future__ import annotations

import re
from typing import List, Dict

from .embeddings import get_engine, tokenize


_SECTION_RE = re.compile(r"(?:required skills|must have|must be|must have:|requirements|required:|skills required)[:\s]*([\s\S]{0,200})", re.I)
_PREFERRED_RE = re.compile(r"(?:preferred|nice to have|nice-to-have|preferred:|nice to have:)[:\s]*([\s\S]{0,200})", re.I)
_YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years|yrs)\b", re.I)
_EDU_KEYWORDS = ["bachelor", "master", "phd", "b.sc", "m.sc", "bachelor's", "master's", "mba"]

_INDUSTRY_CANDIDATES = [
    "finance",
    "healthcare",
    "e-commerce",
    "education",
    "saas",
    "gaming",
    "telecom",
    "automotive",
    "retail",
    "advertising",
]

_BEHAVIORAL_TRAITS = [
    "leadership",
    "communication",
    "collaboration",
    "ownership",
    "problem solving",
    "adaptability",
    "attention to detail",
    "customer focus",
    "initiative",
    "creativity",
]


def _extract_section(pattern: re.Pattern, text: str) -> List[str]:
    m = pattern.search(text)
    if not m:
        return []
    part = m.group(1)
    # split by commas or semicolons or 'and'
    toks = re.split(r"[,;\n]| and ", part)
    return [t.strip().lower() for t in toks if t.strip()]


def _extract_years(text: str) -> str:
    m = _YEARS_RE.search(text)
    if not m:
        return ""
    return m.group(1)


def _extract_education(text: str) -> str:
    tl = text.lower()
    for kw in _EDU_KEYWORDS:
        if kw in tl:
            return kw
    return ""


def _extract_seniority(title: str | None, text: str) -> str:
    if title and title.strip():
        t = title.lower()
        if any(k in t for k in ["principal", "lead", "director", "head"]):
            return "principal"
        if any(k in t for k in ["senior", "sr.", "sr"]):
            return "senior"
        if any(k in t for k in ["junior", "jr.", "jr"]):
            return "junior"
    # fallback based on years
    yrs = _extract_years(text)
    try:
        if yrs:
            v = float(yrs)
            if v >= 8:
                return "principal"
            if v >= 5:
                return "senior"
            if v >= 2:
                return "mid"
            return "junior"
    except Exception:
        pass
    return ""


def _semantic_top_matches(text: str, candidates: List[str], top_n: int = 3, threshold: float = 0.45) -> List[str]:
    engine = get_engine()
    if not candidates:
        return []
    cand_vecs = engine.encode(candidates)
    qvec = engine.encode_one(text)
    sims = [float((cand_vecs[i] @ qvec) / ( ( (cand_vecs[i]**2).sum()**0.5) * ( (qvec**2).sum()**0.5) )) if ((cand_vecs[i]**2).sum()>0 and (qvec**2).sum()>0) else 0.0 for i in range(len(candidates))]
    paired = sorted(list(zip(candidates, sims)), key=lambda x: x[1], reverse=True)
    out = [p for p, s in paired if s >= threshold][:top_n]
    return out


def analyze_job_description(text: str, title: str | None = None) -> Dict[str, object]:
    """Produce structured extraction from a job description.

    Returns dict with keys: required_skills, preferred_skills, experience_years,
    education, industry, behavioral_traits, seniority
    """
    if not text:
        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": "",
            "education": "",
            "industry": "",
            "behavioral_traits": [],
            "seniority": "",
        }

    required = _extract_section(_SECTION_RE, text)
    preferred = _extract_section(_PREFERRED_RE, text)
    # fallback: look for 'must have' and 'preferred' keywords across lines
    if not required:
        # find lines starting with '-' that contain skill-like tokens
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for ln in lines:
            if ln.lower().startswith("must") or ln.lower().startswith("required"):
                toks = re.split(r"[:,]", ln, maxsplit=1)
                if len(toks) > 1:
                    required.extend([t.strip().lower() for t in re.split(r"[,;]", toks[1]) if t.strip()])

    # token-level fallback: pick top tokens as skills
    if not required:
        toks = tokenize(text)[:30]
        required = toks[:8]

    if not preferred:
        # try 'nice to have' phrases
        preferred = []

    experience = _extract_years(text)
    education = _extract_education(text)
    industry_matches = _semantic_top_matches(text, _INDUSTRY_CANDIDATES, top_n=1, threshold=0.42)
    industry = industry_matches[0] if industry_matches else ""
    behavioral = _semantic_top_matches(text, _BEHAVIORAL_TRAITS, top_n=5, threshold=0.32)
    seniority = _extract_seniority(title, text)

    return {
        "required_skills": required,
        "preferred_skills": preferred,
        "experience_years": experience,
        "education": education,
        "industry": industry,
        "behavioral_traits": behavioral,
        "seniority": seniority,
    }
