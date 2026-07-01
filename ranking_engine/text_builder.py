"""Build candidate text representations for embedding."""
from __future__ import annotations

import re
from typing import Dict, List

# Canonical title tokens for semantic retrieval (not used for hard filtering)
_TITLE_ALIASES = {
    "swe": "software engineer",
    "sde": "software development engineer",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ds": "data scientist",
    "mle": "machine learning engineer",
    "research eng": "research engineer",
}


def normalize_title(title: str) -> str:
    """Normalize noisy titles for embedding and domain scoring."""
    if not title:
        return ""
    t = title.lower().strip()
    t = re.sub(r"[^a-z0-9+/#\s-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    for short, full in _TITLE_ALIASES.items():
        t = re.sub(rf"\b{re.escape(short)}\b", full, t)
    return t


def _career_titles_line(career: List[Dict], limit: int = 4) -> str:
    titles = []
    for job in career[:limit]:
        raw = job.get("title", "")
        if raw:
            titles.append(normalize_title(raw))
    return " → ".join(titles)


def _skill_line(skills: List[Dict]) -> str:
    parts = []
    for s in skills:
        name = s.get("name", "")
        prof = s.get("proficiency", "")
        dur = s.get("duration_months", 0)
        if name:
            parts.append(f"{name} ({prof}, {dur}mo)")
    return "; ".join(parts)


def _career_line(career: List[Dict], max_desc: int = 200) -> str:
    parts = []
    for job in career[:5]:
        title = job.get("title", "")
        company = job.get("company", "")
        desc = (job.get("description") or "")[:max_desc]
        industry = job.get("industry", "")
        chunk = f"{title} at {company} ({industry}): {desc}"
        parts.append(chunk.strip())
    return " | ".join(parts)


def build_retrieval_document(candidate: Dict) -> str:
    """Compact document for FAISS indexing — optimized for CPU encoding speed."""
    profile = candidate.get("profile", {})
    skill_names = ", ".join(s.get("name", "") for s in candidate.get("skills", [])[:20])
    career = candidate.get("career_history", [])
    current_title = normalize_title(profile.get("current_title", ""))
    recent = ""
    if career:
        j = career[0]
        recent = f"{normalize_title(j.get('title', ''))} at {j.get('company', '')}"
    trajectory = _career_titles_line(career)
    parts = [
        profile.get("headline", ""),
        (profile.get("summary") or "")[:350],
        current_title or profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
        recent,
        trajectory,
        skill_names,
    ]
    return " | ".join(p for p in parts if p)[:900]


def build_candidate_document(candidate: Dict) -> str:
    profile = candidate.get("profile", {})
    sections = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
        f"{profile.get('years_of_experience', 0)} years experience",
        profile.get("location", ""),
        _skill_line(candidate.get("skills", [])),
        _career_line(candidate.get("career_history", [])),
    ]
    certs = candidate.get("certifications", [])
    if certs:
        sections.append(
            "; ".join(f"{c.get('name')} ({c.get('issuer')}, {c.get('year')})" for c in certs[:5])
        )
    edu = candidate.get("education", [])
    if edu:
        sections.append(
            "; ".join(
                f"{e.get('degree')} {e.get('field_of_study')} {e.get('institution')} tier {e.get('tier')}"
                for e in edu[:3]
            )
        )
    return "\n".join(s for s in sections if s)


def build_candidate_id(candidate: Dict) -> int:
    cid = candidate.get("candidate_id", "")
    return int(str(cid).split("_")[1])
