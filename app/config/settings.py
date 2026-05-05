import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Configuration
    APP_NAME: str = "AntiGravity — VisionAstraa God-Level Backend"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./antigravity.db")
    
    # AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_MAX_RETRIES: int = 4
    GEMINI_RETRY_DELAYS: List[int] = [10, 20, 40, 80]  # Exponential backoff
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"pdf", "txt", "docx"}
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    # OCR Configuration
    OCR_CONFIDENCE_THRESHOLD: int = 30
    OCR_MIN_TEXT_LENGTH: int = 50
    OCR_DPI: int = 200
    
    # Scoring Weights
    ENSEMBLE_WEIGHTS: dict = {
        "gemini": 0.60,      # Primary: AI-based contextual scoring
        "tfidf": 0.30,       # Secondary: Statistical similarity
        "rule": 0.10,        # Fallback: Simple keyword matching
    }
    
    # Skill Extraction Weights
    SKILL_EXTRACTOR_WEIGHTS: dict = {
        "regex": 0.30,       # Fast baseline
        "spacy": 0.50,       # Balanced accuracy
        "vocab": 0.20,       # Large vocabulary
    }
    
    # Funnel Configuration
    STAGE1_MIN_SCORE: int = 60
    STAGE1_REJECT_SCORE: int = 40
    COHORT_SIZE: int = 500
    COHORT_SEGMENTS: dict = {"dev": 0.50, "data": 0.30, "design": 0.20}
    
    # Performance
    CACHE_TTL: int = 3600  # 1 hour
    BATCH_SIZE: int = 100
    MAX_WORKERS: int = 4
    
    # Redis (optional)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    USE_REDIS: bool = os.getenv("USE_REDIS", "False").lower() == "true"
    
    # Celery (for 50k pipeline)
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")


settings = Settings()
