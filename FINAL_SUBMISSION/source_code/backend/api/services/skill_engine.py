from __future__ import annotations

from typing import List, Dict, Tuple
import math
import re


def _parse_candidate_skills(skills_text: str) -> Dict[str, Dict[str, float]]:
    """Parse candidate skill string into structured dict.

    Supported formats:
    - CSV: "python,java,react"
    - Structured: "python:proficiency=0.8|endorsements=12|score=85;java:proficiency=0.6"
    Returns: {"python": {"proficiency":0.8, "endorsements":12, "score":85}, ...}
    """
    out: Dict[str, Dict[str, float]] = {}
    if not skills_text:
        return out
    # split on semicolons for structured entries or commas
    parts = [p.strip() for p in re.split(r"[;\n]", skills_text) if p.strip()]
    for p in parts:
        if ":" in p:
            name, rest = p.split(":", 1)
            attrs = {}
            for kv in rest.split("|"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    try:
                        attrs[k.strip()] = float(v)
                    except Exception:
                        try:
                            attrs[k.strip()] = float(v.strip("%"))
                        except Exception:
                            pass
            out[name.strip().lower()] = attrs
        else:
            # comma separated tokens
            for tok in p.split(","):
                t = tok.strip().lower()
                if t:
                    out.setdefault(t, {})
    return out


import re


def compute_skill_fit(required_skills: List[str], candidate_skills_text: str, candidate_skill_details: Dict[str, Dict] | None = None) -> Tuple[float, Dict]:
    """Compute a Skill Fit Score (0-100) and provide details.

    - required_skills: list of skill names
    - candidate_skills_text: raw skills text
    - candidate_skill_details: optional structured details per skill
    Returns: (score, details_dict)
    """
    if not required_skills:
        return 50.0, {"reason": "no required skills provided"}
    req = [s.strip().lower() for s in required_skills if s and s.strip()]
    cand_struct = _parse_candidate_skills(candidate_skills_text or "")
    if candidate_skill_details:
        # merge
        for k, v in (candidate_skill_details or {}).items():
            cand_struct.setdefault(k.lower(), {}).update(v)

    matched = 0
    proficiency_sum = 0.0
    endorsements_score = 0.0
    assessment_score = 0.0
    details = {"matched": [], "missing": []}
    for sk in req:
        info = cand_struct.get(sk, {})
        if info:
            matched += 1
            details["matched"].append(sk)
            prof = float(info.get("proficiency", info.get("proficiency_level", 0.0)))
            proficiency_sum += prof
            endors = float(info.get("endorsements", 0.0))
            endorsements_score += math.tanh(math.log1p(endors) / 3.0)  # normalize
            assess = float(info.get("assessment", info.get("score", 0.0)))
            assessment_score += (assess / 100.0)
        else:
            details["missing"].append(sk)

    total = len(req)
    base_match = matched / total
    # component weights
    w_match = 0.5
    w_prof = 0.25
    w_end = 0.15
    w_assess = 0.10

    prof_avg = (proficiency_sum / matched) if matched else 0.0
    end_avg = (endorsements_score / matched) if matched else 0.0
    assess_avg = (assessment_score / matched) if matched else 0.0

    combined = (
        base_match * w_match + prof_avg * w_prof + end_avg * w_end + assess_avg * w_assess
    )
    score = float(max(0.0, min(1.0, combined))) * 100.0
    details.update({"base_match": base_match, "proficiency_avg": prof_avg, "endorsements_avg": end_avg, "assessment_avg": assess_avg})
    return score, details

