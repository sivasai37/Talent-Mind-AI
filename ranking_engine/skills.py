"""Generic skill matching and normalization pipeline."""
from __future__ import annotations

import json
import math
import re
import gzip
from pathlib import Path
from typing import Dict, List, Tuple, Any
from functools import lru_cache

import numpy as np

# Cache for loaded/precomputed skills
_CANONICAL_SKILLS: Dict[str, str] = {}
_SKILL_EMBED_CACHE: Dict[str, np.ndarray] = {}


@lru_cache(maxsize=16384)
def normalize_skill(name: str) -> str:
    """Normalize skill name: lowercase, strip punctuation, handle plural, handle common abbreviations."""
    if not name:
        return ""
    # Lowercase
    s = name.lower().strip()
    
    # Remove common JavaScript/JS suffixes
    s = re.sub(r"\.js\b", "", s)
    s = re.sub(r"\bjs\b", "", s)
    
    # Keep alphanumeric characters, + (C++), and # (C#)
    s = "".join(c for c in s if c.isalnum() or c in ("+", "#", " "))
    
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s).strip()
    
    # Singularize words
    words = s.split()
    singular_words = []
    for w in words:
        if w.endswith("s") and not w.endswith("ss") and w not in (
            "redis", "kubernetes", "pandas", "keras", "postgres", "express", "canvas", "gans", "gRPC"
        ):
            singular_words.append(w[:-1])
        else:
            singular_words.append(w)
    s = " ".join(singular_words)
    
    # General abbreviations
    abbrev_map = {
        "nlp": "natural language processing",
        "asr": "automatic speech recognition",
        "tts": "text to speech",
        "rag": "retrieval augmented generation",
        "ai": "artificial intelligence",
        "ml": "machine learning",
        "llm": "large language model",
        "dl": "deep learning",
        "cv": "computer vision",
        "k8s": "kubernetes",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
    }
    if s in abbrev_map:
        s = abbrev_map[s]
    return s


@lru_cache(maxsize=16384)
def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Edit Distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
        
    return previous_row[-1]


@lru_cache(maxsize=16384)
def is_alias(s1: str, s2: str) -> bool:
    """Check if normalized skills s1 and s2 are aliases."""
    if not s1 or not s2:
        return False
    if s1 == s2:
        return True
    # Substring matching (e.g. postgres in postgresql)
    if (s1 in s2 or s2 in s1) and min(len(s1), len(s2)) >= 3:
        return True
    # Spellings check (e.g. edit distance 1 for long names)
    if min(len(s1), len(s2)) >= 5 and levenshtein_distance(s1, s2) <= 1:
        return True
    return False


def get_skill_embedding(skill_name: str, engine: Any) -> np.ndarray:
    """Retrieve or compute normalized embedding vector for a skill."""
    s_norm = skill_name.lower().strip()
    if s_norm not in _SKILL_EMBED_CACHE:
        # Cache single embeddings to avoid duplicate model calls
        _SKILL_EMBED_CACHE[s_norm] = engine.encode_one(s_norm)
    return _SKILL_EMBED_CACHE[s_norm]


def extract_potential_skills(text: str) -> List[str]:
    """Dynamically discover potential tech/skill terms from raw text blocks."""
    # Match potential proper noun technologies (capitalized words, numbers, special symbols)
    pattern = r"\b[A-Za-z][a-zA-Z0-9+#\.]*(?:\+[+]+)?\b"
    words = re.findall(pattern, text)
    res = []
    for w in words:
        if len(w) < 2:
            continue
        # Select tokens with uppercase, digits, or programming symbols (C++, C#, etc.)
        if any(c.isupper() for c in w) or any(c.isdigit() for c in w) or "+" in w or "#" in w or "." in w:
            res.append(w)
    return list(set(res))


