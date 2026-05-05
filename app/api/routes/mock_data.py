"""
Mock data routes — generate test resumes and score them
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.services.mock_data_service import generate_mock_candidates
from app.core.extractors.hybrid_extractor import get_skill_extractor
from app.core.scorers.ensemble_scorer import get_ensemble_scorer
from app.db.database import save_candidate
from app.config.constants import DEFAULT_JD, DEFAULT_JD_SKILLS

router = APIRouter(prefix="/api/mock", tags=["Mock Data"])


@router.post("/generate", summary="Generate N mock candidate records")
async def generate_candidates(
    count: int = Query(10, ge=1, le=1000, description="Number of mock candidates to generate"),
):
    """
    **Generate mock candidate records** for testing.
    Uses Faker if installed, otherwise uses static templates.
    Returns candidate profiles with realistic names, skills, and resume text.
    """
    candidates = generate_mock_candidates(count)
    return {
        "generated": len(candidates),
        "candidates": candidates,
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/generate-and-score", summary="Generate, score, and store N mock candidates")
async def generate_and_score(
    count: int = Query(10, ge=1, le=100, description="Number of mock candidates"),
    job_description: str = Query(DEFAULT_JD, description="Job description to score against"),
    scoring_method: str = Query("tfidf", description="ensemble | gemini | tfidf | rule_based"),
):
    """
    **Generate mock candidates, score them, and persist to the database.**

    Useful for populating the database with test data before running the funnel.
    Defaults to TF-IDF scoring to avoid Gemini API costs during testing.
    """
    extractor = get_skill_extractor()
    scorer = get_ensemble_scorer()

    candidates = generate_mock_candidates(count)
    jd_skills = extractor.extract(job_description)["skills"]
    force = scoring_method if scoring_method != "ensemble" else None

    scored = []
    for c in candidates:
        resume_text = c["resume_text"]
        resume_skills = extractor.extract(resume_text)["skills"]

        score_result = await scorer.score(
            resume_text=resume_text,
            jd_text=job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            force_method=force,
        )

        candidate_id = await save_candidate(
            name=c["name"],
            email=c["email"],
            phone=c["phone"],
            filename=f"mock_{c['id']}.txt",
            raw_text=resume_text,
            skills_extracted=resume_skills,
            skills_matched=score_result["skills_matched"],
            skills_missing=score_result["skills_missing"],
            ats_score=score_result["ats_score"],
            experience_years=float(c["experience_years"]),
            hire_signal=score_result["hire_signal"],
            summary=score_result["summary"],
            parsing_method="text",
            scoring_method=score_result["method"],
        )

        scored.append({
            "db_id": candidate_id,
            "name": c["name"],
            "ats_score": score_result["ats_score"],
            "hire_signal": score_result["hire_signal"],
            "skills_matched": score_result["skills_matched"],
            "skills_missing": score_result["skills_missing"],
        })

    scored.sort(key=lambda x: x["ats_score"], reverse=True)
    for rank, s in enumerate(scored, start=1):
        s["rank"] = rank

    return {
        "generated_and_scored": len(scored),
        "scoring_method": scoring_method,
        "top_candidate": scored[0] if scored else None,
        "average_score": round(
            sum(s["ats_score"] for s in scored) / len(scored), 1
        ) if scored else 0,
        "candidates": scored,
        "timestamp": datetime.now().isoformat(),
    }
