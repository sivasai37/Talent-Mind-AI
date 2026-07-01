# 📡 HireGenius AI — API Documentation

**Beyond Keywords. Intelligent Hiring Starts Here.**

---

## Overview

| Field | Value |
|-------|-------|
| **Base URL (Development)** | `http://localhost:8000/api/` |
| **Base URL (Production)** | `https://your-domain.com/api/` |
| **Content-Type** | `application/json` |
| **Authentication** | None (hackathon demo) |
| **API Version** | v1 |

> **Environment Variable:** Set `GEMINI_API_KEY` in your environment to enable live Gemini 1.5 Flash AI evaluation. Without it, the sophisticated fallback engine provides full functionality.

---

## Endpoints

### 1. `POST /api/rank/`

Rank candidates against a job description using the 5-agent multi-agent AI system.

**Request Body:**

```json
{
  "title": "Senior Python Backend Engineer",
  "job_description": "We are looking for a Senior Python Backend Engineer with 5+ years of experience in Django, REST APIs, PostgreSQL, Redis, and AWS. The ideal candidate has strong system design skills and experience with microservices architecture.",
  "top_k": 10
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Job title |
| `job_description` | string | Yes | Full JD text (max 20,000 chars) |
| `top_k` | integer | No | Number of candidates to return (default: 10, max: 50) |

**Response (200 OK):**

```json
{
  "job_id": "42",
  "role_type": "backend",
  "weights_used": {
    "semantic": 0.25,
    "skill": 0.35,
    "experience": 0.20,
    "recruitability": 0.10,
    "llm": 0.10
  },
  "job_analysis": {
    "required_skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS"],
    "preferred_skills": ["Docker", "Kubernetes", "CI/CD"],
    "years_experience": 5,
    "seniority_level": "Senior",
    "behavioral_traits": ["system design", "team collaboration", "code review"],
    "industry_focus": "Backend Engineering"
  },
  "results": [
    {
      "rank": 1,
      "candidate_id": "C001",
      "full_name": "Priya Sharma",
      "candidate": {
        "id": 1,
        "full_name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "experience_years": 7,
        "skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS", "Docker"]
      },
      "semantic_score": 88.4,
      "skill_score": 91.2,
      "experience_score": 85.0,
      "recruitability_score": 78.5,
      "llm_score": 87.3,
      "final_score": 88.1,
      "recommendation": "Strong Fit",
      "potential_score": 84.0,
      "confidence_score": 91.0,
      "risk_level": "Low",
      "strengths": [
        "Exceptional Python and Django expertise (7 years)",
        "Full AWS cloud stack experience",
        "Strong PostgreSQL + Redis performance tuning background"
      ],
      "weaknesses": [
        "Limited Kubernetes orchestration experience",
        "No prior experience with GraphQL APIs"
      ],
      "missing_skills": ["Kubernetes", "GraphQL"],
      "learning_path": [
        "Complete 'Kubernetes for Developers' on Coursera (4 weeks)",
        "Build a GraphQL API with Strawberry Python (2 weeks project)",
        "AWS Solutions Architect Associate certification (optional)"
      ],
      "interview_questions": [
        "Describe a system you designed for 100K+ concurrent users.",
        "How do you approach database schema migrations with zero downtime?",
        "Walk us through your experience with Redis pub/sub vs. queues."
      ],
      "growth_forecast": {
        "1_year": "Senior Backend Engineer / Tech Lead",
        "3_year": "Principal Engineer / Engineering Manager"
      },
      "salary_fit": {
        "expected_range": "$120,000 - $145,000",
        "role_range": "$130,000 - $160,000",
        "fit": "Strong Fit"
      },
      "recruiter_summary": "Priya Sharma is an exceptional candidate for this Senior Backend Engineer role. With 7 years of hands-on Python/Django experience and full AWS stack proficiency, she exceeds the core technical requirements. Minor gaps in Kubernetes and GraphQL can be addressed through a structured 6-week onboarding plan. Recommend fast-tracking to final interview round.",
      "semantic_explanation": "Strong semantic alignment with job description — 88.4% cosine similarity indicating close match on role themes and technical vocabulary.",
      "skill_explanation": "91.2% skill match: 5 of 5 required skills matched. 2 of 3 preferred skills matched (Docker present, Kubernetes and GraphQL missing).",
      "experience_explanation": "7 years experience exceeds the 5-year requirement. Career trajectory shows progressive senior-level responsibility.",
      "behavioral_explanation": "Active GitHub profile with 847 contributions in the last year. High recruitability signals — engaged, recent activity.",
      "gemini_explanation": "Gemini Agent consensus: Strong Fit with 91% confidence. All 5 agents independently rated candidate in top tier."
    }
  ],
  "total_candidates": 1
}
```

---

### 2. `POST /api/analyze-jd/`

Analyze and structure a job description without running full candidate ranking.

**Request Body:**

```json
{
  "title": "Engineering Manager",
  "job_description": "We are hiring an Engineering Manager to lead a team of 8 backend engineers. You will own delivery, conduct 1:1s, drive technical roadmap, and partner with product management."
}
```

**Response (200 OK):**

```json
{
  "role_type": "leadership",
  "weights": {
    "semantic": 0.20,
    "skill": 0.20,
    "experience": 0.35,
    "recruitability": 0.15,
    "llm": 0.10
  },
  "required_skills": ["Team Leadership", "Technical Roadmap", "Delivery Management"],
  "preferred_skills": ["Engineering Management", "1:1 Coaching", "Product Partnership"],
  "years_experience": 5,
  "seniority_level": "Manager",
  "behavioral_traits": ["leadership", "mentoring", "stakeholder communication"],
  "industry_focus": "Engineering Leadership"
}
```

---

### 3. `GET /api/candidates/`

Retrieve all candidates in the talent pool.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Results per page (default: 20, max: 100) |
| `search` | string | Filter by name or skill |

**Response (200 OK):**

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/candidates/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "full_name": "Priya Sharma",
      "email": "priya.sharma@example.com",
      "experience_years": 7,
      "skills": ["Python", "Django", "PostgreSQL", "Redis", "AWS"],
      "github_url": "https://github.com/priyasharma",
      "created_at": "2026-05-10T12:00:00Z"
    }
  ]
}
```

