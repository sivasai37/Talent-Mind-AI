# ⚡ HireGenius AI — Final Submission README

**Beyond Keywords. Intelligent Hiring Starts Here.**

> An AI-powered recruitment intelligence platform that ranks candidates the way elite recruiters do — understanding skills, career trajectory, behavioral signals, and future potential.

---

## 🏆 Hackathon Submission Overview

| Field | Details |
|-------|---------|
| **Project Name** | HireGenius AI |
| **Tagline** | Beyond Keywords. Intelligent Hiring Starts Here. |
| **Submission Date** | June 12, 2026 |
| **Category** | AI / Recruitment Intelligence |
| **Tech Stack** | Django + React + Gemini 1.5 Flash + FAISS |
| **Key Innovation** | 5-Agent AI Evaluation System with Explainable Rankings |

---

## 🚀 Quick Start (3 Steps)

### Step 1 — Backend Setup

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

### Step 2 — Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Step 3 — Open the App

Navigate to: **http://localhost:5173**

---

## 🔑 Environment Variables

```bash
# Optional — enables live Gemini 1.5 Flash AI evaluation
GEMINI_API_KEY=your-gemini-api-key-here

# Production only
DJANGO_SECRET_KEY=your-secret-key-for-production
DJANGO_DEBUG=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

> **Note:** HireGenius AI works **fully offline** without a Gemini API key using a sophisticated fallback ranking engine that still provides all features.

---

## 🤖 What Makes HireGenius AI Different

### 5-Agent Multi-Agent AI System

```
Job Description Input
       │
       ▼
Role Type Auto-Detection
  (backend / leadership / research / data / design / frontend)
       │
       ▼
Dynamic Weight Selection
  (e.g., Research: Semantic 40%, Skill 20%, LLM 15%)
       │
       ▼
FAISS Semantic Search (Top-K candidates)
       │
       ▼
Multi-Agent Evaluation (5 Agents in Parallel)
  ├── Agent 1: Skill Evaluator       → Matched skills, missing skills, learning path
  ├── Agent 2: Experience Evaluator  → Career trajectory, growth forecast
  ├── Agent 3: Behavior Evaluator    → Culture fit, risk assessment
  ├── Agent 4: Recruiter Evaluator   → Salary fit, time-to-hire signals
  └── Agent 5: Hiring Committee      → Consensus, confidence, potential score
       │
       ▼
Weighted Final Score + Full Explainability Output
  (Why Selected, Interview Questions, Growth Forecast, CSV Export)
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rank/` | Rank candidates against a job description |
| POST | `/api/analyze-jd/` | Analyze and structure a job description |
| GET | `/api/candidates/` | List all candidates in the pool |
| GET | `/api/rankings/` | List all ranking sessions |
| GET | `/api/rankings/<id>/` | Get a specific ranking session |
| GET | `/api/rankings/export/?job_id=<id>&format=submission` | Export submission CSV |
| GET | `/api/stats/` | Executive dashboard statistics |
| POST | `/api/talent-insights/` | AI market and skill insights |

---

## 📊 Submission Artifacts

| Artifact | Location | Description |
|----------|----------|-------------|
| Source Code | `source_code/` | Full Django + React source |
| Architecture | `../docs/architecture.md` | System architecture documentation |
| API Docs | `../docs/API.md` | Full API documentation |
| Presentation (PPTX) | `TalentMind_AI_Presentation.pptx` | Hackathon slides |
| Presentation (PDF) | `TalentMind_AI_Presentation.pdf` | Hackathon slides (PDF) |
| Sample CSV Output | `ranked_candidates.csv` | 5-candidate ranking sample |
| Screenshots | `screenshots/` | Dashboard and feature screenshots |
| Submission Checklist | `submission_checklist.md` | Fully completed checklist |

---

## 🎨 Dashboard Features

### Executive Overview
- 4 KPI cards: Total Candidates, Rankings Run, Avg Final Score, Avg Potential Score
- Top Candidate spotlight with score, potential, and risk indicator
- Recommendation distribution (Strong / Moderate / Weak Fit breakdown)
- Hiring funnel with top 5 candidates and visual progress bars

### Rank Candidates View
- Job Description input with 3 built-in templates (Backend, ML Research, Engineering Manager)
- Real-time job intelligence summary (required skills, seniority, behavioral traits)
- Dynamic weights display — auto-adapts for each role type
- Enterprise ranking table: rank badges (🥇🥈🥉), score bars, potential score, risk level

### 5-Tab Explainability Panel (per candidate)
| Tab | Content |
|-----|---------|
| **Overview** | Why Selected/Rejected, Role Fit, Strengths/Weaknesses, Radar Chart |
| **Scores** | Multi-dimensional breakdown with per-agent explanations |
| **Gap Analysis** | Missing Skills, Learning Path, Salary Fit Analysis |
| **Interview** | AI-generated gap-targeted interview questions |
| **Growth** | Future Role Predictions, 1-3 Year Career Forecast |

---

## ⚖️ Dynamic Role-Aware Weights

| Role Type | Semantic | Skill | Experience | Recruitability | LLM |
|-----------|----------|-------|------------|----------------|-----|
| Backend | 25% | **35%** | 20% | 10% | 10% |
| Frontend | 25% | **35%** | 20% | 10% | 10% |
| Leadership | 20% | 20% | **35%** | 15% | 10% |
| Research | **40%** | 20% | 15% | 10% | **15%** |
| Data | 30% | 30% | 20% | 10% | 10% |
| Design | 30% | 25% | 20% | 15% | 10% |

---

## 🔐 Security Features

| Feature | Implementation |
|---------|---------------|
| CSV Injection Prevention | All cell values prefixed with `'` if starting with `=`, `+`, `-`, `@` |
| Input Validation | Max 20,000 chars for job descriptions; top-K capped at 50 |
| Secret Key Protection | Warning logged if default `SECRET_KEY` detected in production |
| CORS Control | `CORS_ALLOWED_ORIGINS` via environment variable in production |
| API Key Security | `GEMINI_API_KEY` loaded from env only — never hardcoded |

