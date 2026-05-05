"""
AntiGravity God-Level Backend  v3.0
VisionAstraa Resume Parser & Candidate Scorer — RAG Edition

Integrates all three source branches + RAG layer:
  main              → FastAPI, Gemini AI, 50k funnel, aiosqlite
  ev-hiring-platform → TF-IDF ranking, EV skill taxonomy, JD matching
  shashwat          → Security validation, 1000+ vocab, OCR confidence
  RAG layer (new)   → ChromaDB, sentence-transformers, EV knowledge base,
                       role-specific scoring, actionable feedback
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime

from app.config.settings import settings
from app.db.database import init_db

# ── Route modules ─────────────────────────────────────────────────────────────
from app.api.routes.resumes    import router as resumes_router
from app.api.routes.scoring    import router as scoring_router
from app.api.routes.funnel     import router as funnel_router
from app.api.routes.candidates import router as candidates_router
from app.api.routes.mock_data  import router as mock_router
from app.api.routes.admin      import router as admin_router
from app.api.routes.rag        import router as rag_router

# ── Middleware ────────────────────────────────────────────────────────────────
from app.api.middleware.rate_limiter import RateLimiterMiddleware
from app.api.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description="""
## AntiGravity God-Level Backend — RAG Edition

Production-grade resume parser & candidate scorer for **VisionAstraa EV Academy**.

### Architecture
| Layer | Technology | Source |
|-------|-----------|--------|
| Framework | FastAPI (async) | `main` branch |
| PDF Parsing | pdfplumber + PyPDF2 + pdfminer3 + OCR | All branches |
| Skill Extraction | Regex + spaCy + Vocabulary (ensemble) | All branches |
| Scoring | Gemini AI + TF-IDF + Rules (role-weighted) | All branches |
| **RAG** | **ChromaDB + sentence-transformers** | **New** |
| **Knowledge Base** | **EV industry guidelines (7 docs)** | **New** |
| **Role Scoring** | **6 EV role profiles with custom weights** | **New** |
| **Feedback** | **Actionable improvement suggestions** | **New** |
| JD Matching | TF-IDF cosine + weighted skill score | `ev-hiring-platform` |
| 50k Funnel | 3-stage pipeline (ATS → Form → Cohort) | `main` branch |
| Security | File signature + MIME + executable detection | `shashwat` |
| Database | aiosqlite (async SQLite) | `main` branch |

### Quick Start
1. `POST /api/rag/ingest` — load EV knowledge base (once)
2. `POST /api/scoring/score` — score a resume with RAG
3. `GET /api/candidates/` — view stored candidates
4. `GET /docs` — interactive API docs
""",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiter ──────────────────────────────────────────────────────────────
app.add_middleware(RateLimiterMiddleware)

# ── Exception handlers ────────────────────────────────────────────────────────
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ── Startup / shutdown ────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    # 1. Init SQLite
    await init_db()

    # 2. Auto-ingest EV knowledge base (skips if already done)
    try:
        from app.rag.knowledge_base import ingest_knowledge_base
        result = await ingest_knowledge_base(force=False)
        if result["status"] == "success":
            print(f"📚  Knowledge base ingested: {result['total_chunks']} chunks")
        else:
            print(f"📚  Knowledge base: {result['reason']}")
    except Exception as e:
        print(f"⚠️   Knowledge base ingestion skipped: {e}")

    print(f"✅  {settings.APP_NAME} v3.0 started")
    print(f"📖  API docs → http://localhost:8000/docs")


@app.on_event("shutdown")
async def on_shutdown():
    print("👋  Server shutting down")


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(resumes_router)
app.include_router(scoring_router)
app.include_router(funnel_router)
app.include_router(candidates_router)
app.include_router(mock_router)
app.include_router(admin_router)
app.include_router(rag_router)


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], summary="System info")
async def root():
    return {
        "name":    settings.APP_NAME,
        "version": "3.0.0",
        "status":  "operational",
        "docs":    "http://localhost:8000/docs",
        "routes": {
            "resumes":    "/api/resumes",
            "scoring":    "/api/scoring",
            "funnel":     "/api/funnel",
            "candidates": "/api/candidates",
            "mock_data":  "/api/mock",
            "admin":      "/api/admin",
            "rag":        "/api/rag",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health", tags=["Root"], summary="Quick health check")
async def health():
    from app.services.pdf_service import get_pdf_parser
    from app.core.extractors.hybrid_extractor import get_skill_extractor
    from app.core.scorers.ensemble_scorer import get_ensemble_scorer
    from app.rag.vector_store import get_vector_store

    parser    = get_pdf_parser()
    extractor = get_skill_extractor()
    scorer    = get_ensemble_scorer()
    store     = get_vector_store()
    rag_stats = store.stats()

    return {
        "status":            "healthy",
        "version":           "3.0.0",
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "gemini_model":      settings.GEMINI_MODEL,
        "ocr_available":     parser.ocr_available,
        "spacy_loaded":      extractor.nlp is not None,
        "vocabulary_size":   len(extractor.vocabulary),
        "scorer_ready":      scorer.gemini_model is not None,
        "rag": {
            "knowledge_base_ready": rag_stats["knowledge_chunks"] > 0,
            "knowledge_chunks":     rag_stats["knowledge_chunks"],
            "resumes_indexed":      rag_stats["resumes"],
            "talent_pool_size":     rag_stats["talent_pool"],
        },
        "timestamp": datetime.now().isoformat(),
    }


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
