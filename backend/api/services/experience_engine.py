from __future__ import annotations

from typing import List, Dict, Any
from datetime import date
import math


def _years_between(start, end) -> float:
    try:
        if not start:
            return 0.0
        if not end:
            end = date.today()
        return max(0.0, (end - start).days / 365.25)
    except Exception:
        return 0.0


def compute_experience_fit(required_years: float, candidate_years: float, career_history: List[Dict[str, Any]] | None = None, job_industry: str | None = None) -> Dict[str, Any]:
    """Compute Experience Fit Score (0-100) and details.

    career_history: optional list of job dicts with keys 'title','company','start_date','end_date','description'
    """
    try:
        r = float(required_years)
    except Exception:
        r = 0.0
    try:
        cyrs = float(candidate_years)
    except Exception:
        cyrs = 0.0

    # base years score
    if r <= 0:
        years_score = 0.5
    else:
        years_score = 1.0 if cyrs >= r else max(0.0, cyrs / r)

    # analyze career history for growth and stability
    growth = False
    leadership = False
    avg_tenure = 0.0
    industry_alignment = 0.0
    stability = 0.5
    if career_history:
        tenures = []
        titles = [jh.get("title", "") for jh in career_history]
        for jh in career_history:
            sd = jh.get("start_date")
            ed = jh.get("end_date")
            try:
                # accept date or ISO string
                if isinstance(sd, str):
                    sd = date.fromisoformat(sd)
                if isinstance(ed, str):
                    ed = date.fromisoformat(ed)
            except Exception:
                sd = None
                ed = None
            t = _years_between(sd, ed)
            if t > 0:
                tenures.append(t)
        if tenures:
            avg_tenure = sum(tenures) / len(tenures)
            # stability increases with avg tenure (cap at 5 years)
            stability = max(0.0, min(1.0, avg_tenure / 5.0))
        # detect promotions / career growth by presence of senior/lead in later titles
        if titles:
            last = titles[-1].lower()
            if any(k in last for k in ["senior", "lead", "manager", "director", "principal"]):
                leadership = True
        # simplistic growth detection: presence of 'senior' or 'lead' anywhere
        for t in titles:
            if any(k in (t or "").lower() for k in ["senior", "lead", "manager", "director", "principal"]):
                growth = True
                break
        # industry alignment: simple string match between job_industry and company/description
        if job_industry:
            ji = job_industry.lower()
            hits = 0
            for jh in career_history:
                txt = (jh.get("description") or "") + " " + (jh.get("company") or "")
                if ji in txt.lower():
                    hits += 1
            industry_alignment = min(1.0, hits / max(1.0, len(career_history)))

    # leadership boosts
    leadership_score = 1.0 if leadership else 0.0

    # combine components into a 0-1 score
    w_years = 0.45
    w_growth = 0.15
    w_stability = 0.15
    w_lead = 0.15
    w_ind = 0.10

    combined = (
        years_score * w_years
        + (1.0 if growth else 0.0) * w_growth
        + stability * w_stability
        + leadership_score * w_lead
        + industry_alignment * w_ind
    )
    score = float(max(0.0, min(1.0, combined))) * 100.0
    details = {
        "years_score": years_score,
        "avg_tenure": avg_tenure,
        "stability": stability,
        "growth": growth,
        "leadership": leadership,
        "industry_alignment": industry_alignment,
    }
    trajectory = "ascending" if growth or leadership else ("stable" if stability >= 0.5 else "early-stage")
    summary = (
        f"Experience score {score:.0f}/100. Career trajectory: {trajectory}. "
        f"Average tenure {avg_tenure:.1f} years. "
        f"{'Leadership signals detected. ' if leadership else ''}"
        f"{'Strong career growth pattern observed.' if growth else 'Continued experience will strengthen candidacy.'}"
    )
    return {"score": score, "details": details, "summary": summary}

