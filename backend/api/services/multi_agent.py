"""
multi_agent.py — HireGenius AI Multi-Agent Recruiter System

Implements 5 specialized AI agents that evaluate candidates from different angles
and generate a consensus hiring recommendation:

  Agent 1: Skill Evaluator
  Agent 2: Experience Evaluator
  Agent 3: Behavior & Culture Evaluator
  Agent 4: Recruiter Signal Evaluator
  Agent 5: Hiring Committee Consensus
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from django.conf import settings


# ---------------------------------------------------------------------------
# Prompt builders for each agent
# ---------------------------------------------------------------------------

def _build_skill_agent_prompt(job_struct: dict, candidate: Any, skill_score: float, skill_details: dict) -> str:
    return (
        "You are a Senior Technical Skill Evaluator AI for HireGenius AI.\n"
        "Your role: Deeply evaluate the candidate's technical skill alignment with the job.\n\n"
        f"Job Role: {job_struct.get('title', 'Unknown')}\n"
        f"Required Skills: {', '.join(job_struct.get('required_skills', []))}\n"
        f"Preferred Skills: {', '.join(job_struct.get('preferred_skills', []))}\n"
        f"Candidate Name: {candidate.full_name}\n"
        f"Candidate Skills: {candidate.skills}\n"
        f"Skill Match Score: {skill_score:.1f}/100\n"
        f"Matched Skills: {', '.join(skill_details.get('matched', []))}\n"
        f"Missing Skills: {', '.join(skill_details.get('missing', []))}\n\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "skill_agent_score": <0-100>,\n'
        '  "matched_skills": [<list of matched skills>],\n'
        '  "missing_skills": [<list of missing skills>],\n'
        '  "skill_strengths": [<2-3 specific strengths>],\n'
        '  "skill_gaps": [<2-3 specific gaps>],\n'
        '  "learning_path": [<3-5 recommended courses/certifications to close gaps>],\n'
        '  "time_to_readiness": "<e.g. 3-6 months>",\n'
        '  "skill_assessment": "<2-3 sentence professional evaluation>"\n'
        "}"
    )


def _build_experience_agent_prompt(job_struct: dict, candidate: Any, exp_score: float, exp_details: dict) -> str:
    return (
        "You are a Senior Career Experience Evaluator AI for HireGenius AI.\n"
        "Your role: Evaluate career trajectory, growth velocity, and experience alignment.\n\n"
        f"Job Role: {job_struct.get('title', 'Unknown')}\n"
        f"Required Experience: {job_struct.get('experience_years', 'Not specified')} years\n"
        f"Seniority Expected: {job_struct.get('seniority', 'Not specified')}\n"
        f"Candidate Name: {candidate.full_name}\n"
        f"Years of Experience: {candidate.years_experience}\n"
        f"Career Profile: {candidate.profile_text[:500] if candidate.profile_text else 'Not provided'}\n"
        f"Experience Score: {exp_score:.1f}/100\n"
        f"Career Growth Detected: {exp_details.get('growth', False)}\n"
        f"Leadership Detected: {exp_details.get('leadership', False)}\n"
        f"Average Tenure: {exp_details.get('avg_tenure', 0):.1f} years\n\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "experience_agent_score": <0-100>,\n'
        '  "career_trajectory": "<ascending|lateral|declining|early-stage>",\n'
        '  "learning_velocity": "<fast|moderate|slow>",\n'
        '  "leadership_potential": <true|false>,\n'
        '  "experience_strengths": [<2-3 strengths>],\n'
        '  "experience_gaps": [<1-2 gaps>],\n'
        '  "future_roles": [<3 potential future positions in 1-3 years>],\n'
        '  "growth_forecast": {\n'
        '    "year_1": "<predicted role/growth>",\n'
        '    "year_2": "<predicted role/growth>",\n'
        '    "year_3": "<predicted role/growth>"\n'
        '  },\n'
        '  "experience_assessment": "<2-3 sentence professional evaluation>"\n'
        "}"
    )


def _build_behavior_agent_prompt(job_struct: dict, candidate: Any, rec_score: float, rec_details: dict) -> str:
    behavioral_traits = job_struct.get("behavioral_traits", [])
    return (
        "You are a Behavioral & Culture Fit Evaluator AI for HireGenius AI.\n"
        "Your role: Assess cultural alignment, behavioral signals, and soft skills.\n\n"
        f"Job Role: {job_struct.get('title', 'Unknown')}\n"
        f"Required Behavioral Traits: {', '.join(behavioral_traits) if behavioral_traits else 'Not specified'}\n"
        f"Candidate Name: {candidate.full_name}\n"
        f"Open to Work: {'Yes' if candidate.open_to_work else 'No'}\n"
        f"Profile Completeness: {candidate.profile_completeness:.0f}%\n"
        f"GitHub Activity: {'Present' if candidate.github_url else 'Not provided'}\n"
        f"Recruitability Score: {rec_score:.1f}/100\n"
        f"Recruiter Response Rate: {candidate.recruiter_response_rate:.0f}%\n"
        f"Interview Completion Rate: {candidate.interview_completion_rate:.0f}%\n"
        f"Offer Acceptance Rate: {candidate.offer_acceptance_rate:.0f}%\n\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "behavior_agent_score": <0-100>,\n'
        '  "culture_fit_score": <0-100>,\n'
        '  "behavioral_strengths": [<2-3 behavioral strengths>],\n'
        '  "behavioral_concerns": [<1-2 concerns if any>],\n'
        '  "engagement_level": "<high|medium|low>",\n'
        '  "risk_factors": [<0-3 specific risk factors>],\n'
        '  "behavior_assessment": "<2-3 sentence professional evaluation>"\n'
        "}"
    )


def _build_recruiter_agent_prompt(job_struct: dict, candidate: Any, all_scores: dict) -> str:
    return (
        "You are an Expert Recruiter Signal Evaluator AI for HireGenius AI.\n"
        "Your role: Evaluate recruiter-facing signals and market competitiveness.\n\n"
        f"Job Role: {job_struct.get('title', 'Unknown')}\n"
        f"Candidate Name: {candidate.full_name}\n"
        f"Salary Expectation: {candidate.salary_expectation or 'Not specified'}\n"
        f"Relocation Preference: {candidate.relocation_preference or 'Not specified'}\n"
        f"Open to Work: {'Yes' if candidate.open_to_work else 'No'}\n"
        f"Profile Completeness: {candidate.profile_completeness:.0f}%\n"
        f"All Scores Summary: Semantic={all_scores.get('semantic_score', 0):.1f}, "
        f"Skill={all_scores.get('skill_score', 0):.1f}, "
        f"Experience={all_scores.get('experience_score', 0):.1f}, "
        f"Recruitability={all_scores.get('recruitability_score', 0):.1f}\n\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "recruiter_agent_score": <0-100>,\n'
        '  "recommendation": "<Strong Fit|Moderate Fit|Weak Fit>",\n'
        '  "salary_fit": {\n'
        '    "alignment": "<aligned|above_range|below_range|unknown>",\n'
        '    "notes": "<brief salary fit commentary>"\n'
        '  },\n'
        '  "time_to_hire_estimate": "<e.g. 2-3 weeks>",\n'
        '  "recruiter_summary": "<recruiter-quality 3-4 sentence summary>",\n'
        '  "why_selected": "<compelling reason to select this candidate>",\n'
        '  "why_rejected": "<honest reason if not selected>"\n'
        "}"
    )


def _build_committee_prompt(job_struct: dict, candidate: Any, agent_results: dict) -> str:
    return (
        "You are the Hiring Committee Consensus AI for HireGenius AI.\n"
        "Your role: Synthesize all agent evaluations into a final hiring decision.\n\n"
        f"Job Role: {job_struct.get('title', 'Unknown')}\n"
        f"Candidate Name: {candidate.full_name}\n\n"
        "Agent Evaluation Summary:\n"
        f"- Skill Agent Score: {agent_results.get('skill_agent_score', 0):.1f}/100\n"
        f"- Experience Agent Score: {agent_results.get('experience_agent_score', 0):.1f}/100\n"
        f"- Behavior Agent Score: {agent_results.get('behavior_agent_score', 0):.1f}/100\n"
        f"- Recruiter Agent Score: {agent_results.get('recruiter_agent_score', 0):.1f}/100\n"
        f"- Recommendation: {agent_results.get('recommendation', 'Moderate Fit')}\n"
        f"- Career Trajectory: {agent_results.get('career_trajectory', 'unknown')}\n"
        f"- Key Strengths: {', '.join((agent_results.get('skill_strengths', []) + agent_results.get('experience_strengths', []))[:4])}\n"
        f"- Key Gaps: {', '.join((agent_results.get('skill_gaps', []) + agent_results.get('experience_gaps', []))[:3])}\n"
        f"- Risk Factors: {', '.join(agent_results.get('risk_factors', []))}\n\n"
        "Respond ONLY with valid JSON:\n"
        "{\n"
        '  "committee_score": <0-100>,\n'
        '  "confidence_score": <0-100>,\n'
        '  "final_recommendation": "<Strong Fit|Moderate Fit|Weak Fit>",\n'
        '  "risk_level": "<low|medium|high>",\n'
        '  "potential_score": <0-100>,\n'
        '  "hiring_committee_summary": "<4-5 sentence executive-quality summary>",\n'
        '  "interview_questions": [\n'
        '    "<question 1 targeting a skill gap>",\n'
        '    "<question 2 targeting experience>",\n'
        '    "<question 3 targeting behavior>",\n'
        '    "<question 4 targeting growth potential>",\n'
        '    "<question 5 deep technical/role-specific>"\n'
        '  ],\n'
        '  "role_fit_analysis": "<comprehensive 3-4 sentence role alignment analysis>",\n'
        '  "growth_potential_summary": "<1-2 sentence growth potential statement>"\n'
        "}"
    )


# ---------------------------------------------------------------------------
# Gemini call helper
# ---------------------------------------------------------------------------

def _call_gemini(prompt: str, fallback_fn, *fallback_args) -> dict:
    """Call Gemini API with proper error handling and fallback."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")

    if api_key:
        try:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"temperature": 0.2, "max_output_tokens": 2048},
            )
            response = model.generate_content(prompt)
            text = response.text if hasattr(response, "text") else str(response)
            # extract JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass

    return fallback_fn(*fallback_args)


