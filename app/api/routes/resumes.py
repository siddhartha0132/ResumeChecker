"""
Resume routes — upload, parse, extract skills
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import Optional
from datetime import datetime

from app.services.pdf_service import get_pdf_parser, HybridPDFParser
from app.core.extractors.hybrid_extractor import get_skill_extractor, HybridSkillExtractor
from app.utils.helpers import extract_email, extract_phone, extract_name, extract_experience_years
from app.utils.validators import validate_file_size

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])


def _get_parser() -> HybridPDFParser:
    return get_pdf_parser()


def _get_extractor() -> HybridSkillExtractor:
    return get_skill_extractor()


@router.post("/parse", summary="Parse a resume PDF and extract raw text + skills")
async def parse_resume(
    file: UploadFile = File(..., description="PDF, TXT, or DOCX resume file"),
    extract_skills: bool = Form(True, description="Whether to run skill extraction"),
    extraction_method: str = Form("ensemble", description="ensemble | regex | spacy | vocabulary"),
    parser: HybridPDFParser = Depends(_get_parser),
    extractor: HybridSkillExtractor = Depends(_get_extractor),
):
    """
    **Parse a resume file** and optionally extract skills.

    - Tries pdfplumber → PyPDF2 → pdfminer3 → OCR in order
    - Returns extracted text, detected skills, and candidate profile fields
    """
    file_bytes = await file.read()

    # Size check
    ok, err = validate_file_size(file_bytes)
    if not ok:
        raise HTTPException(status_code=400, detail=err)

    # Parse
    parse_result = parser.parse(file_bytes)
    if not parse_result["success"]:
        raise HTTPException(status_code=400, detail=parse_result["error"])

    text = parse_result["text"]

    response = {
        "filename": file.filename,
        "parsing_method": parse_result["method"],
        "is_ocr": parse_result["is_ocr"],
        "text_preview": text[:500],
        "full_text_length": len(text),
        "metadata": parser.extract_metadata(file_bytes),
        "candidate": {
            "name": extract_name(text, file.filename or ""),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "experience_years": extract_experience_years(text),
        },
        "timestamp": datetime.now().isoformat(),
    }

    if extract_skills:
        skill_result = extractor.extract(text, method=extraction_method)
        response["skills"] = skill_result["skills"]
        response["skill_count"] = len(skill_result["skills"])
        response["skill_confidence"] = skill_result["confidence"]
        response["extraction_method"] = skill_result["method"]
        if "method_results" in skill_result:
            response["method_breakdown"] = skill_result["method_results"]

    return response


@router.post("/extract-skills", summary="Extract skills from plain text (no file needed)")
async def extract_skills_from_text(
    text: str = Form(..., description="Resume or any text to extract skills from"),
    method: str = Form("ensemble", description="ensemble | regex | spacy | vocabulary"),
    extractor: HybridSkillExtractor = Depends(_get_extractor),
):
    """
    **Extract skills from raw text** using the ensemble extractor.

    Useful for testing or when you already have the text.
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = extractor.extract(text, method=method)

    return {
        "skills": result["skills"],
        "skill_count": len(result["skills"]),
        "confidence": result["confidence"],
        "method": result["method"],
        "method_breakdown": result.get("method_results", {}),
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/vocabulary", summary="Get the full skill vocabulary list")
async def get_vocabulary(
    extractor: HybridSkillExtractor = Depends(_get_extractor),
):
    """
    Returns the complete skill vocabulary used for extraction.
    Combines skills from all three source branches (1000+ skills).
    """
    return {
        "total_skills": len(extractor.vocabulary),
        "skills": extractor.vocabulary,
        "sources": {
            "main_branch": "60 general tech + EV skills",
            "ev_hiring_platform": "50 EV-specific skills",
            "shashwat": "1000+ skills from CSV vocabulary",
        },
        "timestamp": datetime.now().isoformat(),
    }