---

## 📁 Project Structure

```
HireGenius AI/
├── backend/
│   ├── api/
│   │   ├── models.py           # Candidate, Job, RankingJob, RankingResult
│   │   ├── views.py            # 8 API endpoints with full validation
│   │   ├── serializers.py      # DRF serializers (all new fields)
│   │   ├── urls.py             # URL routing
│   │   └── services/
│   │       ├── multi_agent.py  # ⭐ 5-agent AI evaluation system
│   │       ├── ranking.py      # Core engine + dynamic weights
│   │       ├── embeddings.py   # Sentence transformers + fallback
│   │       ├── vector_store.py # FAISS integration
│   │       ├── jd_understanding.py  # JD analysis + role detection
│   │       ├── skill_engine.py      # Skill fit scoring
│   │       ├── experience_engine.py # Career trajectory analysis
│   │       └── behavioral_engine.py # Recruitability signals
│   └── core/
│       ├── settings.py         # Config + role weights
│       └── urls.py             # Root URL config
├── frontend/
│   └── src/
│       ├── App.jsx             # Enterprise dashboard main layout
│       ├── api.js              # API client
│       ├── index.css           # Enterprise design system (dark theme)
│       └── components/
│           ├── ExecutiveOverview.jsx    # Stats, funnel, distributions
│           ├── ExplainabilityPanel.jsx  # 5-tab candidate report
│           ├── RankingTable.jsx         # Enterprise ranking table
│           ├── RadarChart.jsx           # SVG radar chart (zero-dep)
│           ├── ScoreBreakdownChart.jsx  # Animated score bars
│           ├── JobDescriptionUploader.jsx # JD input with examples
│           └── AIInsightsPanel.jsx      # Market intelligence
├── FINAL_SUBMISSION/
│   ├── README.md                    ← This file
│   ├── submission_checklist.md
│   ├── ranked_candidates.csv
│   ├── architecture_diagram.png
│   ├── TalentMind_AI_Presentation.pptx
│   ├── TalentMind_AI_Presentation.pdf
│   ├── screenshots/
│   └── source_code/
├── docs/
│   ├── architecture.md
│   └── API.md
├── requirements.txt
└── README.md
```

---

## 🏆 Innovation Highlights

1. **Multi-Agent Architecture** — 5 specialized AI evaluators with consensus engine (vs. single LLM call)
2. **Dynamic Role Weights** — Auto-detected role type adjusts scoring per job category
3. **Candidate Potential Score** — Predicts growth trajectory, not just current fit
4. **1-3 Year Growth Forecast** — Career trajectory modeling per candidate
5. **Skill Gap → Learning Path** — From gap identification to specific course recommendations
6. **AI Interview Generator** — Context-aware questions targeting specific candidate gaps
7. **Hiring Risk Predictor** — Pre-interview risk assessment (Low / Medium / High)
8. **Zero-dependency SVG Radar Chart** — Candidate vs. Job comparison across 5 dimensions
9. **Salary Fit Analysis** — Alignment check between candidate expectation and role range
10. **Semantic Role Detection** — Automatically classifies job type from raw description text

---

*HireGenius AI — Beyond Keywords. Intelligent Hiring Starts Here. ⚡*
*Built for hackathon excellence.*
