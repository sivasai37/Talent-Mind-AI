"""Hybrid scoring and end-to-end ranking pipeline."""
from __future__ import annotations

import gzip
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .config import (
    AI_TITLE_KEYWORDS,
    DEFAULT_CANDIDATES_PATH,
    DEFAULT_WEIGHTS,
    FINAL_TOP_K,
    NON_TECH_TITLES,
    RETRIEVAL_TOP_K,
    ROLE_WEIGHTS,
)
from .embeddings import (
    EmbeddingEngine,
    faiss_search,
    get_cached_engine,
    load_embeddings,
    load_faiss_index,
    load_query_vector,
)
from .domain_semantics import compute_domain_alignment, domain_score_bonus, domain_score_multiplier
from .explain import build_full_explanation, generate_reasoning
from .features import (
    compute_assessment_features,
    compute_behavior_features,
    compute_career_features,
    compute_education_features,
    compute_experience_features,
    compute_recruiter_features,
    compute_skill_features,
    compute_publication_features,
)
from .honeypot import detect_honeypot
from .jd import load_job_description
from .text_builder import build_candidate_id, build_retrieval_document, normalize_title


def _open_candidates(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def infer_role_properties(job_struct: Dict) -> Dict:
    title = str(job_struct.get("title", "")).lower()
    skills = [s.lower() for s in job_struct.get("required_skills", [])]
    skills_text = " ".join(skills)
    
    # 1. Seniority
    exp_min = float(job_struct.get("experience_min", 0.0) or 0.0)
    if any(k in title for k in ("director", "vice president", "vp", "head of", "principal", "chief", "cto", "cfo", "ceo")):
        seniority = "leadership"
    elif any(k in title for k in ("lead", "manager", "architect")):
        seniority = "leadership" if exp_min >= 7 else "senior"
    elif exp_min >= 8.0:
        seniority = "leadership"
    elif exp_min >= 5.0 or "senior" in title:
        seniority = "senior"
    elif exp_min >= 3.0 or "mid" in title:
        seniority = "mid"
    else:
        seniority = "junior"
        
    # 2. Job Family
    if any(k in title for k in ("marketing", "branding", "seo", "growth")):
        job_family = "marketing"
    elif any(k in title for k in ("sales", "business development", "account executive", "bde")):
        job_family = "sales"
    elif any(k in title for k in ("hr", "human resource", "talent", "recruiter", "people")):
        job_family = "hr"
    elif any(k in title for k in ("designer", "ui/ux", "illustrator", "creative")):
        job_family = "design"
    elif any(k in title for k in ("business analyst", "data analyst", "analytics", "bi ", "product analyst")):
        job_family = "analytics"
    elif any(k in title for k in ("product manager", "pm ", "project manager", "scrum master")):
        job_family = "management"
    else:
        job_family = "engineering"
        
    # 3. Technical Domain
    tech_domain = "none"
    if job_family == "engineering":
        if any(k in title or k in skills_text for k in ("machine learning", "ml ", "ai ", "nlp", "deep learning", "computer vision", "generative ai", "llm")):
            tech_domain = "ml_ai"
        elif any(k in title or k in skills_text for k in ("devops", "sre", "infrastructure", "platform", "cloud", "terraform", "kubernetes")):
            tech_domain = "devops"
        elif any(k in title or k in skills_text for k in ("data engineer", "spark", "kafka", "etl", "hadoop", "data pipeline")):
            tech_domain = "data"
        elif any(k in title or k in skills_text for k in ("qa", "test", "quality assurance", "selenium")):
            tech_domain = "qa"
        elif any(k in title or k in skills_text for k in ("cybersecurity", "security", "penetration", "cyber")):
            tech_domain = "cybersecurity"
        elif any(k in title or k in skills_text for k in ("frontend", "react", "angular", "vue", "html", "css", "ui developer")):
            tech_domain = "frontend"
        elif any(k in title or k in skills_text for k in ("android", "ios", "mobile", "flutter", "react native")):
            tech_domain = "mobile"
        else:
            tech_domain = "backend"
            
    # 4. Leadership & Research expectation
    leadership_req = (seniority == "leadership") or ("lead" in title) or ("mentor" in title)
    research_req = "research" in title or "scientist" in title or any(k in skills_text for k in ("publication", "paper", "patent"))
    
    return {
        "seniority": seniority,
        "job_family": job_family,
        "tech_domain": tech_domain,
        "leadership_req": leadership_req,
        "research_req": research_req,
    }


def compute_dynamic_weights(job_struct: Dict) -> Dict[str, float]:
    props = infer_role_properties(job_struct)
    
    w = {
        "semantic": 0.20,
        "skill": 0.20,
        "experience": 0.20,
        "behavior": 0.10,
        "recruiter": 0.10,
        "career": 0.10,
        "education": 0.05,
        "assessment": 0.05,
        "publications": 0.00
    }
    
    if props["research_req"]:
        w["publications"] = 0.10
        w["education"] = 0.10
        w["skill"] = 0.25
        w["semantic"] = 0.15
        w["experience"] = 0.15
        w["behavior"] = 0.05
        w["recruiter"] = 0.05
        w["career"] = 0.05
        w["assessment"] = 0.00
    elif props["tech_domain"] != "none":
        w["skill"] += 0.10
        w["semantic"] += 0.05
        w["experience"] -= 0.05
        w["career"] -= 0.05
        w["assessment"] += 0.02
        w["behavior"] -= 0.02
    else:
        w["skill"] -= 0.05
        w["experience"] += 0.05
        w["behavior"] += 0.05
        w["recruiter"] += 0.05
        w["career"] += 0.03
        w["education"] -= 0.03
        w["assessment"] -= 0.03
        w["semantic"] -= 0.02
        
    if props["leadership_req"]:
        w["experience"] += 0.05
        w["career"] += 0.05
        w["behavior"] += 0.02
        w["skill"] -= 0.06
        w["semantic"] -= 0.06
        
    total = sum(w.values())
    for k in w:
        w[k] = round(w[k] / total, 4)
        
    return w


def _get_weights(job_struct: Dict) -> Dict[str, float]:
    return compute_dynamic_weights(job_struct)


def _load_candidate_map(path: Path) -> Dict[int, Dict]:
    by_id: Dict[int, Dict] = {}
    with _open_candidates(path) as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            by_id[build_candidate_id(cand)] = cand
    return by_id


def _load_candidate_map_for_ids(path: Path, needed_ids: set[int]) -> Dict[int, Dict]:
    """Load only required candidates when full map is unnecessary."""
    found: Dict[int, Dict] = {}
    if not needed_ids:
        return found
    with _open_candidates(path) as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            cid = build_candidate_id(cand)
            if cid in needed_ids:
                found[cid] = cand
                if len(found) == len(needed_ids):
                    break
    return found


def score_candidate(
    candidate: Dict,
    job_struct: Dict,
    semantic_sim: float,
    honeypot_penalty: float,
    weights: Dict[str, float],
    engine: EmbeddingEngine | None = None,
    cand_vec: np.ndarray | None = None,
) -> Tuple[float, Dict]:
    signals = candidate.get("redrob_signals", {})

    skill_f = compute_skill_features(candidate, job_struct, signals)
    exp_f = compute_experience_features(candidate, job_struct, engine=engine, fast_mode=False)
    beh_f = compute_behavior_features(candidate)
    rec_f = compute_recruiter_features(candidate)
    career_f = compute_career_features(candidate)
    edu_f = compute_education_features(candidate)
    assess_f = compute_assessment_features(candidate, job_struct)
    domain_f = compute_domain_alignment(candidate, job_struct, engine=engine, cand_vec=cand_vec)
    pub_f = compute_publication_features(candidate, job_struct)

    semantic_pct = max(0.0, min(100.0, semantic_sim * 100.0))

    components = {
        "semantic": semantic_pct,
        "skill": skill_f["score"],
        "experience": exp_f["score"],
        "behavior": beh_f["score"],
        "recruiter": rec_f["score"],
        "career": career_f["score"],
        "education": edu_f["score"],
        "assessment": assess_f["score"],
        "publications": pub_f["score"],
    }

    weighted = sum(components[k] * weights.get(k, 0.0) for k in weights if k in components)
    if "publications" in weights and weights["publications"] > 0:
        weighted += components["publications"] * weights["publications"]
        
    title = (candidate.get("profile", {}).get("current_title") or "")
    final = (
        weighted * (1.0 - honeypot_penalty) * domain_score_multiplier(domain_f)
        + domain_score_bonus(domain_f, title, job_struct.get("title", ""), engine)
    )

    # Apply penalty for missing required skills heavily on final score to ensure correct ranking priority
    n_req = len(job_struct.get("required_skills", []))
    if n_req > 0:
        ratio = len(skill_f["matched_skills"]) / n_req
        final = final * (ratio ** 1.5)

    feature_bundle = {
        "skill": skill_f,
        "experience": exp_f,
        "behavior": beh_f,
        "recruiter": rec_f,
        "career": career_f,
        "education": edu_f,
        "assessment": assess_f,
        "domain": domain_f,
        "publications": pub_f,
        "components": components,
        "honeypot_penalty": honeypot_penalty,
    }
    return final, feature_bundle


def _heuristic_prefilter_score(candidate: Dict, job_struct: Dict) -> float:
    """Fast structured score for narrowing pool before semantic encoding."""
    is_hard, reasons, penalty = detect_honeypot(candidate, fast_mode=True)
    if is_hard:
        return -1.0
        
    title = (candidate.get("profile", {}).get("current_title") or "")
    
    # Fast experience score
    exp = compute_experience_features(candidate, job_struct, fast_mode=True)["score"]
    # Fast skill score
    skill = compute_skill_features(candidate, job_struct, candidate.get("redrob_signals", {}), fast_mode=True)["score"]
    # Behavior score
    beh = compute_behavior_features(candidate)["score"]
    
    # Fast dynamic title relevance check
    from .features import compute_title_relevance_fast
    job_title = job_struct.get("title", "")
    title_rel = compute_title_relevance_fast(title, job_title)
    
    score = exp * 0.30 + skill * 0.35 + beh * 0.15 + (title_rel * 100.0) * 0.20
    score = score * (1.0 - penalty)
    return score


def rank_candidates_online(
    candidates_path: Optional[Path] = None,
    job_struct: Optional[Dict] = None,
    prefilter_k: int = 5000,
    retrieval_k: int = RETRIEVAL_TOP_K,
    top_k: int = FINAL_TOP_K,
    explain_top_k: Optional[int] = None,
) -> List[Dict]:
    """Rank without precomputed index — fits 5-minute CPU budget."""
    start = time.time()
    candidates_path = Path(candidates_path or DEFAULT_CANDIDATES_PATH)
    job_struct = job_struct or load_job_description()
    weights = _get_weights(job_struct)

    print("Online ranking: structured prefilter pass...", flush=True)
    pool: List[tuple[float, Dict]] = []
    with _open_candidates(candidates_path) as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            if detect_honeypot(cand, fast_mode=True)[0]:
                continue
            h = _heuristic_prefilter_score(cand, job_struct)
            if h < 0:
                continue
            pool.append((h, cand))

    pool.sort(key=lambda x: (-x[0], x[1]["candidate_id"]))
    shortlist = [c for _, c in pool[:prefilter_k]]
    print(f"  shortlisted {len(shortlist)} from {len(pool)} valid candidates", flush=True)

    engine = get_cached_engine()
    query_vec = engine.encode_one(job_struct.get("full_text", ""))
    texts = [build_retrieval_document(c) for c in shortlist]
    print(f"  encoding {len(texts)} candidates...", flush=True)
    vectors = engine.encode(texts, batch_size=128)

    sims = vectors @ query_vec
    order = np.argsort(-sims)[: min(retrieval_k, len(shortlist))]
    retrieved = [(shortlist[i], float(sims[i]), vectors[i]) for i in order]

    ranked: List[Dict] = []
    for cand, sim, cand_vec in retrieved:
        _, reasons, penalty = detect_honeypot(cand)
        raw_score, features = score_candidate(
            cand, job_struct, sim, penalty, weights, engine=engine, cand_vec=cand_vec
        )
        ranked.append({
            "candidate_id": cand["candidate_id"],
            "int_id": build_candidate_id(cand),
            "score_raw": raw_score,
            "semantic_sim": sim,
            "features": features,
            "honeypot_reasons": reasons,
            "candidate": cand,
        })

    ranked.sort(key=lambda x: (-x["score_raw"], x["candidate_id"]))

    results = []
    prev_score = 1.0
    raw_vals = [r["score_raw"] for r in ranked[:top_k]]
    min_v, max_v = (min(raw_vals), max(raw_vals)) if raw_vals else (0.0, 1.0)
    span = max(max_v - min_v, 1e-6)

    limit_explain = explain_top_k if explain_top_k is not None else top_k
    for rank_pos, item in enumerate(ranked[:top_k], start=1):
        norm = 0.1 + 0.899 * (item["score_raw"] - min_v) / span
        if rank_pos > 1:
            norm = min(norm, prev_score - 0.0001)
        norm = max(0.1, round(norm, 4))
        prev_score = norm
        if rank_pos <= limit_explain:
            reasoning = generate_reasoning(
                item["candidate"],
                rank_pos,
                item["features"],
                item["features"]["components"]["semantic"],
                job_struct,
            )
            explanation = build_full_explanation(
                item["candidate"], rank_pos, item["features"], item["features"]["components"]["semantic"], job_struct
            )
        else:
            reasoning = ""
            explanation = {}
        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank_pos,
            "score": norm,
            "reasoning": reasoning,
            "explanation": explanation,
            "debug": item,
        })

    print(f"Online ranking complete: {len(results)} candidates in {time.time() - start:.1f}s", flush=True)
    return results


