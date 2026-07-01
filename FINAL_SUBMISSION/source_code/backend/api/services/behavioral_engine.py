from __future__ import annotations

from typing import List
import os
import math
from urllib.parse import urlparse
import requests


def _github_username_from_url(url: str) -> str | None:
    try:
        p = urlparse(url)
        if p.netloc.lower().endswith("github.com"):
            parts = p.path.strip("/").split("/")
            if parts:
                return parts[0]
    except Exception:
        pass
    return None


def _github_activity_score(username: str) -> float:
    """Attempt to compute a simple GitHub activity score (0-1).

    If `GITHUB_TOKEN` env var present, use GitHub API to fetch public events count.
    Otherwise return 0.5 for presence, 0.0 for absence.
    """
    if not username:
        return 0.0
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return 0.5
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(f"https://api.github.com/users/{username}/events/public", headers=headers, timeout=5)
        if resp.status_code == 200:
            events = resp.json()
            cnt = len(events)
            # scale: 0 events ->0 ; 1-10 -> 0.3-0.6 ; 50+ ->0.95
            score = min(0.99, math.tanh(math.log1p(cnt) / 3.0))
            return float(score)
    except Exception:
        pass
    return 0.5


def compute_recruitability_score(candidate, extra_signals: dict | None = None) -> dict:
    """Compute Recruitability Score (0-100) and details using multiple signals.

    Candidate expected fields: recruiter_response_rate, interview_completion_rate,
    offer_acceptance_rate, profile_completeness, open_to_work, github_url
    extra_signals may include search_appearances, recruiter_saves.
    """
    r_resp = getattr(candidate, "recruiter_response_rate", 0.0) / 100.0
    interview = getattr(candidate, "interview_completion_rate", 0.0) / 100.0
    offer = getattr(candidate, "offer_acceptance_rate", 0.0) / 100.0
    completeness = getattr(candidate, "profile_completeness", 0.0) / 100.0
    open_to_work = 1.0 if getattr(candidate, "open_to_work", False) else 0.5

    github_score = 0.0
    gh = getattr(candidate, "github_url", None)
    if gh:
        uname = _github_username_from_url(gh)
        github_score = _github_activity_score(uname)

    search_appearances = 0.0
    recruiter_saves = 0.0
    if extra_signals:
        search_appearances = float(extra_signals.get("search_appearances", 0.0))
        recruiter_saves = float(extra_signals.get("recruiter_saves", 0.0))

    # normalize auxiliary signals (assume counts)
    search_score = min(1.0, math.tanh(math.log1p(search_appearances) / 4.0))
    saves_score = min(1.0, math.tanh(math.log1p(recruiter_saves) / 3.0))

    # component weights
    w_resp = 0.2
    w_interview = 0.2
    w_offer = 0.15
    w_profile = 0.15
    w_open = 0.1
    w_github = 0.1
    w_search = 0.05
    w_saves = 0.05

    combined = (
        r_resp * w_resp
        + interview * w_interview
        + offer * w_offer
        + completeness * w_profile
        + open_to_work * w_open
        + github_score * w_github
        + search_score * w_search
        + saves_score * w_saves
    )
    score = float(max(0.0, min(1.0, combined))) * 100.0
    details = {
        "recruiter_response_rate": r_resp,
        "interview_completion_rate": interview,
        "offer_acceptance_rate": offer,
        "profile_completeness": completeness,
        "open_to_work": open_to_work,
        "github_score": github_score,
        "search_score": search_score,
        "recruiter_saves_score": saves_score,
    }
    return {"score": score, "details": details}