def extract_all_text_from_candidate(candidate: Dict) -> str:
    """Consolidate text fields from all parts of the candidate profile."""
    if "_raw_text" in candidate:
        return candidate["_raw_text"]
        
    parts = []
    profile = candidate.get("profile", {})
    parts.append(profile.get("headline", "") or "")
    parts.append(profile.get("summary", "") or "")
    parts.append(profile.get("current_title", "") or "")
    
    for job in candidate.get("career_history", []):
        parts.append(job.get("title", "") or "")
        parts.append(job.get("description", "") or "")
        
    for edu in candidate.get("education", []):
        parts.append(edu.get("field_of_study", "") or "")
        parts.append(edu.get("degree", "") or "")
        parts.append(edu.get("institution", "") or "")
        
    for cert in candidate.get("certifications", []):
        parts.append(cert.get("name", "") or "")
        parts.append(cert.get("issuer", "") or "")
        
    for proj in candidate.get("projects", []):
        if isinstance(proj, dict):
            parts.append(proj.get("name", "") or "")
            parts.append(proj.get("description", "") or "")
        elif isinstance(proj, str):
            parts.append(proj)
            
    res = " ".join(parts)
    candidate["_raw_text"] = res
    return res


def get_canonical_skills() -> Dict[str, str]:
    """Load or dynamically compile canonical skill list from candidate dataset."""
    global _CANONICAL_SKILLS
    if _CANONICAL_SKILLS:
        return _CANONICAL_SKILLS

    from .config import EMBEDDINGS_DIR, DEFAULT_CANDIDATES_PATH
    cache_path = EMBEDDINGS_DIR / "canonical_skills.json"
    
    if cache_path.exists():
        try:
            _CANONICAL_SKILLS = json.loads(cache_path.read_text(encoding="utf-8"))
            return _CANONICAL_SKILLS
        except Exception:
            pass

    # Build dynamically by scanning candidate dataset
    skills_dict = {}
    if DEFAULT_CANDIDATES_PATH.exists():
        try:
            def _open_file(p):
                if str(p).endswith(".gz"):
                    return gzip.open(p, "rt", encoding="utf-8")
                return open(p, "r", encoding="utf-8")

            with _open_file(DEFAULT_CANDIDATES_PATH) as f:
                for line in f:
                    if not line.strip():
                        continue
                    cand = json.loads(line)
                    for s in cand.get("skills", []):
                        name = s.get("name", "")
                        if name:
                            skills_dict[name.lower().strip()] = name
        except Exception:
            pass

    # Fallback to general skills if scan fails/empty
    if not skills_dict:
        skills_dict = {
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "react": "React", "node": "Node.js", "kubernetes": "Kubernetes", "aws": "AWS"
        }

    # Save to cache
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(skills_dict, indent=2), encoding="utf-8")
    except Exception:
        pass

    _CANONICAL_SKILLS = skills_dict
    return _CANONICAL_SKILLS


