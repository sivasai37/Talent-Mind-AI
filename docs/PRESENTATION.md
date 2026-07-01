# Presentation Content — TalentMind AI

## Problem Statement
- Hiring decisions are noisy and time-consuming.
- Recruiters need fast, explainable candidate shortlists.

## Architecture
- Lightweight React dashboard for JD upload and explainability.
- Django + DRF backend hosting scoring engines and vector store.
- Semantic retrieval + feature engines + LLM recruiter agent for hybrid ranking.

## AI Pipeline
- Embed candidate profiles and JD with SentenceTransformers.
- Retrieve top-N with FAISS.
- Apply Skill / Experience / Behavioral scoring.
- Call Gemini recruiter agent for qualitative signals.
- Combine via weighted hybrid formula to yield final score.

## Ranking Formula
- final = 0.35 * semantic + 0.25 * skill + 0.15 * experience + 0.15 * recruitability + 0.10 * llm

## Results
- Demonstrated explainability: semantic, skill, experience, behavioral, LLM
- CSV exports and submission-ready outputs

## Innovation
- LLM recruiter agent that synthesizes qualitative strengths/weaknesses
- Explainable per-candidate breakdowns for fast hiring decisions

## Demo Walkthrough
- Upload/paste JD → Analyze → Rank → Inspect candidate explainability → Export CSV

