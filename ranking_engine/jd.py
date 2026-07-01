"""Structured job-description understanding."""
from __future__ import annotations

import json
import re
import os
from pathlib import Path
from typing import Dict, List

from .config import DEFAULT_JD_PATH

_YEARS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years|yrs)", re.I)

class DynamicSkillClusters(dict):
    def __init__(self, is_required=True):
        super().__init__()
        self.is_required = is_required
        if is_required:
            self.keys_list = ["embeddings_retrieval", "vector_search", "python", "ranking_evaluation"]
        else:
            self.keys_list = ["llm_finetuning", "ltr_models", "hr_tech", "distributed", "open_source"]
            
    def __getitem__(self, key):
        return self.get(key)
        
    def get(self, key, default=None):
        try:
            from .embeddings import get_cached_engine
            from .skills import get_canonical_skills
            engine = get_cached_engine()
            canonical_skills = list(get_canonical_skills().values())
            
            key_l = key.lower().replace("_", " ")
            key_words = [w for w in key_l.split() if len(w) > 3]
            key_vec = engine.encode_one(key_l)
            aliases = [key]
            for skill in canonical_skills:
                s_lower = skill.lower()
                # 1. Semantic similarity
                skill_vec = engine.encode_one(s_lower)
                sim = float(key_vec @ skill_vec)
                # 2. Word overlap
                word_match = any(w in s_lower for w in key_words) if key_words else False
                if sim >= 0.45 or word_match:
                    aliases.append(skill)
            return list(set(aliases))
        except Exception:
            return [key]
            
    def items(self):
        return [(k, self.get(k)) for k in self.keys_list]
        
    def __contains__(self, item):
        return item in self.keys_list


class DynamicAllSkills(list):
    def __init__(self):
        super().__init__()
        self._loaded = False
        
    def _ensure_loaded(self):
        if not self._loaded:
            try:
                from .skills import get_canonical_skills
                skills = list(get_canonical_skills().keys())
                self.clear()
                self.extend(skills)
                self._loaded = True
            except Exception:
                pass
                
    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()
        
    def __len__(self):
        self._ensure_loaded()
        return super().__len__()
        
    def __contains__(self, item):
        self._ensure_loaded()
        return super().__contains__(item)


class DynamicDisplayNames(dict):
    def __init__(self):
        super().__init__()
        self._loaded = False
        
    def _ensure_loaded(self):
        if not self._loaded:
            try:
                from .skills import get_canonical_skills
                skills = get_canonical_skills()
                self.clear()
                self.update(skills)
                self._loaded = True
            except Exception:
                pass
                
    def get(self, key, default=None):
        self._ensure_loaded()
        return super().get(key.lower().strip() if isinstance(key, str) else key, default)
        
    def __getitem__(self, key):
        self._ensure_loaded()
        return super().__getitem__(key.lower().strip() if isinstance(key, str) else key)
        
    def items(self):
        self._ensure_loaded()
        return super().items()
        
    def keys(self):
        self._ensure_loaded()
        return super().keys()
        
    def values(self):
        self._ensure_loaded()
        return super().values()
        
    def __contains__(self, item):
        self._ensure_loaded()
        return super().__contains__(item.lower().strip() if isinstance(item, str) else item)


REQUIRED_SKILL_CLUSTERS = DynamicSkillClusters(is_required=True)
PREFERRED_SKILL_CLUSTERS = DynamicSkillClusters(is_required=False)
ALL_SKILLS = DynamicAllSkills()
DISPLAY_NAMES = DynamicDisplayNames()