# ---------------------------------------------------------------------------
# Fallback implementations for each agent
# ---------------------------------------------------------------------------

def _skill_fallback(job_struct: dict, candidate: Any, skill_score: float, skill_details: dict) -> dict:
    matched = skill_details.get("matched", [])
    missing = skill_details.get("missing", [])
    learning = []
    for skill in missing[:3]:
        learning.append(f"Complete a certified course in {skill.title()}")
    return {
        "skill_agent_score": float(round(skill_score, 1)),
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_strengths": [f"Proficient in {s}" for s in matched[:3]],
        "skill_gaps": [f"Missing {s}" for s in missing[:2]],
        "learning_path": learning or ["Complete role-relevant technical certifications"],
        "time_to_readiness": "3-6 months" if missing else "Immediately ready",
        "skill_assessment": (
            f"Candidate demonstrates {skill_score:.0f}% skill alignment with {len(matched)} of {len(matched)+len(missing)} "
            f"required skills matched. {'Strong technical profile.' if skill_score >= 70 else 'Some upskilling needed.'}"
        ),
    }


def _experience_fallback(job_struct: dict, candidate: Any, exp_score: float, exp_details: dict) -> dict:
    trajectory = "ascending" if exp_details.get("growth") else "lateral"
    learning_velocity = "fast" if exp_details.get("growth") and exp_details.get("leadership") else "moderate"
    try:
        req_years = float(job_struct.get("experience_years", 0) or 0)
    except Exception:
        req_years = 0.0
    return {
        "experience_agent_score": float(round(exp_score, 1)),
        "career_trajectory": trajectory,
        "learning_velocity": learning_velocity,
        "leadership_potential": bool(exp_details.get("leadership", False)),
        "experience_strengths": ["Relevant industry experience", "Career progression evident"] if exp_score >= 60 else ["Entry-level experience"],
        "experience_gaps": ["Limited years relative to requirement"] if candidate.years_experience < req_years else [],
        "future_roles": ["Senior " + (job_struct.get("title", "Professional")), "Team Lead", "Principal/Staff role"],
        "growth_forecast": {
            "year_1": "Fully ramped, driving independent deliverables",
            "year_2": "Mentoring juniors, leading small projects",
            "year_3": "Senior/Lead level, strategic contributions",
        },
        "experience_assessment": (
            f"With {candidate.years_experience:.0f} years of experience, candidate shows {trajectory} career trajectory. "
            f"Experience score of {exp_score:.0f}/100 indicates "
            f"{'strong alignment' if exp_score >= 70 else 'moderate fit'} with role requirements."
        ),
    }