def rank_candidates(
    candidates_path: Optional[Path] = None,
    job_struct: Optional[Dict] = None,
    retrieval_k: int = RETRIEVAL_TOP_K,
    top_k: int = FINAL_TOP_K,
    use_index: bool = True,
    explain_top_k: Optional[int] = None,
) -> List[Dict]:
    start = time.time()
    candidates_path = Path(candidates_path or DEFAULT_CANDIDATES_PATH)
    job_struct = job_struct or load_job_description()
    weights = _get_weights(job_struct)

    ids, vectors = load_embeddings()
    id_to_row = {cid: i for i, cid in enumerate(ids)}
    index = load_faiss_index() if use_index else None
    engine = get_cached_engine()
    if job_struct and job_struct.get("full_text"):
        query_vec = engine.encode_one(job_struct["full_text"])
    else:
        query_vec = load_query_vector()

    scores_arr, idxs_arr = faiss_search(index, query_vec, min(retrieval_k, len(ids)))
    retrieved_ids = [ids[i] for i in idxs_arr if i >= 0]
    retrieved_sims = {retrieved_ids[j]: float(scores_arr[j]) for j in range(len(retrieved_ids))}

    needed = set(retrieved_ids)
    candidate_map = _load_candidate_map_for_ids(candidates_path, needed)
    engine = get_cached_engine()

    ranked: List[Dict] = []
    for cid in retrieved_ids:
        cand = candidate_map.get(cid)
        if not cand:
            continue

        is_hard, reasons, penalty = detect_honeypot(cand)
        if is_hard:
            continue

        sim = retrieved_sims.get(cid, 0.0)
        row_idx = id_to_row.get(cid)
        cand_vec = vectors[row_idx] if row_idx is not None else None
        raw_score, features = score_candidate(
            cand, job_struct, sim, penalty, weights, engine=engine, cand_vec=cand_vec
        )

        ranked.append({
            "candidate_id": cand["candidate_id"],
            "int_id": cid,
            "score_raw": raw_score,
            "semantic_sim": sim,
            "features": features,
            "honeypot_reasons": reasons,
            "candidate": cand,
        })

    ranked.sort(key=lambda x: (-x["score_raw"], x["candidate_id"]))

    results = []
    prev_score = 1.0
    limit_explain = explain_top_k if explain_top_k is not None else top_k
    for rank_pos, item in enumerate(ranked[:top_k], start=1):
        if rank_pos == 1:
            raw_vals = [r["score_raw"] for r in ranked[:top_k]]
            min_v, max_v = min(raw_vals), max(raw_vals)
            span = max(max_v - min_v, 1e-6)
            norm = 0.1 + 0.899 * (item["score_raw"] - min_v) / span
        else:
            raw_vals = [r["score_raw"] for r in ranked[:top_k]]
            min_v, max_v = min(raw_vals), max(raw_vals)
            span = max(max_v - min_v, 1e-6)
            norm = 0.1 + 0.899 * (item["score_raw"] - min_v) / span
            norm = min(norm, prev_score - 0.0001)
        norm = max(0.1, round(norm, 4))
        prev_score = norm
        if rank_pos <= limit_explain:
            reasoning = generate_reasoning(
                item["candidate"],
                rank_pos,
                item["features"],
                item["features"]["components"]["semantic"],
                job_struct,
            )
            explanation = build_full_explanation(
                item["candidate"], rank_pos, item["features"], item["features"]["components"]["semantic"], job_struct
            )
        else:
            reasoning = ""
            explanation = {}
        results.append({
            "candidate_id": item["candidate_id"],
            "rank": rank_pos,
            "score": norm,
            "reasoning": reasoning,
            "explanation": explanation,
            "debug": item,
        })

    elapsed = time.time() - start
    print(f"Ranking complete: {len(results)} candidates in {elapsed:.1f}s")
    return results


def write_submission_csv(results: List[Dict], out_path: Path) -> None:
    import csv

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for row in results:
            writer.writerow([
                row["candidate_id"],
                row["rank"],
                f"{row['score']:.4f}",
                row["reasoning"],
            ])