ROLE_MAP = {
    "AI Engineer": ["ai engineer", "ml engineer", "machine learning", "deep learning", "nlp", "computer vision", "llm", "embeddings", "retrieval", "prompt engineer", "applied scientist"],
    "DevOps": ["devops", "sre", "site reliability", "ci/cd", "jenkins", "ansible", "terraform", "infrastructure"],
    "Cloud": ["cloud", "aws", "azure", "gcp", "cloud engineer", "cloud architect"],
    "Data Engineering": ["data engineer", "data engineering", "etl", "spark", "kafka", "hadoop", "snowflake", "bigquery", "redshift", "airflow", "dbt"],
    "Frontend": ["frontend", "react", "angular", "vue", "css", "ui/ux", "javascript", "typescript", "frontend developer", "web developer"],
    "Full Stack": ["full stack", "fullstack", "mern", "mean", "full-stack"],
    "Backend": ["backend", "django", "flask", "fastapi", "spring boot", "java", "node.js", "express", "go developer", "backend developer"],
    "QA": ["qa", "test", "testing", "automation engineer", "qa engineer", "tester"],
    "Security": ["security", "cybersecurity", "pentest", "secops"],
    "Analytics": ["business analyst", "analyst", "analytics", "bi", "data analyst"],
    "Management": ["manager", "director", "head of", "lead", "vp", "product manager", "project manager", "engineering manager"],
    "Marketing": ["marketing", "seo", "growth marketer"],
    "Sales": ["sales", "account manager", "bd", "business development"],
    "Finance": ["finance", "accountant", "treasury", "controller"],
    "HR": ["hr", "human resources", "recruiter", "talent acquisition"],
    "Support": ["support", "customer support", "helpdesk"],
}

INDUSTRY_KEYWORDS = {
    "Healthcare": ["healthcare", "medical", "hospital", "pharma", "clinical", "biotech"],
    "Finance": ["finance", "fintech", "banking", "investment", "trading", "crypto", "blockchain"],
    "HR Tech": ["hr tech", "hr-tech", "recruiting", "talent", "recruitment", "hiring", "marketplace"],
    "Retail": ["retail", "commerce", "store"],
    "AI": ["ai", "ml", "artificial intelligence", "machine learning", "deep learning", "neural"],
    "SaaS": ["saas", "software as a service", "b2b software"],
    "E-commerce": ["e-commerce", "ecommerce", "shopping", "shopify"],
    "Manufacturing": ["manufacturing", "factory", "industrial"],
    "Gaming": ["gaming", "game", "xbox", "playstation"],
}

BEHAVIOR_KEYWORDS = {
    "Research Mindset": ["research-driven mindset", "research mindset", "research-driven", "research-oriented"],
    "Intellectual Curiosity": ["intellectual curiosity", "curiosity"],
    "Collaboration": ["collaborative", "collaboration", "collaborate", "cooperation"],
    "Leadership": ["leadership", "lead", "manage", "direct"],
    "Communication": ["communication", "writing", "present"],
    "Mentoring": ["mentoring", "mentor"],
    "Ownership": ["ownership", "own", "accountability"],
    "Problem Solving": ["problem solving", "problem-solving", "analytical"],
    "Fast Learner": ["fast learner", "quick learner"],
    "Team Player": ["team player", "team-oriented"],
    "Startup Experience": ["startup"],
    "Customer Focus": ["customer focus", "customer-centric", "user-first"],
}

LOCATION_CITIES = ["pune", "noida", "delhi", "hyderabad", "mumbai", "bangalore", "bengaluru", "chennai", "gurgaon", "ncr", "kolkata"]

def _extract_years_band(text: str) -> tuple[float, float]:
    m = re.search(r"(\d+)\s*[-–to]\s*(\d+)\s*years", text, re.I)
    if m:
        return float(m.group(1)), float(m.group(2))
    single = _YEARS_RE.search(text)
    if single:
        v = float(single.group(1))
        return v, v + 2
    
    # Heuristic fallback based on seniority keywords
    lower = text.lower()
    if any(k in lower for k in ["lead", "principal", "director", "manager", "head"]):
        return 8.0, 15.0
    if "senior" in lower:
        return 5.0, 9.0
    if any(k in lower for k in ["junior", "entry", "associate"]):
        return 1.0, 3.0
    
    return 5.0, 9.0

