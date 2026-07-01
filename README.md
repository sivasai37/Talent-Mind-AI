# ⚡ HireGenius AI

**Beyond Keywords. Intelligent Hiring Starts Here.**

> An AI-powered recruitment intelligence platform that ranks candidates the way elite recruiters do — understanding skills, career trajectory, behavioral signals, and future potential.

---

## 🏆 Problem Statement

Traditional ATS systems fail. They reject 75% of qualified candidates through keyword matching, miss high-potential candidates, and produce zero explainability for hiring decisions.

**The cost of a bad hire: $17,000–$240,000 per role.**

HireGenius AI solves this with multi-agent AI evaluation, semantic understanding, and explainable rankings.

---

## 💡 Solution

HireGenius AI is the first recruitment intelligence platform that:

- 🤖 **5 Specialized AI Agents** — Skill Evaluator, Experience Evaluator, Behavior Evaluator, Recruiter Evaluator, and Hiring Committee Consensus
- 🎯 **Dynamic Role-Aware Weights** — Automatically adapts ranking logic for Backend, Leadership, Research, and Design roles
- 📊 **Explainable AI** — Every ranking comes with Why Selected, Why Rejected, Strengths, Weaknesses, Learning Path, and Interview Questions
- 🚀 **Potential Score** — Predicts candidate growth potential, not just current fit
- ⚠️ **Hiring Risk Predictor** — Flags Low/Medium/High risk candidates before interview
- 📈 **1-3 Year Growth Forecast** — Predicts where a candidate will be in 1-3 years
- 🎙️ **AI Interview Generator** — Tailored interview questions based on gaps
- 💰 **Salary Fit Analysis** — Aligns expectations with role range

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HireGenius AI Platform                       │
├───────────────────────────────┬─────────────────────────────────┤
│     React Enterprise Dashboard │     Django REST API Backend     │
│  ┌────────────────────────────┐│  ┌──────────────────────────┐  │
│  │ Executive Overview         ││  │ Job Description Analyzer │  │
│  │ Ranking Panel              ││  │ Role Type Detector       │  │
│  │ ExplainabilityPanel (5 tabs)│  │ Dynamic Weight Engine    │  │
│  │ RadarChart (SVG)           ││  │ FAISS Vector Store       │  │
│  │ AI Insights Dashboard      ││  │ Sentence Transformers    │  │
│  │ History View               ││  │ Multi-Agent System       │  │
│  └────────────────────────────┘│  └──────────────────────────┘  │
├───────────────────────────────┴─────────────────────────────────┤
│                      Multi-Agent AI Layer                        │
│  Agent 1: Skill Evaluator → Agent 2: Experience Evaluator      │
│  Agent 3: Behavior Evaluator → Agent 4: Recruiter Evaluator     │
│  Agent 5: Hiring Committee Consensus (Final Decision)           │
├─────────────────────────────────────────────────────────────────┤
│              Semantic Search (FAISS + Sentence Transformers)     │
│              Gemini 1.5 Flash API (with robust fallback)        │
│              SQLite / PostgreSQL Database + DB Indexes           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Pipeline

```
Job Description Input
        │
        ▼
Job Understanding Engine
  (Required Skills, Experience, Seniority, Behavioral Traits, Industry)
        │
        ▼
Role Type Detection
  (backend / frontend / leadership / research / data / design / general)
        │
        ▼
Dynamic Weight Selection
  (e.g., Research: Semantic 40%, Skill 20%, Experience 15%)
        │
        ▼
FAISS Semantic Search
  (Top-K candidates by semantic similarity)
        │
        ▼
Multi-Agent Evaluation (5 Agents in Parallel)
  ├── Agent 1: Skill Evaluator (matched/missing/learning path)
  ├── Agent 2: Experience Evaluator (trajectory/growth/forecast)
  ├── Agent 3: Behavior Evaluator (culture fit/risk/engagement)
  ├── Agent 4: Recruiter Evaluator (salary fit/time-to-hire)
  └── Agent 5: Hiring Committee (consensus/confidence/potential)
        │
        ▼
Weighted Final Score
  (Dynamic weights × 5 component scores)
        │
        ▼
Explainable Ranking Output
  (Why Selected, Interview Questions, Learning Path, Growth Forecast)
```

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI / LLM** | Google Gemini 1.5 Flash |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) + Fallback |
| **Vector Search** | FAISS (in-memory, persistent embeddings) |
| **Backend** | Django 4.x + Django REST Framework |
| **Database** | SQLite (dev) / PostgreSQL (production) |
| **Frontend** | React 18 + Vite |
| **Styling** | Vanilla CSS Design System (dark enterprise theme) + Tailwind utilities |
| **Charts** | SVG-based RadarChart (zero dependency) |
| **CSV Export** | Python csv module (injection-safe) |

