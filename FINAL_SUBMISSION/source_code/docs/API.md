# API Documentation

Base URL: `/api/`

Endpoints:

- `POST /api/analyze-jd/`
  - Payload: `{ "title": "<job title>", "job_description": "<text>" }`
  - Returns: structured job analysis (top skills, experience focus, behavioral themes)

- `POST /api/rank/`
  - Payload: `{ "title": "<job title>", "job_description": "<text>", "top_k": 10 }`
  - Returns: `RankingJob` object with `results` array. Each result contains:
    - `candidate` (nested candidate object)
    - `semantic_score`, `skill_score`, `experience_score`, `recruitability_score`, `llm_score`, `final_score`
    - `strengths`, `weaknesses`, `missing_skills`, `recruiter_summary`
    - `semantic_explanation`, `skill_explanation`, `experience_explanation`, `behavioral_explanation`, `gemini_explanation`

- `GET /api/candidates/`
  - Returns: list of candidates

- `GET /api/rankings/`
  - Returns: list of `RankingJob` runs with nested `results`.

- `GET /api/rankings/export/?job_id=<id>&format=[submission]`
  - Returns: CSV export for the specified job. If `job_id` omitted, exports the latest job.
  - `format=submission` produces a condensed submission-ready CSV.

Authentication: None (demo)

Notes: Set `GEMINI_API_KEY` in settings or environment to enable LLM recruiter agent calls.