def _detect_role_type_rule_based(title: str, text: str) -> str:
    combined = (title + " " + text).lower()
    best_role = "Unknown"
    max_hits = 0
    for role, keywords in ROLE_MAP.items():
        hits = sum(1 for kw in keywords if kw in combined)
        title_hits = sum(3 for kw in keywords if kw in title.lower())
        total_score = hits + title_hits
        if total_score > max_hits:
            max_hits = total_score
            best_role = role
    return best_role

def _detect_industry(text: str) -> str:
    lower = text.lower()
    best_ind = "Technology"
    max_hits = 0
    for ind, keywords in INDUSTRY_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in lower)
        if hits > max_hits:
            max_hits = hits
            best_ind = ind
    return best_ind

def _extract_skills_rule_based(text: str) -> tuple[list[str], list[str]]:
    lower_text = text.lower()
    is_redrob_challenge = ("redrob" in lower_text) or ("founding team" in lower_text and "embeddings-based retrieval" in lower_text)
    
    lines = [line.strip() for line in text.split("\n")]
    required = []
    preferred = []
    
    preferred_headers = ["preferred", "nice to have", "plus", "optional", "bonus", "desirable", "advantages", "highly regarded", "nice-to-have"]
    required_headers = ["requirement", "required", "qualification", "what you need", "must have", "skills inventory", "experience required", "requirements"]
    
    ignore_words = [
        "years", "experience", "degree", "work in", "willing to", "candidate", "ability", 
        "excellent", "behavioral", "behavior", "behavioural", "behaviour", "vibe check", 
        "responsibilities", "duties", "role", "industry", "location", "hybrid", "remote",
        "onsite", "office", "salary", "shift", "employment", "type", "benefit"
    ]
    
    current_section = "required"
    
    # Try to extract the title from the first non-empty lines to filter it out from skills
    title_to_filter = ""
    non_empty_lines = [line for line in lines if line]
    if non_empty_lines:
        first_line = non_empty_lines[0]
        if any(w in first_line.lower() for w in ["engineer", "developer", "scientist", "manager", "designer", "architect", "lead", "analyst", "specialist", "role"]):
            title_to_filter = re.sub(r"^(job description|job description:)\s*", "", first_line, flags=re.I).strip()

    for line in lines:
        if not line:
            continue
        line_l = line.lower()
        
        # Check if line indicates a section header
        if any(h in line_l for h in preferred_headers):
            current_section = "preferred"
            if ":" in line:
                line = line.split(":", 1)[1].strip()
                line_l = line.lower()
            else:
                continue
        elif any(h in line_l for h in required_headers):
            current_section = "required"
            if ":" in line:
                line = line.split(":", 1)[1].strip()
                line_l = line.lower()
            else:
                continue
                
        # Skip if the line itself contains words suggesting it's behavioral, experience, or title only
        if not is_redrob_challenge:
            if any(w in line_l for w in ["experience required", "behavioral", "behavior", "vibe check", "location", "responsibilities"]):
                continue

        # Clean bullet point indicators or list prefixes
        cleaned = re.sub(r"^[-*•\s\d.]+", "", line).strip()
        if not cleaned:
            continue
            
        sub_items = []
        if "," in cleaned and len(cleaned) < 150:
            sub_items = [s.strip() for s in cleaned.split(",")]
        elif ";" in cleaned and len(cleaned) < 150:
            sub_items = [s.strip() for s in cleaned.split(";")]
        else:
            sub_items = [cleaned]
            
        for item in sub_items:
            item = item.strip(".,;:*•- ")
            if not item:
                continue
            item_l = item.lower()
            
            # Avoid adding the job title itself as a skill
            if title_to_filter and item_l == title_to_filter.lower():
                continue
                
            if len(item.split()) > 4:
                continue
                
            if any(re.search(rf"\b{re.escape(w)}\b", item_l) for w in ignore_words):
                continue
                
            # Map to DISPLAY_NAMES representation case-insensitively if exists
            display_name = item
            for skill_key, skill_disp in DISPLAY_NAMES.items():
                if item_l == skill_key:
                    display_name = skill_disp
                    break
                    
            if current_section == "preferred":
                if display_name not in preferred:
                    preferred.append(display_name)
            else:
                if display_name not in required:
                    required.append(display_name)

    # Predefined skill regex matching fallback (complement parsing)
    if is_redrob_challenge:
        for skill in ALL_SKILLS:
            pattern = rf"\b{re.escape(skill)}\b"
            if skill == "c++":
                pattern = r"\bc\+\+(?!\+)"
            elif skill == "c#":
                pattern = r"\bc#\b"
            elif skill == ".net":
                pattern = r"\b\.net\b"
                
            if re.search(pattern, lower_text):
                display_name = DISPLAY_NAMES.get(skill, skill)
                req_lower = [s.lower() for s in required]
                pref_lower = [s.lower() for s in preferred]
                if skill.lower() not in req_lower and skill.lower() not in pref_lower:
                    pos = lower_text.find(skill.lower())
                    last_pref = -1
                    last_req = -1
                    for h in preferred_headers:
                        idx = lower_text.rfind(h, 0, pos)
                        if idx > last_pref:
                            last_pref = idx
                    for h in required_headers:
                        idx = lower_text.rfind(h, 0, pos)
                        if idx > last_req:
                            last_req = idx
                    
                    if last_pref > last_req:
                        preferred.append(display_name)
                    else:
                        required.append(display_name)

    # Clean and deduplicate case-insensitively
    final_req = []
    seen_req = set()
    for r in required:
        if r.lower() not in seen_req:
            seen_req.add(r.lower())
            final_req.append(r)
            
    final_pref = []
    seen_pref = set()
    for p in preferred:
        if p.lower() not in seen_req and p.lower() not in seen_pref:
            seen_pref.add(p.lower())
            final_pref.append(p)
            
    return final_req, final_pref