---

## 🔧 Local Setup & Testing

### 1. Prerequisites
- Python 3.10+
- Node.js 18+

### 2. Environment Variables Setup
Create a `.env` file in the project root (use `.env.example` as a template):
```bash
cp .env.example .env
```
Key variables:
- `DJANGO_SECRET_KEY`: Set a secure secret key.
- `DJANGO_DEBUG`: Set to `True` for local development.
- `GEMINI_API_KEY`: Set your Gemini API key (optional, fallback is used if not provided).
- `VITE_API_BASE`: Set to `http://localhost:8000/api` for dev server connection.

### 3. Running Django Backend
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install requirements
pip install -r ../requirements.txt

# Run migrations
python manage.py migrate

# Start backend dev server
python manage.py runserver
```

### 4. Running Tests & Offline Ranker Scripts
With your virtual environment active, you can execute the test suite and run offline ranker tasks:
```bash
# Run backend tests to verify database and ranking adapters
python manage.py test

# Rebuild FAISS index and generate submission.csv
python rank.py --out submission.csv --build-index

# Validate the generated submission
python validate_submission.py submission.csv

# Verify the job description parsing engine
python verify_jd_parser.py
```

### 5. Running React Frontend
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5173`.

---

## 🐳 Docker Setup

We provide production-ready Docker configurations to build and run the services in a isolated stack.

### Run via Docker Compose
Make sure you have `.env` set up in the root directory. Then start the compose stack:
```bash
docker-compose up --build
```
This builds and starts:
- **Backend Service** (Django + Gunicorn) exposed at `http://localhost:8000` with container health checks.
- **Frontend Service** (Nginx + static build) exposed at `http://localhost:80`.

---

## 🚀 Production Deployment

