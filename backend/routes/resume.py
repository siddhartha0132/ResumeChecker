from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.parser import (
    extract_text_from_pdf,
    extract_text_from_string,
    extract_candidate_info,
    extract_skills_nlp,
    extract_experience_years,
)
from services.scorer import score_resume
from db.database import save_candidate, get_all_candidates, get_jd, reset_candidates_table
import json

router = APIRouter()


@router.post("/upload")
async def upload_and_score(
    file: UploadFile = File(None),
    resume_text: str = Form(None),
    jd_id: int = Form(1),
):
    # ── 1. Extract raw text ───────────────────────────────────────────────
    if file is not None:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Only PDF files accepted (or use resume_text for plain text)")
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 10MB)")
        raw_text = extract_text_from_pdf(content)
    elif resume_text:
        raw_text = extract_text_from_string(resume_text)
    else:
        raise HTTPException(400, "Provide either a PDF file or resume_text")

    if not raw_text:
        raise HTTPException(422, "Could not extract text from input")

    # ── 2. NLP extraction ────────────────────────────────────────────────
    info = extract_candidate_info(raw_text)
    nlp_skills = extract_skills_nlp(raw_text)
    exp_years = extract_experience_years(raw_text)

    # ── 3. Load JD ───────────────────────────────────────────────────────
    jd = await get_jd(jd_id)
    if not jd:
        raise HTTPException(404, "Job description not found")
    jd_required = json.loads(jd.get("required_skills", "[]"))

    # ── 4. Gemini scoring ────────────────────────────────────────────────
    result = await score_resume(raw_text, jd["description"], nlp_skills)

    skills_matched = result.get("skills_matched") or nlp_skills
    skills_missing = result.get("skills_missing") or [
        s for s in jd_required if s not in skills_matched
    ]

    # ── 5. Persist ───────────────────────────────────────────────────────
    candidate_id = await save_candidate(
        name=info["name"],
        email=info["email"],
        raw_text=raw_text,
        skills_extracted=json.dumps(nlp_skills),
        skills_matched=json.dumps(skills_matched),
        skills_missing=json.dumps(skills_missing),
        ats_score=result["ats_score"],
        experience_years=result.get("experience_years", exp_years),
        hire_signal=result.get("hire_signal", "moderate"),
        summary=result.get("summary", ""),
    )

    return {
        "candidate_id": candidate_id,
        "name": info["name"],
        "email": info["email"],
        "college": info.get("college"),
        "ats_score": result["ats_score"],
        "nlp_skills_extracted": nlp_skills,
        "skills_matched": skills_matched,
        "skills_missing": skills_missing,
        "experience_years": result.get("experience_years", exp_years),
        "breakdown": {
            "skills": result.get("skills_score", 0),
            "experience": result.get("experience_score", 0),
            "education": result.get("education_score", 0),
            "format": result.get("format_score", 0),
        },
        "summary": result.get("summary", ""),
        "hire_signal": result.get("hire_signal", "moderate"),
    }


@router.get("/results")
async def get_results():
    candidates = await get_all_candidates()
    return sorted(candidates, key=lambda x: x["ats_score"], reverse=True)


@router.delete("/reset")
async def reset_candidates():
    await reset_candidates_table()
    return {"status": "cleared"}