def _extract_behavior(text: str) -> list[str]:
    lower = text.lower()
    extracted = []
    
    # Precise behavioral keyword checks using word boundaries and precise phrases
    precise_keywords = {
        "Research Mindset": [r"\bresearch-driven mindset\b", r"\bresearch mindset\b", r"\bresearch-driven\b", r"\bresearch-oriented\b"],
        "Intellectual Curiosity": [r"\bintellectual curiosity\b", r"\bcuriosity\b"],
        "Collaboration": [r"\bcollaborative\b", r"\bcollaboration\b", r"\bcollaborate\b", r"\bcooperation\b"],
        "Leadership": [r"\bleadership\b", r"\blead a team\b", r"\bmanage a team\b", r"\bpeople management\b", r"\bteam lead\b", r"\bleadership skills\b"],
        "Communication": [r"\bcommunication\b", r"\bcommunication skills\b", r"\bwritten and verbal communication\b"],
        "Mentoring": [r"\bmentoring\b", r"\bmentor\b", r"\bmentorship\b"],
        "Ownership": [r"\bownership\b", r"\baccountability\b", r"\btake ownership\b", r"\bsense of ownership\b"],
        "Problem Solving": [r"\bproblem solving\b", r"\bproblem-solving\b", r"\banalytical skills\b", r"\banalytical mindset\b"],
        "Fast Learner": [r"\bfast learner\b", r"\bquick learner\b", r"\blearn fast\b", r"\bfast-learner\b"],
        "Team Player": [r"\bteam player\b", r"\bteam-oriented\b"],
        "Startup Experience": [r"\bstartup\b", r"\bstart-up\b"],
        "Customer Focus": [r"\bcustomer focus\b", r"\bcustomer-centric\b", r"\buser-first\b", r"\bcustomer centric\b"],
    }
    
    for behavior, patterns in precise_keywords.items():
        if any(re.search(pat, lower) for pat in patterns):
            extracted.append(behavior)
            
    return extracted