---

### 4. `GET /api/rankings/`

List all ranking sessions.

**Response (200 OK):**

```json
[
  {
    "id": 42,
    "job": {
      "id": 15,
      "title": "Senior Python Backend Engineer",
      "role_type": "backend"
    },
    "created_at": "2026-06-12T08:30:00Z",
    "weights_used": {
      "semantic": 0.25,
      "skill": 0.35,
      "experience": 0.20,
      "recruitability": 0.10,
      "llm": 0.10
    },
    "result_count": 10
  }
]
```

---

### 5. `GET /api/rankings/<id>/`

Get a specific ranking session with all candidate results.

**Path Parameter:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | RankingJob ID |

**Response (200 OK):** Same as the `POST /api/rank/` response.

---

### 6. `GET /api/rankings/export/`

Export candidate rankings as a CSV file.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | integer | No | Specific ranking job ID (defaults to latest) |
| `format` | string | No | `full` (all fields) or `submission` (condensed) |

**Response (200 OK):**
- Content-Type: `text/csv`
- Content-Disposition: `attachment; filename="ranked_candidates.csv"`

**Submission Format CSV Columns:**

```
rank, candidate_id, full_name, final_score, recommendation, potential_score,
confidence_score, risk_level, strengths, weaknesses, missing_skills,
learning_path, recruiter_summary
```

---

### 7. `GET /api/stats/`

Get executive dashboard statistics across all ranking sessions.

**Response (200 OK):**