def match_skill(target: str, candidate: Dict, engine: Any, fast_mode: bool = False) -> Tuple[bool, float, str]:
    """
    Evaluates candidate's alignment to target skill with 5 strategies:
      1. Exact Match (explicit skills)
      2. Normalized Match (explicit skills)
      3. Alias Detection (explicit skills)
      4. Semantic embedding similarity (explicit skills) [skipped in fast_mode]
      5. Context matching from work experience, summary, education, certs, projects
    """
    target_l = target.lower().strip()
    norm_target = normalize_skill(target)
    
    candidate_skills = candidate.get("skills", [])
    
    # Strategy 1: Exact Match in explicit skills
    for s in candidate_skills:
        s_name = s.get("name", "")
        if s_name.lower().strip() == target_l:
            prof = s.get("proficiency", "intermediate")
            prof_val = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.82, "expert": 0.95}.get(str(prof).lower(), 0.60)
            dur = int(s.get("duration_months", 0) or 0)
            dur_bonus = min(1.0, dur / 24.0) * 0.15
            endorse = min(1.0, math.tanh(math.log1p(int(s.get("endorsements", 0) or 0)) / 3.0))
            score = prof_val * 0.70 + dur_bonus + endorse * 0.15
            return True, score, s_name

    # Strategy 2: Normalized Match in explicit skills
    for s in candidate_skills:
        s_name = s.get("name", "")
        if normalize_skill(s_name) == norm_target:
            prof = s.get("proficiency", "intermediate")
            prof_val = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.82, "expert": 0.95}.get(str(prof).lower(), 0.60)
            dur = int(s.get("duration_months", 0) or 0)
            dur_bonus = min(1.0, dur / 24.0) * 0.15
            endorse = min(1.0, math.tanh(math.log1p(int(s.get("endorsements", 0) or 0)) / 3.0))
            score = prof_val * 0.70 + dur_bonus + endorse * 0.15
            return True, score * 0.95, s_name

    # Strategy 3: Alias Detection in explicit skills
    for s in candidate_skills:
        s_name = s.get("name", "")
        if is_alias(normalize_skill(s_name), norm_target):
            prof = s.get("proficiency", "intermediate")
            prof_val = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.82, "expert": 0.95}.get(str(prof).lower(), 0.60)
            dur = int(s.get("duration_months", 0) or 0)
            dur_bonus = min(1.0, dur / 24.0) * 0.15
            endorse = min(1.0, math.tanh(math.log1p(int(s.get("endorsements", 0) or 0)) / 3.0))
            score = prof_val * 0.70 + dur_bonus + endorse * 0.15
            return True, score * 0.90, s_name

    # Strategy 4: Semantic Embedding Similarity in explicit skills
    if not fast_mode:
        target_vec = get_skill_embedding(target, engine)
        best_sim = 0.0
        best_skill_name = None
        for s in candidate_skills:
            s_name = s.get("name", "")
            s_vec = get_skill_embedding(s_name, engine)
            sim = float(target_vec @ s_vec)
            if sim > best_sim:
                best_sim = sim
                best_skill_name = s_name
                
        if best_sim >= 0.72:
            for s in candidate_skills:
                if s.get("name", "") == best_skill_name:
                    prof = s.get("proficiency", "intermediate")
                    prof_val = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.82, "expert": 0.95}.get(str(prof).lower(), 0.60)
                    dur = int(s.get("duration_months", 0) or 0)
                    dur_bonus = min(1.0, dur / 24.0) * 0.15
                    endorse = min(1.0, math.tanh(math.log1p(int(s.get("endorsements", 0) or 0)) / 3.0))
                    score = prof_val * 0.70 + dur_bonus + endorse * 0.15
                    return True, score * best_sim, best_skill_name

    # Strategy 5: Context Matching from raw text (Career history, summary, education, certs, projects)
    if "_raw_text" in candidate:
        raw_text = candidate["_raw_text"]
    else:
        raw_text = extract_all_text_from_candidate(candidate)
        candidate["_raw_text"] = raw_text
    raw_text_l = raw_text.lower()
    
    # Substring match on normalized string (using 'in' operator first to bypass expensive regex compilation/search)
    if norm_target in raw_text_l:
        pattern = rf"\b{re.escape(norm_target)}\b"
        if re.search(pattern, raw_text_l):
            score = 0.60
            mentions = raw_text_l.count(norm_target)
            boost = min(0.15, (mentions - 1) * 0.05) if mentions > 1 else 0.0
            return True, score + boost, target

    if not fast_mode:
        # Match against dynamically discovered capitalized words in text
        potential_skills = extract_potential_skills(raw_text)
        for ps in potential_skills:
            norm_ps = normalize_skill(ps)
            if norm_ps == norm_target or is_alias(norm_ps, norm_target):
                score = 0.60
                return True, score, ps

    # Semantic match against career history titles
    if not fast_mode:
        target_vec = get_skill_embedding(target, engine)
        for job in candidate.get("career_history", []):
            j_title = job.get("title", "")
            if j_title:
                jt_vec = get_skill_embedding(j_title, engine)
                if float(target_vec @ jt_vec) >= 0.72:
                    return True, 0.65, j_title

    return False, 0.0, ""