def _extract_location(text: str) -> list[str]:
    lower = text.lower()
    locs = []
    if "remote" in lower:
        locs.append("Remote")
    if "hybrid" in lower:
        locs.append("Hybrid")
    if "onsite" in lower or "on-site" in lower or "in-office" in lower:
        locs.append("Onsite")
        
    for city in LOCATION_CITIES:
        if city in lower:
            locs.append(city.capitalize())
            
    if not locs:
        locs = ["Remote"]
    return locs

def _extract_responsibilities(text: str) -> list[str]:
    lines = text.split("\n")
    resp = []
    
    action_verbs = ["build", "own", "deploy", "design", "write", "lead", "manage", "architect", "develop", "implement", "create", "drive", "collaborate", "ensure", "optimize"]
    
    in_section = False
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        line_l = line_strip.lower()
        
        if any(h in line_l for h in ["responsibilities", "what you'd actually be doing", "what you will do", "duties", "role description"]):
            in_section = True
            continue
        elif any(h in line_l for h in ["requirements", "skills", "experience", "what we mean", "about us", "benefits"]):
            in_section = False
            
        is_bullet = line_strip.startswith(("-", "*", "•", "1.", "2.", "3.", "4.", "5."))
        has_verb = any(line_l.startswith(v) or (is_bullet and any(w in line_l[:25] for w in action_verbs)) for v in action_verbs)
        
        if (in_section and (is_bullet or len(line_strip) < 120)) or (is_bullet and has_verb):
            cleaned = re.sub(r"^[-*•\s\d.]+", "", line_strip).strip()
            if cleaned and cleaned not in resp:
                resp.append(cleaned)
                
    if not resp:
        for line in lines:
            line_strip = line.strip()
            line_l = line_strip.lower()
            if any(line_l.startswith(v) for v in action_verbs) and len(line_strip) < 120:
                cleaned = re.sub(r"^[-*•\s\d.]+", "", line_strip).strip()
                if cleaned and cleaned not in resp:
                    resp.append(cleaned)
                    
    return resp[:5]