def _behavior_fallback(job_struct: dict, candidate: Any, rec_score: float, rec_details: dict) -> dict:
    engagement = "high" if rec_score >= 70 else ("medium" if rec_score >= 45 else "low")
    risks = []
    if candidate.interview_completion_rate < 50:
        risks.append("Low interview completion rate may indicate lack of follow-through")
    if not candidate.open_to_work:
        risks.append("Not actively seeking — may require competitive offer")
    if candidate.profile_completeness < 60:
        risks.append("Incomplete profile — engagement level uncertain")
    return {
        "behavior_agent_score": float(round(rec_score, 1)),
        "culture_fit_score": float(round(min(100, rec_score * 1.1), 1)),
        "behavioral_strengths": ["Professional engagement signals", "Consistent recruiter responsiveness"] if rec_score >= 60 else ["Available for opportunities"],
        "behavioral_concerns": risks[:2],
        "engagement_level": engagement,
        "risk_factors": risks,
        "behavior_assessment": (
            f"Behavioral signals indicate {engagement} engagement level. "
            f"Recruiter response rate of {candidate.recruiter_response_rate:.0f}% and "
            f"interview completion of {candidate.interview_completion_rate:.0f}% suggest "
            f"{'reliable follow-through' if rec_score >= 60 else 'potential engagement risks'}."
        ),
    }


