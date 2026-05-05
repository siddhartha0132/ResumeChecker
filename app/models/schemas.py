"""
Pydantic schemas for request/response validation
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ResumeParseRequest(BaseModel):
    """Request model for resume parsing"""
    extract_skills: bool = True


class ResumeParseResponse(BaseModel):
    """Response model for resume parsing"""
    filename: str
    text: str
    full_text_length: int
    method: str
    is_ocr: bool
    metadata: Dict
    skills: Optional[List[str]] = None
    skill_confidence: Optional[Dict[str, float]] = None
    skill_extraction_method: Optional[str] = None


class ResumeScoreRequest(BaseModel):
    """Request model for resume scoring"""
    job_description: str
    scoring_method: str = "ensemble"


class ResumeScoreResponse(BaseModel):
    """Response model for resume scoring"""
    filename: str
    parsing_method: str
    is_ocr: bool
    resume_skills: List[str]
    resume_skill_count: int
    jd_skills: List[str]
    jd_skill_count: int
    score: float
    ats_score: int
    skills_matched: List[str]
    skills_missing: List[str]
    match_percentage: float
    summary: str
    hire_signal: str
    scoring_method: str
    methods_used: List[str]
    individual_scores: Dict[str, float]
    timestamp: str


class BatchScoreResponse(BaseModel):
    """Response model for batch scoring"""
    total_resumes: int
    successfully_parsed: int
    failed: int
    jd_skills: List[str]
    jd_skill_count: int
    candidates: List[Dict]
    top_candidate: Optional[Dict]
    scoring_method: str
    timestamp: str


class SkillExtractionRequest(BaseModel):
    """Request model for skill extraction"""
    text: str
    method: str = "ensemble"


class SkillExtractionResponse(BaseModel):
    """Response model for skill extraction"""
    skills: List[str]
    skill_count: int
    confidence: Dict[str, float]
    method: str
    method_results: Optional[Dict] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    gemini_configured: bool
    ocr_available: bool
    spacy_loaded: bool
    timestamp: str


class CandidateProfile(BaseModel):
    """Candidate profile model"""
    id: Optional[int] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    raw_text: str
    skills_extracted: List[str]
    skills_matched: List[str]
    skills_missing: List[str]
    ats_score: int
    experience_years: float = 0.0
    hire_signal: str
    summary: str
    stage: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JobDescription(BaseModel):
    """Job description model"""
    id: Optional[int] = None
    title: str
    description: str
    required_skills: List[str]
    created_at: Optional[str] = None
