import json
from db.database import get_candidates_by_stage, update_candidate_stage

STAGE1_MIN_SCORE = 60
STAGE1_REJECT_SCORE = 40

WEIGHTS = {
    "ats_score": 0.30,
    "essay_score": 0.25,
    "ev_project": 0.20,
    "portfolio": 0.15,
    "availability": 0.10,
}

COHORT_SIZE = 500
COHORT_SEGMENTS = {"dev": 0.50, "data": 0.30, "design": 0.20}

SEGMENT_SKILL_MAP = {
    "data": ["Python", "Machine Learning", "Data Analysis", "Pandas", "NumPy",
             "TensorFlow", "PyTorch", "SQL", "Power BI", "Tableau"],
    "design": ["CAD", "SolidWorks", "AutoCAD", "CATIA", "Fusion 360", "ANSYS", "FEA"],
}


def _infer_segment(skills_json: str) -> str:
    try:
        skills = json.loads(skills_json or "[]")
    except Exception:
        skills = []
    skills_lower = [s.lower() for s in skills]
    for seg, kws in SEGMENT_SKILL_MAP.items():
        if any(k.lower() in skills_lower for k in kws):
            return seg
    return "dev"


async def run_stage1() -> dict:
    all_candidates = await get_candidates_by_stage(0)
    passed, rejected, waitlisted = [], [], []
    for c in all_candidates:
        score = c["ats_score"]
        if score >= STAGE1_MIN_SCORE:
            passed.append(c["id"])
            await update_candidate_stage(c["id"], 1)
        elif score < STAGE1_REJECT_SCORE:
            rejected.append(c["id"])
        else:
            waitlisted.append(c["id"])
    return {
        "total_processed": len(all_candidates),
        "passed_to_stage2": len(passed),
        "rejected": len(rejected),
        "waitlisted": len(waitlisted),
    }


async def run_stage2() -> dict:
    stage1 = await get_candidates_by_stage(1)
    promoted = []
    for c in stage1:
        final_score = (
            c["ats_score"] * WEIGHTS["ats_score"] +
            c["essay_score"] * WEIGHTS["essay_score"] +
            20 * WEIGHTS["ev_project"] +
            (15 if c.get("skills_matched") else 0) * WEIGHTS["portfolio"] +
            (10 if c.get("availability_match") else 0) * WEIGHTS["availability"]
        )
        if final_score >= 25:
            promoted.append(c["id"])
            await update_candidate_stage(c["id"], 2)
    return {"stage1_count": len(stage1), "promoted_to_stage3": len(promoted)}


async def run_stage3_selection() -> list:
    stage2 = await get_candidates_by_stage(2)
    ranked = sorted(stage2, key=lambda x: x["ats_score"], reverse=True)
    selected = []
    segment_counts = {"dev": 0, "data": 0, "design": 0}
    segment_limits = {k: int(COHORT_SIZE * v) for k, v in COHORT_SEGMENTS.items()}
    for c in ranked:
        if len(selected) >= COHORT_SIZE:
            break
        seg = _infer_segment(c.get("skills_matched", "[]"))
        if segment_counts.get(seg, 0) < segment_limits.get(seg, 999):
            c["segment"] = seg
            selected.append(c)
            segment_counts[seg] = segment_counts.get(seg, 0) + 1
            await update_candidate_stage(c["id"], 3)
    return selected