def _recruiter_fallback(job_struct: dict, candidate: Any, all_scores: dict) -> dict:
    avg_score = sum(all_scores.values()) / max(1, len(all_scores))
    rec = "Strong Fit" if avg_score >= 75 else ("Moderate Fit" if avg_score >= 45 else "Weak Fit")
    salary = candidate.salary_expectation or "not disclosed"
    return {
        "recruiter_agent_score": float(round(avg_score, 1)),
        "recommendation": rec,
        "salary_fit": {
            "alignment": "unknown" if not candidate.salary_expectation else "aligned",
            "notes": f"Candidate expectation: {salary}. Verify against budget range.",
        },
        "time_to_hire_estimate": "2-3 weeks",
        "recruiter_summary": (
            f"{candidate.full_name} presents as a {rec.lower()} for this role. "
            f"Key strengths: skill alignment ({all_scores.get('skill_score', 0):.0f}/100) and "
            f"experience ({all_scores.get('experience_score', 0):.0f}/100). "
            f"Recommend {'proceeding to interview' if avg_score >= 55 else 'reviewing alternatives first'}."
        ),
        "why_selected": (
            f"Strong combination of technical skills ({all_scores.get('skill_score', 0):.0f}/100) "
            f"and relevant experience ({all_scores.get('experience_score', 0):.0f}/100) makes this candidate competitive."
        ),
        "why_rejected": (
            "Skill gaps in required areas and/or insufficient experience relative to role requirements."
            if avg_score < 55 else "No significant rejection concerns at this stage."
        ),
    }


