"""
Helper utilities
"""

import re
from typing import List, Dict
from datetime import datetime


def extract_email(text: str) -> str:
    """Extract email from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    """Extract phone number from text"""
    pattern = r'(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
    match = re.search(pattern, text)
    if match:
        phone = match.group(0).strip()
        # Format nicely
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone
    return ""


def extract_name(text: str, filename: str = "") -> str:
    """Extract candidate name from text"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Try first few lines
    for line in lines[:10]:
        # Remove email and phone
        line = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '', line)
        line = re.sub(r'(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', '', line)
        line = line.strip()
        
        # Check if looks like a name
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(word[0].isupper() for word in words if word):
                if not any(char.isdigit() for char in line):
                    return line
    
    # Fallback to filename
    if filename:
        name = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        return name.title()
    
    return "Unknown Candidate"


def extract_experience_years(text: str) -> float:
    """Extract years of experience from text"""
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:work|industry|professional)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    # Try to infer from years mentioned
    years = re.findall(r'\b(20[0-2][0-9])\b', text)
    if len(years) >= 2:
        unique_years = sorted(set(int(y) for y in years))
        return float(unique_years[-1] - unique_years[0])
    
    return 0.0


def format_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def truncate_text(text: str, max_length: int = 1000) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def calculate_match_percentage(matched: List[str], total: List[str]) -> float:
    """Calculate match percentage"""
    if not total:
        return 0.0
    return round(len(matched) / len(total) * 100, 1)


def deduplicate_list(items: List[str]) -> List[str]:
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for item in items:
        if item.lower() not in seen:
            seen.add(item.lower())
            result.append(item)
    return result


def normalize_skill(skill: str) -> str:
    """Normalize skill name"""
    # Handle acronyms
    acronyms = {"api", "aws", "css", "gcp", "html", "llm", "nlp", "sql", "ui", "iot"}
    words = skill.lower().split()
    
    normalized = []
    for word in words:
        if word in acronyms:
            normalized.append(word.upper())
        else:
            normalized.append(word.capitalize())
    
    return " ".join(normalized)


def merge_skill_lists(*skill_lists: List[str]) -> List[str]:
    """Merge multiple skill lists, removing duplicates"""
    all_skills = []
    for skills in skill_lists:
        all_skills.extend(skills)
    return deduplicate_list(all_skills)


def calculate_confidence_score(votes: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted confidence score"""
    total_score = 0.0
    total_weight = 0.0
    
    for method, vote in votes.items():
        weight = weights.get(method, 0.0)
        total_score += vote * weight
        total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0.0
