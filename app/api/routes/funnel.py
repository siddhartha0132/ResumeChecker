"""
Funnel routes — 50k applicant pipeline management
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.pipeline.funnel import get_funnel_pipeline, FunnelPipeline

router = APIRouter(prefix="/api/funnel", tags=["Funnel Pipeline"])


# ── Request / Response models ─────────────────────────────────────────────────

class CandidateInput(BaseModel):
    id: str
    name: str = "Unknown"
    email: str = ""
    ats_score: int = Field(..., ge=0, le=100, description="ATS score 0-100")
    skills_matched: List[str] = []
    essay_score: float = Field(0.0, ge=0, le=100)
    has_ev_project: bool = False
    has_portfolio: bool = False
    availability_match: bool = False
    experience_years: float = 0.0


class FunnelRunRequest(BaseModel):
    candidates: List[CandidateInput]


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/run", summary="Run the full 3-stage funnel on a list of candidates")
async def run_full_funnel(request: FunnelRunRequest):
    """
    **Run the complete 3-stage VisionAstraa hiring funnel.**

    - **Stage 1 (ATS):** Filters by ATS score threshold (≥60 pass, <40 reject)
    - **Stage 2 (Form):** Weighted scoring — ATS 30%, Essay 25%, Project 20%, Portfolio 15%, Availability 10%
    - **Stage 3 (Cohort):** Selects top 500 with segment distribution (Dev 50%, Data 30%, Design 20%)

    Designed to handle 50k+ applicants.
    """
    if not request.candidates:
        raise HTTPException(status_code=400, detail="No candidates provided")

    pipeline = get_funnel_pipeline()
    candidates_dicts = [c.model_dump() for c in request.candidates]
    result = pipeline.run_full_pipeline(candidates_dicts)

    return {
        "funnel_result": result,
        "stats": {
            "total_applicants": result["total_applicants"],
            "stage1_passed": result["stage1"]["passed"],
            "stage1_rejected": result["stage1"]["rejected"],
            "stage1_waitlisted": result["stage1"]["waitlisted"],
            "stage2_promoted": result["stage2"]["promoted"],
            "stage3_selected": result["stage3"]["selected"],
            "segment_distribution": result["stage3"]["segments"],
            "selection_rate": round(
                result["stage3"]["selected"] / result["total_applicants"] * 100, 2
            ) if result["total_applicants"] > 0 else 0,
        },
        "final_cohort_preview": result["final_cohort"][:10],  # First 10
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/stage1", summary="Run Stage 1 — ATS screening only")
async def run_stage1(request: FunnelRunRequest):
    """
    **Stage 1: ATS Screening**

    - Score ≥ 60 → passes to Stage 2
    - Score < 40 → rejected
    - Score 40-59 → waitlisted
    """
    pipeline = get_funnel_pipeline()
    candidates_dicts = [c.model_dump() for c in request.candidates]
    result = pipeline.stage1_ats_screening(candidates_dicts)

    return {
        "stage": 1,
        "total_processed": result["total_processed"],
        "passed": result["passed_to_stage2"],
        "rejected": result["rejected"],
        "waitlisted": result["waitlisted"],
        "passed_candidates": result["passed_candidates"],
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/stage2", summary="Run Stage 2 — Form evaluation on Stage 1 passers")
async def run_stage2(request: FunnelRunRequest):
    """
    **Stage 2: Form Evaluation**

    Weighted scoring:
    - ATS score: 30%
    - Essay score: 25%
    - EV project: 20%
    - Portfolio: 15%
    - Availability: 10%
    """
    pipeline = get_funnel_pipeline()
    candidates_dicts = [c.model_dump() for c in request.candidates]
    result = pipeline.stage2_form_evaluation(candidates_dicts)

    return {
        "stage": 2,
        "stage1_count": result["stage1_count"],
        "promoted_to_stage3": result["promoted_to_stage3"],
        "promoted_candidates": result["promoted_candidates"],
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/stage3", summary="Run Stage 3 — Cohort selection from Stage 2 passers")
async def run_stage3(request: FunnelRunRequest):
    """
    **Stage 3: Cohort Selection**

    Selects top 500 candidates with segment distribution:
    - Dev track: 50% (250 seats)
    - Data track: 30% (150 seats)
    - Design track: 20% (100 seats)
    """
    pipeline = get_funnel_pipeline()
    candidates_dicts = [c.model_dump() for c in request.candidates]
    result = pipeline.stage3_cohort_selection(candidates_dicts)

    return {
        "stage": 3,
        "stage2_count": result["stage2_count"],
        "selected_count": result["selected_count"],
        "segment_distribution": result["segment_distribution"],
        "selected_candidates": result["selected_candidates"],
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/config", summary="Get current funnel configuration")
async def get_funnel_config():
    """Returns the current funnel thresholds and segment configuration."""
    from app.config.settings import settings
    return {
        "stage1": {
            "min_score_to_pass": settings.STAGE1_MIN_SCORE,
            "max_score_to_reject": settings.STAGE1_REJECT_SCORE,
        },
        "stage2": {
            "weights": {
                "ats_score": "30%",
                "essay_score": "25%",
                "ev_project": "20%",
                "portfolio": "15%",
                "availability": "10%",
            }
        },
        "stage3": {
            "cohort_size": settings.COHORT_SIZE,
            "segments": settings.COHORT_SEGMENTS,
        },
        "timestamp": datetime.now().isoformat(),
    }
