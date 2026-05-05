"""
Candidates routes — CRUD on stored candidates, export, stats
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from typing import Optional
from datetime import datetime

from app.db.database import (
    get_all_candidates,
    get_candidate_by_id,
    update_candidate_stage,
    delete_candidate,
    clear_all_candidates,
    get_funnel_stats,
)
from app.services.export_service import export_to_csv, export_to_json

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


@router.get("/", summary="List all stored candidates")
async def list_candidates(
    limit: int = Query(50, ge=1, le=500, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """Returns all candidates stored in the database, ordered by ATS score."""
    candidates = await get_all_candidates(limit=limit, offset=offset)
    return {
        "total": len(candidates),
        "limit": limit,
        "offset": offset,
        "candidates": candidates,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/stats", summary="Funnel statistics")
async def funnel_stats():
    """Returns aggregate stats: total candidates, stage distribution, hire signal breakdown."""
    stats = await get_funnel_stats()
    return {**stats, "timestamp": datetime.now().isoformat()}


@router.get("/export/csv", summary="Export all candidates as CSV")
async def export_csv():
    """Download all stored candidates as a CSV file."""
    candidates = await get_all_candidates(limit=10000)
    csv_content = export_to_csv(candidates)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidates.csv"},
    )


@router.get("/export/json", summary="Export all candidates as JSON")
async def export_json():
    """Download all stored candidates as a JSON file."""
    candidates = await get_all_candidates(limit=10000)
    json_content = export_to_json(candidates)
    return Response(
        content=json_content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=candidates.json"},
    )


@router.get("/{candidate_id}", summary="Get a single candidate by ID")
async def get_candidate(candidate_id: int):
    candidate = await get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    return candidate


@router.patch("/{candidate_id}/stage", summary="Update a candidate's funnel stage")
async def set_stage(candidate_id: int, stage: int = Query(..., ge=-1, le=3)):
    """
    Update the funnel stage for a candidate.
    - `-1` = rejected
    - `0`  = pending / waitlisted
    - `1`  = passed Stage 1 (ATS)
    - `2`  = passed Stage 2 (Form)
    - `3`  = selected (Cohort)
    """
    candidate = await get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    await update_candidate_stage(candidate_id, stage)
    return {"success": True, "candidate_id": candidate_id, "new_stage": stage}


@router.delete("/{candidate_id}", summary="Delete a candidate")
async def remove_candidate(candidate_id: int):
    candidate = await get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    await delete_candidate(candidate_id)
    return {"success": True, "deleted_id": candidate_id}


@router.delete("/", summary="Clear ALL candidates (dev utility)")
async def clear_candidates():
    """⚠️ Deletes every candidate from the database. Use with caution."""
    await clear_all_candidates()
    return {"success": True, "message": "All candidates cleared"}
