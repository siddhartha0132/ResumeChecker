"""
Admin routes — system info, config, database management
"""

from fastapi import APIRouter
from datetime import datetime

from app.config.settings import settings
from app.services.pdf_service import get_pdf_parser
from app.core.extractors.hybrid_extractor import get_skill_extractor
from app.core.scorers.ensemble_scorer import get_ensemble_scorer

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/health", summary="Full system health check")
async def health_check():
    """
    **Detailed health check** — verifies all subsystems are operational.
    """
    parser = get_pdf_parser()
    extractor = get_skill_extractor()
    scorer = get_ensemble_scorer()

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "subsystems": {
            "gemini_ai": {
                "configured": bool(settings.GEMINI_API_KEY),
                "model": settings.GEMINI_MODEL,
            },
            "pdf_parser": {
                "ocr_available": parser.ocr_available,
                "methods": ["pdfplumber", "PyPDF2", "pdfminer3", "OCR"],
            },
            "skill_extractor": {
                "spacy_loaded": extractor.nlp is not None,
                "vocabulary_size": len(extractor.vocabulary),
                "methods": ["regex", "spacy", "vocabulary"],
            },
            "scorer": {
                "gemini_ready": scorer.gemini_model is not None,
                "methods": ["gemini", "tfidf", "rule_based"],
                "weights": settings.ENSEMBLE_WEIGHTS,
            },
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/config", summary="View current system configuration")
async def get_config():
    """Returns all non-secret configuration values."""
    return {
        "app": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
        },
        "scoring": {
            "ensemble_weights": settings.ENSEMBLE_WEIGHTS,
            "skill_extractor_weights": settings.SKILL_EXTRACTOR_WEIGHTS,
        },
        "funnel": {
            "stage1_min_score": settings.STAGE1_MIN_SCORE,
            "stage1_reject_score": settings.STAGE1_REJECT_SCORE,
            "cohort_size": settings.COHORT_SIZE,
            "cohort_segments": settings.COHORT_SEGMENTS,
        },
        "upload": {
            "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
            "allowed_extensions": list(settings.ALLOWED_EXTENSIONS),
        },
        "ocr": {
            "confidence_threshold": settings.OCR_CONFIDENCE_THRESHOLD,
            "min_text_length": settings.OCR_MIN_TEXT_LENGTH,
            "dpi": settings.OCR_DPI,
        },
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/vocabulary/stats", summary="Skill vocabulary statistics")
async def vocabulary_stats():
    """Returns statistics about the skill vocabulary."""
    extractor = get_skill_extractor()
    vocab = extractor.vocabulary

    # Categorise by length
    short = [s for s in vocab if len(s.split()) == 1]
    medium = [s for s in vocab if len(s.split()) == 2]
    long_ = [s for s in vocab if len(s.split()) >= 3]

    return {
        "total_skills": len(vocab),
        "single_word_skills": len(short),
        "two_word_skills": len(medium),
        "multi_word_skills": len(long_),
        "sample_skills": vocab[:20],
        "timestamp": datetime.now().isoformat(),
    }