```json
{
  "total_candidates": 150,
  "total_rankings": 23,
  "avg_final_score": 67.4,
  "avg_potential_score": 71.2,
  "top_candidate": {
    "id": 1,
    "full_name": "Priya Sharma",
    "final_score": 88.1,
    "recommendation": "Strong Fit",
    "potential_score": 84.0,
    "risk_level": "Low"
  },
  "recommendation_distribution": {
    "strong_fit": 12,
    "moderate_fit": 38,
    "weak_fit": 100
  },
  "risk_distribution": {
    "low": 45,
    "medium": 70,
    "high": 35
  }
}
```

---

### 8. `POST /api/talent-insights/`

Get AI-powered market intelligence and skill trend insights for a role type.

**Request Body:**

```json
{
  "role_type": "backend",
  "focus_skills": ["Python", "Kubernetes", "Go"]
}
```

**Response (200 OK):**

```json
{
  "market_trends": [
    "Go language adoption up 34% for backend roles in 2026",
    "Kubernetes proficiency now required at 72% of backend job postings",
    "Python remains #1 backend language — strong candidate pool"
  ],
  "skill_demand": {
    "Python": "Very High",
    "Kubernetes": "High (rising)",
    "Go": "High (emerging)",
    "Django": "Stable",
    "FastAPI": "Rising"
  },
  "hiring_recommendations": [
    "Expand search to include Go engineers — large transferable skillset",
    "Consider candidates with FastAPI experience as Django alternatives",
    "Kubernetes gap is common — consider providing training for strong Python candidates"
  ],
  "talent_pool_stats": {
    "backend_candidates_in_pool": 42,
    "avg_experience_years": 5.3,
    "top_skills_in_pool": ["Python", "Django", "PostgreSQL", "AWS", "Docker"]
  }
}
```

---

## Error Responses

| Status Code | Meaning | Example |
|-------------|---------|---------|
| `400 Bad Request` | Invalid input (missing required fields, validation failure) | `{"error": "job_description is required"}` |
| `404 Not Found` | Resource not found | `{"error": "RankingJob 99 not found"}` |
| `413 Payload Too Large` | Job description exceeds 20,000 character limit | `{"error": "job_description exceeds maximum length of 20000 characters"}` |
| `422 Unprocessable Entity` | Semantic validation failure | `{"error": "top_k must be between 1 and 50"}` |
| `500 Internal Server Error` | Unexpected server error | `{"error": "Internal server error. Check GEMINI_API_KEY configuration."}` |

---

## Authentication & Security Notes

- **Authentication:** None required for hackathon demo mode.
- **Production:** Integrate JWT or API key middleware using Django REST Framework's `authentication_classes`.
- **Rate Limiting:** Not enforced in demo. Use `django-ratelimit` or API gateway throttling in production.
- **CORS:** Set `CORS_ALLOWED_ORIGINS` environment variable to restrict cross-origin requests in production.
- **GEMINI_API_KEY:** Must be set as an OS environment variable. Never pass via request headers or URL parameters.
- **Top-K Cap:** Maximum 50 candidates per ranking request to prevent resource exhaustion.
- **Input Length Cap:** Job descriptions capped at 20,000 characters.
- **CSV Injection Prevention:** All CSV cell values are sanitized before export (formula-starting characters are escaped).

---

## Sample cURL Commands

### Rank Candidates

```bash
curl -X POST http://localhost:8000/api/rank/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Backend Engineer",
    "job_description": "We are hiring a Senior Python Backend Engineer with 5+ years Django and AWS experience.",
    "top_k": 5
  }'
```

### Analyze Job Description

```bash
curl -X POST http://localhost:8000/api/analyze-jd/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "ML Research Scientist",
    "job_description": "Join our AI research team. You will publish papers, build models, and advance NLP."
  }'
```

### Export CSV

```bash
curl -o ranked_candidates.csv \
  "http://localhost:8000/api/rankings/export/?job_id=42&format=submission"
```

### Get Stats

```bash
curl http://localhost:8000/api/stats/
```

---

*HireGenius AI — Beyond Keywords. Intelligent Hiring Starts Here. ⚡*