### 1. Render Blueprint Deployment
You can deploy the complete stack using the provided [render.yaml](file:///d:/kiran/TalentMind%20AI/TalentMind%20AI/render.yaml) blueprint:
1. Connect your GitHub repository to Render.
2. In Render, select **Blueprints** -> **New Blueprint Instance**.
3. Choose your repository.
4. Render will parse `render.yaml` and configure:
   - A PostgreSQL database (`talent-mind-db`).
   - A Gunicorn backend web service (`talent-mind-backend`).
   - A static site frontend (`talent-mind-frontend`) served via high-performance CDN.
5. In the Render Dashboard, manually configure your `GEMINI_API_KEY` and other credentials.

### 2. Railway Deployment
To deploy on Railway:
1. Connect your repository to Railway.
2. Add a new service from your GitHub repository.
3. Railway will auto-detect the root `Procfile` and deploy the backend.
4. Add a PostgreSQL plugin to auto-generate `DATABASE_URL`.
5. Deploy the React frontend by selecting the `/frontend` subfolder as the root directory, building via `npm run build` and serving the static assets.

### 3. VPS Deployment (Ubuntu + Nginx + Gunicorn)
We have provided sample configuration files in the [deployment/](file:///d:/kiran/TalentMind%20AI/TalentMind%20AI/deployment) directory:
- **Gunicorn Systemd Service:** [gunicorn.service](file:///d:/kiran/TalentMind%20AI/TalentMind%20AI/deployment/gunicorn.service)
- **Nginx Virtual Host Config:** [nginx.vhost.conf](file:///d:/kiran/TalentMind%20AI/TalentMind%20AI/deployment/nginx.vhost.conf)

Steps to configure:
1. Clone the project to `/var/www/talent-mind`.
2. Set up virtual environment, install requirements, and collect static files:
   ```bash
   cd /var/www/talent-mind
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd backend
   python manage.py collectstatic --noinput
   ```
3. Build the frontend static assets:
   ```bash
   cd /var/www/talent-mind/frontend
   npm install
   npm run build
   ```
4. Setup systemd Gunicorn service:
   ```bash
   sudo cp /var/www/talent-mind/deployment/gunicorn.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```
5. Setup Nginx Virtual Host:
   ```bash
   sudo cp /var/www/talent-mind/deployment/nginx.vhost.conf /etc/nginx/sites-available/talent-mind
   sudo ln -s /etc/nginx/sites-available/talent-mind /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```


---

## 🎯 Usage

1. **Start both servers** (backend on port 8000, frontend on port 5173)
2. **Navigate to** `http://localhost:5173`
3. **Click "Start Ranking"** in the sidebar
4. **Paste a job description** (or load an example from the UI)
5. **Click "Analyze & Rank"**
6. **View ranked candidates** with full explainability
7. **Click any candidate** to see their AI evaluation report
8. **Switch between tabs**: Overview, Scores, Gap Analysis, Interview Questions, Growth
9. **Export CSV** for submission or detailed analysis

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rank/` | Rank candidates against a job description |
| POST | `/api/analyze-jd/` | Analyze and structure a job description |
| GET | `/api/candidates/` | List all candidates in the pool |
| GET | `/api/rankings/` | List all ranking sessions |
| GET | `/api/rankings/<id>/` | Get a specific ranking session |
| GET | `/api/rankings/export/?job_id=<id>&format=full` | Export full ranking CSV |
| GET | `/api/rankings/export/?job_id=<id>&format=submission` | Export submission CSV |
| GET | `/api/stats/` | Executive dashboard statistics |
| POST | `/api/talent-insights/` | AI market and skill insights |
| GET | `/api/docs/` | Interactive API documentation |

---

## 🎨 Dashboard Features

### Executive Overview
- 4 KPI stat cards (Candidates, Rankings, Avg Score, Avg Potential)
- Top Candidate spotlight with score and recommendation
- Recommendation distribution bar (Strong / Moderate / Weak)
- Risk distribution (Low / Medium / High)
- Hiring Funnel — top 5 candidates with visual progress bars

### Rank Candidates View
- Job Description input with 3 example templates (Backend, ML Research, Engineering Manager)
- Real-time job intelligence summary (required skills, seniority, behavioral traits)
- Dynamic weights display (role-aware: Backend = 35% skill, Research = 40% semantic, etc.)
- Enterprise ranking table with rank badges (🥇🥈🥉), score bars, potential score, risk indicator
- 5-tab explainability panel per candidate:
  - **Overview**: Why Selected/Rejected, Role Fit Analysis, Strengths/Weaknesses, Radar Chart
  - **Scores**: Multi-dimensional breakdown with explanations
  - **Gap Analysis**: Missing Skills, Learning Path, Salary Fit
  - **Interview**: AI-generated targeted interview questions
  - **Growth**: Future Role Predictions, 1-3 Year Growth Forecast

### AI Insights Panel
- Market trend insights by role type
- Skill trend analysis
- Hiring recommendations
- Talent pool statistics

---

## 🔐 Security Features

- ✅ CSV injection prevention (dangerous formula characters escaped)
- ✅ Input length validation (max 20,000 chars for job descriptions)
- ✅ Secret key warning in dev mode
- ✅ CORS restricted in production (via env var)
- ✅ Content-Type headers on all responses
- ✅ Top-K capped at 50 to prevent resource exhaustion

---

## 📊 Dynamic Role-Aware Weights

| Role Type | Semantic | Skill | Experience | Recruitability | LLM |
|-----------|----------|-------|------------|----------------|-----|
| Backend | 25% | **35%** | 20% | 10% | 10% |
| Frontend | 25% | **35%** | 20% | 10% | 10% |
| Leadership | 20% | 20% | **35%** | 15% | 10% |
| Research | **40%** | 20% | 15% | 10% | **15%** |
| Data | 30% | 30% | 20% | 10% | 10% |
| Design | 30% | 25% | 20% | 15% | 10% |

---

## 🏆 Innovation Highlights

1. **Multi-Agent Architecture** — 5 specialized evaluators with consensus engine (vs. single LLM call)
2. **Dynamic Role Weights** — Auto-detected role type adjusts scoring for each job category
3. **Candidate Potential Score** — Predicts growth trajectory, not just current fit
4. **1-3 Year Growth Forecast** — Career trajectory modeling per candidate
5. **Skill Gap → Learning Path** — From gap identification to specific course recommendations
6. **AI Interview Generator** — Context-aware questions targeting specific candidate gaps
7. **Hiring Risk Predictor** — Pre-interview risk assessment with specific risk factors
8. **Zero-dependency SVG Radar Chart** — Candidate vs. Job comparison across 5 dimensions
9. **Salary Fit Analysis** — Alignment check between candidate expectation and role range
10. **Semantic Role Detection** — Automatically classifies job type from description

---

## 📈 Future Work

- [ ] **Bias Auditing Panel** — Detect and flag demographic bias in rankings
- [ ] **Candidate Interview Scheduling** — One-click calendar integration
- [ ] **Multi-Candidate Comparison** — Side-by-side comparison matrix
- [ ] **PDF Report Generation** — Printable recruiter-ready reports
- [ ] **Batch Upload** — Import candidates from LinkedIn/CSV
- [ ] **Real-time GitHub Analysis** — Live GitHub API integration for activity scoring
- [ ] **WebSocket Updates** — Real-time ranking progress for large pools
- [ ] **Role Benchmark Database** — Compare candidates against industry benchmarks
- [ ] **Diversity Analytics** — Inclusion and diversity reporting
- [ ] **ATS Integration** — Workday, Greenhouse, Lever connectors

---

## 📁 Project Structure

```
HireGenius AI/
├── backend/
│   ├── api/
│   │   ├── models.py           # Candidate, Job, RankingJob, RankingResult models
│   │   ├── views.py            # 8 API endpoints with full validation
│   │   ├── serializers.py      # DRF serializers with all new fields
│   │   ├── urls.py             # URL routing
│   │   └── services/
│   │       ├── multi_agent.py  # ⭐ 5-agent AI evaluation system
│   │       ├── ranking.py      # Core ranking engine + dynamic weights
│   │       ├── embeddings.py   # Sentence transformers + fallback
│   │       ├── vector_store.py # FAISS integration
│   │       ├── jd_understanding.py  # JD analysis + role detection
│   │       ├── skill_engine.py      # Skill fit scoring
│   │       ├── experience_engine.py # Career trajectory analysis
│   │       └── behavioral_engine.py # GitHub + recruitability signals
│   └── core/
│       ├── settings.py         # Project config + role weights
│       └── urls.py             # Root URL config
├── frontend/
│   └── src/
│       ├── App.jsx             # Enterprise dashboard main layout
│       ├── api.js              # API client
│       ├── index.css           # Enterprise design system (dark theme)
│       └── components/
│           ├── ExecutiveOverview.jsx   # Stats, funnel, distributions
│           ├── ExplainabilityPanel.jsx # 5-tab candidate report
│           ├── RankingTable.jsx        # Enterprise ranking table
│           ├── RadarChart.jsx          # SVG radar chart
│           ├── ScoreBreakdownChart.jsx # Animated score bars
│           ├── JobDescriptionUploader.jsx # JD input with examples
│           └── AIInsightsPanel.jsx     # Market intelligence
├── FINAL_SUBMISSION/
│   ├── HireGenius_AI_Presentation.pptx
│   ├── HireGenius_AI_Presentation.pdf
│   └── screenshots/
├── docs/
└── README.md                   # This file
```

---

## 🏁 Final Submission Artifacts

- `FINAL_SUBMISSION/HireGenius_AI_Presentation.pptx`
- `FINAL_SUBMISSION/HireGenius_AI_Presentation.pdf`
- `FINAL_SUBMISSION/ranked_candidates.csv`
- `FINAL_SUBMISSION/screenshots/`
- `HireGenius_AI_Final_Submission.zip`

---

## 📝 Notes

- Set `GEMINI_API_KEY` environment variable for live Gemini 1.5 Flash AI evaluation
- Without API key: sophisticated fallback engine provides full evaluation
- All Gemini API calls use model `gemini-1.5-flash` (NOT deprecated gemini-1.0)
- FAISS index is cached in-memory and only rebuilt when candidate pool changes
- DB indexes on all frequently-queried fields for production performance

---

*Built for hackathon excellence. HireGenius AI — Beyond Keywords. Intelligent Hiring Starts Here.* ⚡
