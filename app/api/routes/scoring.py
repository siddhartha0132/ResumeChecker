"""
Scoring routes — single, batch, compare, RAG-enhanced
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import uuid

from app.services.pdf_service import get_pdf_parser, HybridPDFParser
from app.core.extractors.hybrid_extractor import get_skill_extractor, HybridSkillExtractor
from app.core.scorers.ensemble_scorer import get_ensemble_scorer, EnsembleScorer
from app.core.scorers.role_scorer import ROLE_WEIGHTS, get_role_key_skills
from app.core.matchers.jd_matcher import get_jd_matcher, JDMatcher
from app.rag.retriever import retrieve_ev_context, retrieve_similar_candidates
from app.rag.vector_store import get_vector_store
from app.feedback.generator import generate_feedback
from app.db.database import save_candidate
from app.utils.helpers import extract_name, extract_email, extract_phone, extract_experience_years
from app.utils.validators import validate_file_size, validate_job_description

router = APIRouter(prefix="/api/scoring", tags=["Scoring"])


def _get_parser()    -> HybridPDFParser:    return get_pdf_parser()
def _get_extractor() -> HybridSkillExtractor: return get_skill_extractor()
def _get_scorer()    -> EnsembleScorer:     return get_ensemble_scorer()
def _get_matcher()   -> JDMatcher:          return get_jd_matcher()


# ── Single resume ─────────────────────────────────────────────────────────────

@router.post("/score", summary="Score a single resume against a job description")
async def score_resume(
    file: UploadFile = File(..., description="PDF, TXT, or DOCX resume"),
    job_description: str = Form(..., description="Full job description text"),
    role_type: str = Form("general", description="battery_engineer | powertrain_engineer | charging_infrastructure | adas_autonomy | embedded_software | testing_validation | general"),
    scoring_method: str = Form("ensemble", description="ensemble | gemini | tfidf | rule_based"),
    use_rag: bool = Form(True, description="Retrieve EV guidelines from knowledge base"),
    save_to_db: bool = Form(True, description="Persist candidate to database"),
    parser:    HybridPDFParser    = Depends(_get_parser),
    extractor: HybridSkillExtractor = Depends(_get_extractor),
    scorer:    EnsembleScorer     = Depends(_get_scorer),
    matcher:   JDMatcher          = Depends(_get_matcher),
):
    """
    **Score a resume against a job description** with full RAG enhancement.

    Pipeline:
    1. Parse PDF (pdfplumber → PyPDF2 → pdfminer3 → OCR)
    2. Extract skills (Regex 30% + spaCy 50% + Vocabulary 20%)
    3. Retrieve EV guidelines from ChromaDB (RAG context)
    4. Score with Gemini AI + TF-IDF + Rules (role-weighted ensemble)
    5. Generate actionable feedback
    6. Store candidate in database + vector store
    """
    jd_ok, jd_err = validate_job_description(job_description)
    if not jd_ok:
        raise HTTPException(status_code=400, detail=jd_err)

    file_bytes = await file.read()
    size_ok, size_err = validate_file_size(file_bytes)
    if not size_ok:
        raise HTTPException(status_code=400, detail=size_err)

    # 1. Parse
    parse_result = parser.parse(file_bytes)
    if not parse_result["success"]:
        raise HTTPException(status_code=400, detail=parse_result["error"])
    resume_text = parse_result["text"]

    # 2. Extract skills
    resume_skills = extractor.extract(resume_text)["skills"]
    jd_skills     = extractor.extract(job_description)["skills"]

    # 3. RAG context
    rag_context = ""
    if use_rag:
        rag_context = retrieve_ev_context(job_description, role_type, n=3)

    # 4. Score
    force = scoring_method if scoring_method != "ensemble" else None
    score_result = await scorer.score(
        resume_text=resume_text,
        jd_text=job_description,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        force_method=force,
        role_type=role_type,
        rag_context=rag_context,
    )

    # 5. JD match details
    exp_years = extract_experience_years(resume_text)
    match_result = matcher.match(
        resume_text=resume_text,
        jd_text=job_description,
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        experience_years=exp_years,
    )

    # 6. Feedback
    parsed_info = {
        "name":             extract_name(resume_text, file.filename or ""),
        "email":            extract_email(resume_text),
        "phone":            extract_phone(resume_text),
        "experience_years": exp_years,
        "skills":           resume_skills,
    }
    feedback = generate_feedback(score_result, parsed_info, role_type, rag_context)

    # 7. Persist
    candidate_id = str(uuid.uuid4())
    if save_to_db:
        db_id = await save_candidate(
            name=parsed_info["name"],
            email=parsed_info["email"],
            phone=parsed_info["phone"],
            filename=file.filename or "unknown",
            raw_text=resume_text,
            skills_extracted=resume_skills,
            skills_matched=score_result["skills_matched"],
            skills_missing=score_result["skills_missing"],
            ats_score=score_result["ats_score"],
            experience_years=exp_years,
            hire_signal=score_result["hire_signal"],
            summary=score_result["summary"],
            parsing_method=parse_result["method"],
            scoring_method=score_result["method"],
        )
        candidate_id = str(db_id)

        # Add to vector store for future similarity search
        store = get_vector_store()
        store.add_resume(
            resume_id=candidate_id,
            text=resume_text,
            metadata={
                "name":        parsed_info["name"],
                "role":        role_type,
                "ats_score":   score_result["ats_score"],
                "hire_signal": score_result["hire_signal"],
                "skills":      ", ".join(resume_skills[:10]),
            },
        )
        if score_result["hire_signal"] == "strong":
            store.add_to_talent_pool(
                candidate_id=candidate_id,
                text=resume_text,
                metadata={
                    "name":      parsed_info["name"],
                    "role":      role_type,
                    "ats_score": score_result["ats_score"],
                },
            )

    return {
        "candidate_id": candidate_id,
        "filename":     file.filename,
        "candidate":    parsed_info,
        "parsing": {
            "method":      parse_result["method"],
            "is_ocr":      parse_result["is_ocr"],
            "text_length": len(resume_text),
        },
        "skills": {
            "resume_skills":      resume_skills,
            "resume_skill_count": len(resume_skills),
            "jd_skills":          jd_skills,
            "jd_skill_count":     len(jd_skills),
        },
        "scoring": {
            "ats_score":        score_result["ats_score"],
            "score_normalized": round(score_result["score"], 4),
            "hire_signal":      score_result["hire_signal"],
            "summary":          score_result["summary"],
            "method":           score_result["method"],
            "methods_used":     score_result.get("methods_used", []),
            "individual_scores": score_result.get("individual_scores", {}),
            "role_type":        role_type,
            "rag_used":         score_result.get("rag_used", False),
        },
        "matching": {
            "skills_matched":      score_result["skills_matched"],
            "skills_missing":      score_result["skills_missing"],
            "match_percentage":    round(
                len(score_result["skills_matched"]) / max(len(jd_skills), 1) * 100, 1
            ),
            "tfidf_similarity":    match_result["tfidf_score"],
            "weighted_skill_score": match_result["skill_score"],
        },
        "feedback":   feedback,
        "timestamp":  datetime.now().isoformat(),
    }


# ── Batch scoring ─────────────────────────────────────────────────────────────

@router.post("/batch", summary="Score up to 100 resumes and return ranked candidates")
async def batch_score(
    files: List[UploadFile] = File(..., description="Up to 100 resume files"),
    job_description: str = Form(..., description="Full job description text"),
    role_type: str = Form("general", description="EV role type"),
    scoring_method: str = Form("tfidf", description="ensemble | gemini | tfidf | rule_based (tfidf recommended for batch)"),
    use_rag: bool = Form(True, description="Use RAG context"),
    save_to_db: bool = Form(True, description="Persist all candidates to database"),
    parser:    HybridPDFParser    = Depends(_get_parser),
    extractor: HybridSkillExtractor = Depends(_get_extractor),
    scorer:    EnsembleScorer     = Depends(_get_scorer),
):
    """
    **Score up to 100 resumes** in one request and return them ranked by ATS score.

    Tip: Use `scoring_method=tfidf` for batch to avoid Gemini rate limits.
    Use `scoring_method=ensemble` for smaller batches where Gemini quality matters.
    """
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 resumes per batch")

    jd_ok, jd_err = validate_job_description(job_description)
    if not jd_ok:
        raise HTTPException(status_code=400, detail=jd_err)

    jd_skills   = extractor.extract(job_description)["skills"]
    rag_context = retrieve_ev_context(job_description, role_type, n=2) if use_rag else ""
    force       = scoring_method if scoring_method != "ensemble" else None

    candidates, failed = [], []

    for file in files:
        try:
            file_bytes = await file.read()
            size_ok, size_err = validate_file_size(file_bytes)
            if not size_ok:
                failed.append({"filename": file.filename, "error": size_err})
                continue

            parse_result = parser.parse(file_bytes)
            if not parse_result["success"]:
                failed.append({"filename": file.filename, "error": parse_result["error"]})
                continue

            resume_text   = parse_result["text"]
            resume_skills = extractor.extract(resume_text)["skills"]
            exp_years     = extract_experience_years(resume_text)

            score_result = await scorer.score(
                resume_text=resume_text,
                jd_text=job_description,
                resume_skills=resume_skills,
                jd_skills=jd_skills,
                force_method=force,
                role_type=role_type,
                rag_context=rag_context,
            )

            db_id = None
            if save_to_db:
                db_id = await save_candidate(
                    name=extract_name(resume_text, file.filename or ""),
                    email=extract_email(resume_text),
                    phone=extract_phone(resume_text),
                    filename=file.filename or "unknown",
                    raw_text=resume_text,
                    skills_extracted=resume_skills,
                    skills_matched=score_result["skills_matched"],
                    skills_missing=score_result["skills_missing"],
                    ats_score=score_result["ats_score"],
                    experience_years=exp_years,
                    hire_signal=score_result["hire_signal"],
                    summary=score_result["summary"],
                    parsing_method=parse_result["method"],
                    scoring_method=score_result["method"],
                )

            candidates.append({
                "db_id":           db_id,
                "filename":        file.filename,
                "name":            extract_name(resume_text, file.filename or ""),
                "email":           extract_email(resume_text),
                "experience_years": exp_years,
                "ats_score":       score_result["ats_score"],
                "hire_signal":     score_result["hire_signal"],
                "summary":         score_result["summary"],
                "skills_matched":  score_result["skills_matched"],
                "skills_missing":  score_result["skills_missing"],
                "match_percentage": round(
                    len(score_result["skills_matched"]) / max(len(jd_skills), 1) * 100, 1
                ),
                "parsing_method":  parse_result["method"],
                "is_ocr":          parse_result["is_ocr"],
                "rank":            0,
            })

        except Exception as exc:
            failed.append({"filename": file.filename, "error": str(exc)})

    candidates.sort(key=lambda c: c["ats_score"], reverse=True)
    for rank, c in enumerate(candidates, start=1):
        c["rank"] = rank

    return {
        "summary": {
            "total_submitted":    len(files),
            "successfully_scored": len(candidates),
            "failed":             len(failed),
            "top_candidate":      candidates[0]["name"] if candidates else None,
            "top_score":          candidates[0]["ats_score"] if candidates else 0,
            "average_score":      round(
                sum(c["ats_score"] for c in candidates) / max(len(candidates), 1), 1
            ),
            "shortlisted":        sum(1 for c in candidates if c["hire_signal"] == "strong"),
        },
        "jd_skills":      jd_skills,
        "role_type":      role_type,
        "rag_used":       bool(rag_context),
        "candidates":     candidates,
        "failed_files":   failed,
        "scoring_method": scoring_method,
        "timestamp":      datetime.now().isoformat(),
    }


# ── Compare two resumes ───────────────────────────────────────────────────────

@router.post("/compare", summary="Compare two resumes side-by-side against a JD")
async def compare_resumes(
    file_a: UploadFile = File(..., description="First resume"),
    file_b: UploadFile = File(..., description="Second resume"),
    job_description: str = Form(..., description="Job description"),
    role_type: str = Form("general"),
    parser:    HybridPDFParser    = Depends(_get_parser),
    extractor: HybridSkillExtractor = Depends(_get_extractor),
    scorer:    EnsembleScorer     = Depends(_get_scorer),
):
    """
    **Compare two resumes side-by-side** against the same job description.
    Returns scores, skill gaps, unique skills, and a recommendation.
    """
    jd_ok, jd_err = validate_job_description(job_description)
    if not jd_ok:
        raise HTTPException(status_code=400, detail=jd_err)

    jd_skills   = extractor.extract(job_description)["skills"]
    rag_context = retrieve_ev_context(job_description, role_type, n=2)
    results     = []

    for file in [file_a, file_b]:
        file_bytes = await file.read()
        parse_result = parser.parse(file_bytes)
        if not parse_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Could not parse {file.filename}: {parse_result['error']}"
            )
        resume_text   = parse_result["text"]
        resume_skills = extractor.extract(resume_text)["skills"]
        score_result  = await scorer.score(
            resume_text=resume_text,
            jd_text=job_description,
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            role_type=role_type,
            rag_context=rag_context,
        )
        results.append({
            "filename":       file.filename,
            "name":           extract_name(resume_text, file.filename or ""),
            "ats_score":      score_result["ats_score"],
            "hire_signal":    score_result["hire_signal"],
            "summary":        score_result["summary"],
            "skills_matched": score_result["skills_matched"],
            "skills_missing": score_result["skills_missing"],
            "all_skills":     resume_skills,
        })

    winner = results[0] if results[0]["ats_score"] >= results[1]["ats_score"] else results[1]
    loser  = results[1] if winner == results[0] else results[0]

    return {
        "resume_a":   results[0],
        "resume_b":   results[1],
        "recommendation": {
            "winner":           winner["filename"],
            "winner_name":      winner["name"],
            "score_difference": abs(results[0]["ats_score"] - results[1]["ats_score"]),
            "reason":           winner["summary"],
            "unique_to_winner": [
                s for s in winner["skills_matched"]
                if s not in loser["skills_matched"]
            ],
        },
        "jd_skills":  jd_skills,
        "role_type":  role_type,
        "rag_used":   bool(rag_context),
        "timestamp":  datetime.now().isoformat(),
    }


# ── Available roles ───────────────────────────────────────────────────────────

@router.get("/roles", summary="List available EV role types and their key skills")
async def list_roles():
    """Returns all supported EV role types with their key skills and pass thresholds."""
    return {
        "roles": {
            role: {
                "key_skills":    profile.get("key_skills", []),
                "min_pass_score": profile.get("min_pass_score", 60),
            }
            for role, profile in ROLE_WEIGHTS.items()
        },
        "timestamp": datetime.now().isoformat(),
    }
