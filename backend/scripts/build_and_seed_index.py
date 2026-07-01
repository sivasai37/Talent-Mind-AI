import os
import sys
import json
import numpy as np
from datetime import date
import time

# Put backend path on sys.path
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base not in sys.path:
    sys.path.insert(0, base)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.db import transaction
from django.conf import settings
from api.models import Candidate, CandidateJob, CandidateEmbedding
from api.services.embeddings import get_engine

dataset_path = os.path.join(settings.DATA_DIR, "challenge_dataset", "[PUB] India_runs_data_and_ai_challenge", "India_runs_data_and_ai_challenge", "candidates.jsonl")

def is_honeypot(cand):
    # 1. Expert/advanced skill with 0 duration
    skills = cand.get("skills", [])
    bad_skills = sum(1 for s in skills if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", 0) == 0)
    if bad_skills >= 1:
        return True, "expert_skills_zero_duration"
        
    # 2. Future certifications
    for cert in cand.get("certifications", []):
        if cert.get("year", 0) > 2026:
            return True, f"future_cert_{cert.get('year')}"
            
    # 3. Experience duration inconsistencies
    profile = cand.get("profile", {})
    years_exp = profile.get("years_of_experience", 0.0)
    career = cand.get("career_history", [])
    for job in career:
        dur_years = job.get("duration_months", 0) / 12.0
        if dur_years > years_exp + 0.5:
            return True, "job_dur_gt_total_exp"
            
        sd_str = job.get("start_date")
        ed_str = job.get("end_date")
        duration = job.get("duration_months", 0)
        if sd_str:
            try:
                sd = date.fromisoformat(sd_str)
                if ed_str:
                    ed = date.fromisoformat(ed_str)
                else:
                    ed = date(2026, 6, 25)
                elapsed_days = (ed - sd).days
                elapsed_months = round(elapsed_days / 30.4375)
                if duration > elapsed_months + 3:
                    return True, "job_dur_gt_elapsed"
            except Exception:
                pass
                
    # 4. Job starting way before college
    education = cand.get("education", [])
    if career and education:
        edu_years = [edu.get("start_year") for edu in education if edu.get("start_year")]
        if edu_years:
            min_edu_year = min(edu_years)
            job_years = []
            for job in career:
                sd_str = job.get("start_date")
                if sd_str:
                    try:
                        job_years.append(date.fromisoformat(sd_str).year)
                    except Exception:
                        pass
            if job_years:
                min_job_year = min(job_years)
                if min_edu_year - min_job_year > 6:
                    return True, "job_started_way_before_college"
                    
    return False, ""

def main():
    print("Clearing old candidates...")
    Candidate.objects.all().delete()
    
    print("Reading and parsing candidates...")
    start_time = time.time()
    
    candidates_to_create = []
    career_history_to_create = []
    texts_to_embed = []
    ids_to_embed = []
    
    total_count = 0
    honeypot_count = 0
    
    # Let's read candidates.jsonl
    with open(dataset_path, "r", encoding="utf-8") as f:
        for line in f:
            total_count += 1
            cand = json.loads(line)
            cid = cand.get("candidate_id")
            
            # Extract numeric id from CAND_XXXXXXX
            int_id = int(cid.split("_")[1])
            
            # Check honeypot
            honeypot, reason = is_honeypot(cand)
            if honeypot:
                honeypot_count += 1
                continue
                
            # Parse fields
            profile = cand.get("profile", {})
            skills_list = cand.get("skills", [])
            signals = cand.get("redrob_signals", {})
            certs = cand.get("certifications", [])
            edu = cand.get("education", [])
            
            skills_str = ", ".join([s.get("name", "") for s in skills_list if s.get("name")])
            
            profile_parts = [
                profile.get("headline", ""),
                profile.get("summary", ""),
                skills_str
            ]
            profile_text = " \n ".join([p for p in profile_parts if p])
            
            github_activity = signals.get("github_activity_score", -1)
            github_url = f"https://github.com/cand_{int_id}" if github_activity >= 0 else ""
            
            salary_expectation = f"{signals.get('expected_salary_range_inr_lpa', {}).get('min', 0)} - {signals.get('expected_salary_range_inr_lpa', {}).get('max', 0)} LPA"
            relocation_pref = f"Willing to relocate: {signals.get('willing_to_relocate', False)}, Mode: {signals.get('preferred_work_mode', 'remote')}"
            
            cert_str = ", ".join([f"{c.get('name', '')} ({c.get('issuer', '')}, {c.get('year', '')})" for c in certs if c.get("name")])
            edu_str = " ; ".join([f"{e.get('degree', '')} in {e.get('field_of_study', '')} from {e.get('institution', '')} ({e.get('start_year', '')}-{e.get('end_year', '')})" for e in edu if e.get("degree")])
            location_str = f"{profile.get('location', '')}, {profile.get('country', '')}"
            
            c_obj = Candidate(
                id=int_id,
                full_name=profile.get("anonymized_name", ""),
                profile_text=profile_text,
                skills=skills_str,
                years_experience=profile.get("years_of_experience", 0.0),
                github_url=github_url,
                open_to_work=signals.get("open_to_work_flag", False),
                recruiter_response_rate=signals.get("recruiter_response_rate", 0.0) * 100.0,
                interview_completion_rate=signals.get("interview_completion_rate", 0.0) * 100.0,
                offer_acceptance_rate=signals.get("offer_acceptance_rate", 0.0) * 100.0,
                profile_completeness=signals.get("profile_completeness_score", 0.0),
                salary_expectation=salary_expectation,
                relocation_preference=relocation_pref,
                certifications=cert_str,
                education_level=edu_str,
                location=location_str
            )
            
            candidates_to_create.append(c_obj)
            
            # Prepare text for embedding
            # In ranking.py: full_name + profile_text + skills + certifications + education_level
            parts = [c_obj.full_name, c_obj.profile_text, c_obj.skills, c_obj.certifications, c_obj.education_level]
            if github_url:
                parts.append(github_url)
            text_to_embed = " \n ".join([p for p in parts if p])
            texts_to_embed.append(text_to_embed)
            ids_to_embed.append(int_id)
            
            # Parse career history
            for job in cand.get("career_history", []):
                sd = job.get("start_date")
                ed = job.get("end_date")
                try:
                    if sd:
                        sd = date.fromisoformat(sd)
                    if ed:
                        ed = date.fromisoformat(ed)
                except Exception:
                    sd = None
                    ed = None
                
                j_obj = CandidateJob(
                    candidate_id=int_id,
                    company=job.get("company", ""),
                    title=job.get("title", ""),
                    start_date=sd,
                    end_date=ed,
                    description=job.get("description", "")
                )
                career_history_to_create.append(j_obj)
                
    print(f"Parsed {total_count} total records. Honeypots skipped: {honeypot_count}. Valid candidates: {len(candidates_to_create)}.")
    
    # Bulk create candidates and jobs
    print("Seeding candidates in database...")
    chunk_size = 5000
    for i in range(0, len(candidates_to_create), chunk_size):
        with transaction.atomic():
            Candidate.objects.bulk_create(candidates_to_create[i:i+chunk_size])
        print(f"  Seeded candidates {i} to {min(i+chunk_size, len(candidates_to_create))}")
        
    print("Seeding candidate jobs in database...")
    for i in range(0, len(career_history_to_create), chunk_size):
        with transaction.atomic():
            CandidateJob.objects.bulk_create(career_history_to_create[i:i+chunk_size])
        print(f"  Seeded jobs {i} to {min(i+chunk_size, len(career_history_to_create))}")
        
    # Generate embeddings and build FAISS index
    print("Generating embeddings and building FAISS index...")
    engine = get_engine()
    
    # Batch encode on CPU
    embed_start = time.time()
    embeddings_list = []
    encode_batch_size = 1000
    for i in range(0, len(texts_to_embed), encode_batch_size):
        batch_texts = texts_to_embed[i:i+encode_batch_size]
        vecs = engine.encode(batch_texts)
        embeddings_list.append(vecs)
        elapsed = time.time() - embed_start
        print(f"  Encoded batch {i//encode_batch_size + 1}/{len(texts_to_embed)//encode_batch_size + 1} ({len(batch_texts)} texts). Elapsed: {elapsed:.1f}s")
        
    all_vectors = np.vstack(embeddings_list).astype("float32")
    print(f"Embeddings generated. Shape: {all_vectors.shape}")
    
    # Save embeddings to compressed file
    npz_path = os.path.join(settings.EMBEDDINGS_DIR, "embeddings.npz")
    np.savez_compressed(npz_path, ids=np.array(ids_to_embed), vectors=all_vectors)
    print(f"Saved precomputed embeddings to {npz_path}")
    
    # Build and save FAISS index
    print("Building FAISS index...")
    import faiss
    dim = all_vectors.shape[1]
    # Normalize vectors
    norms = np.linalg.norm(all_vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    norm_vectors = all_vectors / norms
    
    index = faiss.IndexFlatIP(dim)
    index.add(norm_vectors)
    faiss_path = os.path.join(settings.FAISS_INDEX_DIR, "index.faiss")
    faiss.write_index(index, faiss_path)
    print(f"Saved FAISS index to {faiss_path}")
    
    print(f"Indexing completed successfully in {time.time() - start_time:.1f} seconds.")

if __name__ == "__main__":
    main()
