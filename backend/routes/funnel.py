from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.funnel_engine import run_stage1, run_stage2, run_stage3_selection
from db.database import get_funnel_stats, get_candidates_by_stage
import csv
import io
import json
import asyncio
import random

router = APIRouter()


@router.get("/stats")
async def funnel_stats():
    return await get_funnel_stats()


@router.post("/stage1")
async def funnel_stage1():
    result = await run_stage1()
    return result


@router.post("/stage2")
async def funnel_stage2():
    result = await run_stage2()
    return result


@router.post("/stage3")
async def funnel_stage3():
    selected = await run_stage3_selection()
    return {"selected_count": len(selected), "cohort": selected[:50]}  # first 50 for UI


@router.get("/cohort")
async def get_cohort():
    selected = await get_candidates_by_stage(3)
    return selected


@router.get("/export")
async def export_csv():
    """Download stage-3 selected candidates as CSV."""
    selected = await get_candidates_by_stage(3)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Email", "College", "ATS Score", "Hire Signal", "Skills Matched", "Summary"])
    for c in selected:
        skills = json.loads(c.get("skills_matched") or "[]")
        writer.writerow([
            c["id"], c["name"], c["email"], c.get("college", ""),
            c["ats_score"], c["hire_signal"],
            ", ".join(skills), c.get("summary", "")
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=visionastraa_cohort.csv"}
    )


@router.post("/seed-mock")
async def seed_mock_data(count: int = 50000):
    """
    Generate mock applicant data to simulate 50k funnel.
    Uses deterministic fake data — no Gemini calls.
    """
    from db.database import DB_PATH
    import aiosqlite

    NAMES = ["Aryan", "Priya", "Rahul", "Sneha", "Dev", "Kavya", "Rohan", "Anjali",
             "Amit", "Pooja", "Vikram", "Nisha", "Karan", "Divya", "Aditya"]
    DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "iitd.ac.in", "nit.ac.in"]
    COLLEGES = ["IIT Delhi", "NIT Trichy", "VIT Vellore", "BITS Pilani",
                "SRM University", "Amrita University", "Anna University"]
    SIGNALS = ["strong", "moderate", "weak"]
    ALL_SKILLS = ["Python", "C++", "Arduino", "Raspberry Pi", "CAD", "Battery",
                  "Motor Control", "EV", "MATLAB", "SolidWorks", "Machine Learning"]

    batch_size = 1000
    inserted = 0

    async with aiosqlite.connect(DB_PATH) as db:
        for batch_start in range(0, count, batch_size):
            rows = []
            for i in range(batch_start, min(batch_start + batch_size, count)):
                name = f"{random.choice(NAMES)} {chr(65 + i % 26)}"
                email = f"candidate{i}@{random.choice(DOMAINS)}"
                college = random.choice(COLLEGES)
                ats_score = random.randint(20, 98)
                skills = random.sample(ALL_SKILLS, random.randint(2, 7))
                signal = "strong" if ats_score >= 75 else ("moderate" if ats_score >= 50 else "weak")
                rows.append((
                    name, email, f"Mock resume for {name}",
                    json.dumps(skills), json.dumps(skills[:4]), json.dumps(skills[4:]),
                    ats_score, round(random.uniform(0, 4), 1), signal,
                    f"Mock candidate with ATS score {ats_score}."
                ))
            await db.executemany("""
                INSERT INTO candidates
                  (name, email, raw_text, skills_extracted, skills_matched, skills_missing,
                   ats_score, experience_years, hire_signal, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            await db.commit()
            inserted += len(rows)

    return {"seeded": inserted, "message": f"{inserted} mock candidates created"}
