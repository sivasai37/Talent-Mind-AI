"""Paths and role-aware weight presets for the offline ranker."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "challenge_dataset" / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"
_CANDIDATES_JSONL = DATA_DIR / "candidates.jsonl"
_CANDIDATES_GZ = DATA_DIR / "candidates.jsonl.gz"
DEFAULT_CANDIDATES_PATH = _CANDIDATES_GZ if _CANDIDATES_GZ.exists() else _CANDIDATES_JSONL
DEFAULT_JD_PATH = PROJECT_ROOT.parent / "job_description.txt"
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
FAISS_DIR = PROJECT_ROOT / "faiss_index"

RETRIEVAL_TOP_K = 500
FINAL_TOP_K = 100
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_BATCH_SIZE = 128

# Hybrid weights — research/backend AI role (semantic tilt per JD)
DEFAULT_WEIGHTS = {
    "semantic": 0.30,
    "skill": 0.25,
    "experience": 0.15,
    "behavior": 0.10,
    "recruiter": 0.10,
    "career": 0.05,
    "education": 0.03,
    "assessment": 0.02,
}

ROLE_WEIGHTS = {
    "backend": {"semantic": 0.25, "skill": 0.30, "experience": 0.15, "behavior": 0.10, "recruiter": 0.10, "career": 0.05, "education": 0.03, "assessment": 0.02},
    "leadership": {"semantic": 0.20, "skill": 0.20, "experience": 0.25, "behavior": 0.10, "recruiter": 0.12, "career": 0.08, "education": 0.03, "assessment": 0.02},
    "research": {"skill": 0.35, "semantic": 0.15, "experience": 0.20, "education": 0.10, "publications": 0.10, "behavior": 0.05, "recruiter": 0.05},
}

CONSULTING_FIRMS = [
    "tcs", "tata consultancy", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "tech mahindra", "l&t", "lnt", "mindtree",
]

PRODUCT_INDICATORS = [
    "flipkart", "swiggy", "zomato", "razorpay", "freshworks", "meesho",
    "cred", "phonepe", "paytm", "ola", "uber", "netflix", "adobe", "meta",
    "google", "microsoft", "amazon", "apple", "spotify", "linkedin",
    "yellow.ai", "haptik", "verloop", "glance", "zoho", "byju", "unacademy",
]

AI_TITLE_KEYWORDS = [
    "ai engineer", "ml engineer", "machine learning", "nlp", "deep learning",
    "research engineer", "applied scientist", "data scientist", "recommendation",
    "search engineer", "retrieval", "ranking", "llm", "computer vision engineer",
]

NON_TECH_TITLES = [
    "hr manager", "accountant", "marketing manager", "sales executive",
    "content writer", "graphic designer", "civil engineer", "mechanical engineer",
    "customer support", "operations manager", "business analyst", "project manager",
    "qa engineer", "frontend engineer", "mobile developer", "java developer",
    ".net developer", "net developer", "sales manager", "account executive",
]

IDEAL_EXP_MIN = 5.0
IDEAL_EXP_MAX = 9.0

PREFERRED_LOCATIONS = ["pune", "noida", "delhi", "gurgaon", "ghaziabad", "faridabad", "ncr"]
GOOD_LOCATIONS = ["hyderabad", "mumbai", "bangalore", "bengaluru", "chennai"]
