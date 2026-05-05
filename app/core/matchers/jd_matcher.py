"""
Job Description Matcher
Matches resumes against job descriptions with weighted scoring
"""

from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config.constants import SKILL_WEIGHTS


class JDMatcher:
    """
    Job Description Matcher
    Implements weighted skill matching from ev-hiring-platform
    """
    
    def __init__(self):
        self.skill_weights = SKILL_WEIGHTS
    
    def calculate_tfidf_similarity(
        self,
        resume_text: str,
        jd_text: str
    ) -> float:
        """
        Calculate TF-IDF cosine similarity between resume and JD
        """
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=2000,
                ngram_range=(1, 2),
                sublinear_tf=True,
            )
            
            documents = [jd_text, resume_text]
            tfidf_matrix = vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except Exception as e:
            print(f"TF-IDF error: {e}")
            return 0.0
    
    def calculate_weighted_skill_score(
        self,
        jd_skills: List[str],
        resume_skills: List[str]
    ) -> float:
        """
        Calculate weighted skill match score
        Critical skills (BMS, AUTOSAR, ADAS) count more
        """
        if not jd_skills:
            return 0.0
        
        jd_lower = {s.lower() for s in jd_skills}
        
        # Calculate total weight of JD skills
        total_weight = sum(
            self.skill_weights.get(s.lower(), 1)
            for s in jd_skills
        )
        
        if total_weight == 0:
            return 0.0
        
        # Calculate matched weight
        matched_weight = sum(
            self.skill_weights.get(s.lower(), 1)
            for s in resume_skills
            if s.lower() in jd_lower
        )
        
        return min(matched_weight / total_weight, 1.0)
    
    def calculate_experience_score(self, years: float) -> float:
        """Normalize experience years to 0-1 score"""
        if years <= 0:
            return 0.0
        if years >= 10:
            return 1.0
        return years / 10.0
    
    def match(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills: List[str],
        jd_skills: List[str],
        experience_years: float = 0.0
    ) -> Dict:
        """
        Comprehensive JD matching with weighted scoring
        
        Returns:
            {
                "match_score": 0-100,
                "tfidf_score": 0-100,
                "skill_score": 0-100,
                "experience_score": 0-100,
                "skills_matched": [...],
                "skills_missing": [...],
                "match_percentage": 0-100
            }
        """
        # TF-IDF similarity (50% weight)
        tfidf_sim = self.calculate_tfidf_similarity(resume_text, jd_text)
        
        # Weighted skill match (30% weight)
        skill_score = self.calculate_weighted_skill_score(jd_skills, resume_skills)
        
        # Experience score (20% weight)
        exp_score = self.calculate_experience_score(experience_years)
        
        # Composite score
        composite = (
            tfidf_sim * 0.50 +
            skill_score * 0.30 +
            exp_score * 0.20
        )
        
        # Skill gap analysis
        resume_skills_lower = {s.lower() for s in resume_skills}
        jd_skills_lower = {s.lower() for s in jd_skills}
        
        matched = [s for s in resume_skills if s.lower() in jd_skills_lower]
        missing = [s for s in jd_skills if s.lower() not in resume_skills_lower]
        
        match_pct = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0
        
        return {
            "match_score": round(composite * 100, 1),
            "tfidf_score": round(tfidf_sim * 100, 1),
            "skill_score": round(skill_score * 100, 1),
            "experience_score": round(exp_score * 100, 1),
            "skills_matched": matched,
            "skills_missing": missing,
            "match_percentage": round(match_pct, 1)
        }
    
    def rank_candidates(
        self,
        candidates: List[Dict],
        jd_text: str,
        jd_skills: List[str]
    ) -> List[Dict]:
        """
        Rank multiple candidates against a job description
        """
        for candidate in candidates:
            match_result = self.match(
                resume_text=candidate.get("resume_text", ""),
                jd_text=jd_text,
                resume_skills=candidate.get("skills", []),
                jd_skills=jd_skills,
                experience_years=candidate.get("experience_years", 0.0)
            )
            
            candidate.update(match_result)
        
        # Sort by match score
        candidates.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        # Add rank
        for rank, candidate in enumerate(candidates, start=1):
            candidate["rank"] = rank
        
        return candidates


# Singleton instance
_matcher = None

def get_jd_matcher() -> JDMatcher:
    """Get or create singleton JD matcher"""
    global _matcher
    if _matcher is None:
        _matcher = JDMatcher()
    return _matcher