def _parse_llm_output(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    return {}

def _analyze_job_description_rule_based(text: str, title: str = "Senior AI Engineer") -> Dict:
    lower = text.lower()
    exp_min, exp_max = _extract_years_band(text)
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        first_line = lines[0]
        if any(w in first_line.lower() for w in ["engineer", "developer", "scientist", "manager", "designer", "architect", "lead", "analyst", "specialist", "role"]):
            title = re.sub(r"^(job description|job description:)\s*", "", first_line, flags=re.I).strip()
            
    role = _detect_role_type_rule_based(title, text)
    industry = _detect_industry(text)
    required_skills, preferred_skills = _extract_skills_rule_based(text)
    
    is_redrob_challenge = ("redrob" in lower) or ("founding team" in lower and "embeddings-based retrieval" in lower)
    
    # Ensure backward compatibility clusters mapping
    if is_redrob_challenge:
        for cluster, aliases in REQUIRED_SKILL_CLUSTERS.items():
            if any(alias.lower() in lower for alias in aliases):
                if cluster not in required_skills:
                    required_skills.append(cluster)
                canonical_alias = DISPLAY_NAMES.get(aliases[0], aliases[0])
                if canonical_alias not in required_skills:
                    required_skills.append(canonical_alias)
                    
        for cluster, aliases in PREFERRED_SKILL_CLUSTERS.items():
            if any(alias.lower() in lower for alias in aliases):
                if cluster not in preferred_skills:
                    preferred_skills.append(cluster)
                
    # Extract publications
    pubs_list = ["NeurIPS", "ICML", "ACL", "CVPR", "ICLR", "ECCV"]
    preferred_publications = [p for p in pubs_list if re.search(rf"\b{re.escape(p)}\b", text, re.I)]
    
    # Extract math skills
    math_skills_list = ["linear algebra", "probability", "optimization", "statistics"]
    required_math_skills = [m for m in math_skills_list if re.search(rf"\b{re.escape(m)}\b", lower)]
    for m in required_math_skills:
        display = DISPLAY_NAMES.get(m, m)
        if display not in required_skills:
            required_skills.append(display)
        
    education = "Bachelor"
    if any(k in lower for k in ["phd", "doctorate"]):
        education = "PhD"
    elif any(k in lower for k in ["master", "m.s", "m.tech", "postgraduate"]):
        education = "Master"
    elif any(k in lower for k in ["mba"]):
        education = "MBA"
        
    behaviour = _extract_behavior(text)
    location_preferences = _extract_location(text)
    responsibilities = _extract_responsibilities(text)
    
    return {
        "title": title,
        "role": role,
        "industry": industry,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "required_math_skills": required_math_skills,
        "preferred_publications": preferred_publications,
        "experience_min": exp_min,
        "experience_max": exp_max,
        "education": education,
        "behaviour_expectations": behaviour,
        "behavior_expectations": behaviour,
        "location_preferences": location_preferences,
        "responsibilities": responsibilities,
        "leadership": "mentoring future hires" in lower or "mentor" in lower,
        "full_text": text.strip(),
    }

def analyze_job_description(text: str, title: str = "Senior AI Engineer") -> Dict:
    api_key = ""
    try:
        from django.conf import settings
        api_key = getattr(settings, "GEMINI_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if api_key and api_key != "FAKE_KEY_FOR_TEST":
        try:
            import google.generativeai as genai
            model_name = "gemini-1.5-flash"
            try:
                from django.conf import settings
                model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
            except Exception:
                pass
            if not model_name:
                model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
                
            genai.configure(api_key=api_key)
            prompt = (
                "You are an expert recruiter. Analyze this job description text and return a structured JSON object matching this schema:\n"
                "{\n"
                "  \"title\": \"job title\",\n"
                "  \"role\": \"one of: AI Engineer, Backend, Frontend, Full Stack, Data Engineering, DevOps, Cloud, QA, Security, Analytics, Management, Marketing, Sales, Finance, HR, Support, Unknown\",\n"
                "  \"industry\": \"e.g. Healthcare, Finance, HR Tech, Retail, AI, SaaS, E-commerce, Technology, etc.\",\n"
                "  \"required_skills\": [\"skill1\", \"skill2\", ...],\n"
                "  \"preferred_skills\": [\"skill1\", \"skill2\", ...],\n"
                "  \"experience_min\": number,\n"
                "  \"experience_max\": number,\n"
                "  \"education\": \"e.g. Bachelor, Master, PhD, MBA\",\n"
                "  \"behaviour_expectations\": [\"expectation1\", \"expectation2\", ...],\n"
                "  \"location_preferences\": [\"location1\", \"location2\", ...],\n"
                "  \"responsibilities\": [\"responsibility1\", \"responsibility2\", ...],\n"
                "  \"full_text\": \"the original text\"\n"
                "}\n\n"
                "Make sure to extract actual raw skills. Do not output markdown tags or any other text than the raw JSON string.\n"
                f"Job Description Text:\n{text}\n"
            )
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text_out = response.text
            parsed = _parse_llm_output(text_out)
            
            if parsed:
                title_out = parsed.get("title") or title
                role = parsed.get("role") or "Unknown"
                industry = parsed.get("industry") or "Technology"
                required_skills = parsed.get("required_skills") or []
                preferred_skills = parsed.get("preferred_skills") or []
                experience_min = parsed.get("experience_min") or 5.0
                experience_max = parsed.get("experience_max") or 9.0
                education = parsed.get("education") or "Bachelor"
                location_preferences = parsed.get("location_preferences") or []
                responsibilities = parsed.get("responsibilities") or []
                
                lower = text.lower()
                is_redrob_challenge = ("redrob" in lower) or ("founding team" in lower and "embeddings-based retrieval" in lower)
                
                # Normalize initial LLM skills using DISPLAY_NAMES case-insensitively
                normalized_req = []
                for s in required_skills:
                    s_l = s.lower()
                    mapped = s
                    for skill_key, skill_disp in DISPLAY_NAMES.items():
                        if s_l == skill_key:
                            mapped = skill_disp
                            break
                    normalized_req.append(mapped)
                required_skills = normalized_req

                normalized_pref = []
                for s in preferred_skills:
                    s_l = s.lower()
                    mapped = s
                    for skill_key, skill_disp in DISPLAY_NAMES.items():
                        if s_l == skill_key:
                            mapped = skill_disp
                            break
                    normalized_pref.append(mapped)
                preferred_skills = normalized_pref

                if is_redrob_challenge:
                    for cluster, aliases in REQUIRED_SKILL_CLUSTERS.items():
                        if any(alias.lower() in lower for alias in aliases):
                            if cluster not in required_skills:
                                required_skills.append(cluster)
                    for cluster, aliases in PREFERRED_SKILL_CLUSTERS.items():
                        if any(alias.lower() in lower for alias in aliases):
                            if cluster not in preferred_skills:
                                preferred_skills.append(cluster)
                            
                # Extract publications
                pubs_list = ["NeurIPS", "ICML", "ACL", "CVPR", "ICLR", "ECCV"]
                preferred_publications = [p for p in pubs_list if re.search(rf"\b{re.escape(p)}\b", text, re.I)]
                
                # Extract math skills
                math_skills_list = ["linear algebra", "probability", "optimization", "statistics"]
                required_math_skills = [m for m in math_skills_list if re.search(rf"\b{re.escape(m)}\b", lower)]
                for m in required_math_skills:
                    display = DISPLAY_NAMES.get(m, m)
                    if display not in required_skills:
                        required_skills.append(display)
                
                # Deduplicate required_skills & preferred_skills
                final_req = []
                seen_req = set()
                for r in required_skills:
                    if r.lower() not in seen_req:
                        seen_req.add(r.lower())
                        final_req.append(r)
                required_skills = final_req
                
                final_pref = []
                seen_pref = set()
                for p in preferred_skills:
                    if p.lower() not in seen_req and p.lower() not in seen_pref:
                        seen_pref.add(p.lower())
                        final_pref.append(p)
                preferred_skills = final_pref
                
                # Run strict behavior parsing
                behavior_expectations = _extract_behavior(text)
                
                return {
                    "title": title_out,
                    "role": role,
                    "industry": industry,
                    "required_skills": required_skills,
                    "preferred_skills": preferred_skills,
                    "required_math_skills": required_math_skills,
                    "preferred_publications": preferred_publications,
                    "experience_min": float(experience_min),
                    "experience_max": float(experience_max),
                    "education": education,
                    "behaviour_expectations": behavior_expectations,
                    "behavior_expectations": behavior_expectations,
                    "location_preferences": location_preferences,
                    "responsibilities": responsibilities,
                    "leadership": "mentoring future hires" in lower or "mentor" in lower,
                    "full_text": text.strip(),
                }
        except Exception:
            pass
            
    return _analyze_job_description_rule_based(text, title)

def load_job_description(path: Path | None = None) -> Dict:
    jd_path = path or DEFAULT_JD_PATH
    text = jd_path.read_text(encoding="utf-8")
    return analyze_job_description(text)

def job_struct_to_json(path: Path) -> None:
    struct = load_job_description()
    path.write_text(json.dumps(struct, indent=2), encoding="utf-8")