def _committee_fallback(job_struct: dict, candidate: Any, agent_results: dict) -> dict:
    scores = [
        agent_results.get("skill_agent_score", 0),
        agent_results.get("experience_agent_score", 0),
        agent_results.get("behavior_agent_score", 0),
        agent_results.get("recruiter_agent_score", 0),
    ]
    committee_score = sum(scores) / max(1, len(scores))
    rec = agent_results.get("recommendation", "Moderate Fit")
    risks = agent_results.get("risk_factors", [])
    risk_level = "low" if not risks else ("medium" if len(risks) <= 1 else "high")
    potential = min(100, committee_score * 1.15)
    missing = agent_results.get("missing_skills", [])
    interview_qs = [
        f"Walk me through your experience with {missing[0] if missing else 'the core technical requirements'}.",
        "Describe a situation where you had to learn a new technology quickly. What was your approach?",
        "How do you handle competing priorities in a fast-paced environment?",
        f"What does career growth look like for you in the next 2-3 years at {job_struct.get('title', 'this role')}?",
        "Tell me about a complex technical challenge you solved and the impact it had.",
    ]
    return {
        "committee_score": float(round(committee_score, 1)),
        "confidence_score": float(round(min(100, committee_score + 10), 1)),
        "final_recommendation": rec,
        "risk_level": risk_level,
        "potential_score": float(round(potential, 1)),
        "hiring_committee_summary": (
            f"The hiring committee evaluates {candidate.full_name} as a {rec.lower()} with "
            f"a consensus score of {committee_score:.0f}/100. "
            f"Skill alignment and experience profile support {'advancement to next interview stage' if committee_score >= 60 else 'further evaluation'}. "
            f"Risk level is {risk_level}. "
            f"{'Candidate shows strong growth potential and is recommended for fast-tracking.' if potential >= 75 else 'Standard evaluation process recommended.'}"
        ),
        "interview_questions": interview_qs,
        "role_fit_analysis": (
            f"Role fit analysis for {candidate.full_name}: Technical competencies align at {agent_results.get('skill_agent_score', 0):.0f}/100, "
            f"experience trajectory scores {agent_results.get('experience_agent_score', 0):.0f}/100, "
            f"and behavioral readiness at {agent_results.get('behavior_agent_score', 0):.0f}/100. "
            f"Overall alignment suggests {'excellent' if committee_score >= 75 else 'moderate'} fit for the {job_struct.get('title', 'role')}."
        ),
        "growth_potential_summary": (
            f"{'High growth potential' if potential >= 75 else 'Moderate growth potential'} detected based on career trajectory "
            f"and learning velocity indicators."
        ),
    }


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_multi_agent_evaluation(
    job_struct: dict,
    candidate: Any,
    scores: dict,
    skill_details: dict,
    exp_details: dict,
    rec_details: dict,
) -> dict:
    """
    Run all 5 agents and return a merged evaluation dict.

    Agent 1: Skill Evaluator
    Agent 2: Experience Evaluator
    Agent 3: Behavior Evaluator
    Agent 4: Recruiter Evaluator
    Agent 5: Hiring Committee Consensus
    """
    skill_score = scores.get("skill_score", 0)
    exp_score = scores.get("experience_score", 0)
    rec_score = scores.get("recruitability_score", 0)

    # Agent 1: Skills
    skill_result = _call_gemini(
        _build_skill_agent_prompt(job_struct, candidate, skill_score, skill_details),
        _skill_fallback,
        job_struct, candidate, skill_score, skill_details,
    )

    # Agent 2: Experience
    exp_result = _call_gemini(
        _build_experience_agent_prompt(job_struct, candidate, exp_score, exp_details),
        _experience_fallback,
        job_struct, candidate, exp_score, exp_details,
    )

    # Agent 3: Behavior
    behavior_result = _call_gemini(
        _build_behavior_agent_prompt(job_struct, candidate, rec_score, rec_details),
        _behavior_fallback,
        job_struct, candidate, rec_score, rec_details,
    )

    # Agent 4: Recruiter
    recruiter_result = _call_gemini(
        _build_recruiter_agent_prompt(job_struct, candidate, scores),
        _recruiter_fallback,
        job_struct, candidate, scores,
    )

    # Merge results for committee
    merged = {}
    for result in [skill_result, exp_result, behavior_result, recruiter_result]:
        merged.update(result)

    # Agent 5: Committee consensus
    committee_result = _call_gemini(
        _build_committee_prompt(job_struct, candidate, merged),
        _committee_fallback,
        job_struct, candidate, merged,
    )

    merged.update(committee_result)
    return merged
