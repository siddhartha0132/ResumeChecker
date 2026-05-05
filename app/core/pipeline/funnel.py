"""
50k Applicant Funnel Pipeline
3-stage selection process from main branch
"""

from typing import List, Dict
from app.config.settings import settings


class FunnelPipeline:
    """
    3-stage funnel for 50k applicants:
    Stage 1 (ATS): 50k → 10k (score >= 60)
    Stage 2 (Form): 10k → 2k (weighted scoring)
    Stage 3 (Cohort): 2k → 500 (segmented selection)
    """
    
    def __init__(self):
        self.stage1_min_score = settings.STAGE1_MIN_SCORE
        self.stage1_reject_score = settings.STAGE1_REJECT_SCORE
        self.cohort_size = settings.COHORT_SIZE
        self.cohort_segments = settings.COHORT_SEGMENTS
    
    def stage1_ats_screening(self, candidates: List[Dict]) -> Dict:
        """
        Stage 1: ATS Screening
        Filter by minimum score threshold
        """
        passed = []
        rejected = []
        waitlisted = []
        
        for candidate in candidates:
            score = candidate.get("ats_score", 0)
            
            if score >= self.stage1_min_score:
                candidate["stage"] = 1
                passed.append(candidate)
            elif score < self.stage1_reject_score:
                candidate["stage"] = -1  # Rejected
                rejected.append(candidate)
            else:
                candidate["stage"] = 0  # Waitlisted
                waitlisted.append(candidate)
        
        return {
            "total_processed": len(candidates),
            "passed_to_stage2": len(passed),
            "rejected": len(rejected),
            "waitlisted": len(waitlisted),
            "passed_candidates": passed
        }
    
    def stage2_form_evaluation(self, candidates: List[Dict]) -> Dict:
        """
        Stage 2: Form Evaluation
        Weighted scoring: ATS 30%, Essay 25%, Project 20%, Portfolio 15%, Availability 10%
        """
        weights = {
            "ats_score": 0.30,
            "essay_score": 0.25,
            "ev_project": 0.20,
            "portfolio": 0.15,
            "availability": 0.10,
        }
        
        promoted = []
        
        for candidate in candidates:
            # Calculate composite score
            final_score = (
                candidate.get("ats_score", 0) * weights["ats_score"] +
                candidate.get("essay_score", 0) * weights["essay_score"] +
                (20 if candidate.get("has_ev_project") else 0) * weights["ev_project"] +
                (15 if candidate.get("has_portfolio") else 0) * weights["portfolio"] +
                (10 if candidate.get("availability_match") else 0) * weights["availability"]
            )
            
            candidate["stage2_score"] = final_score
            
            # Promote if score >= 25
            if final_score >= 25:
                candidate["stage"] = 2
                promoted.append(candidate)
        
        return {
            "stage1_count": len(candidates),
            "promoted_to_stage3": len(promoted),
            "promoted_candidates": promoted
        }
    
    def stage3_cohort_selection(self, candidates: List[Dict]) -> Dict:
        """
        Stage 3: Cohort Selection
        Select top 500 with segment distribution:
        - Dev: 50% (250)
        - Data: 30% (150)
        - Design: 20% (100)
        """
        # Sort by ATS score
        ranked = sorted(candidates, key=lambda x: x.get("ats_score", 0), reverse=True)
        
        # Segment limits
        segment_limits = {
            "dev": int(self.cohort_size * self.cohort_segments["dev"]),
            "data": int(self.cohort_size * self.cohort_segments["data"]),
            "design": int(self.cohort_size * self.cohort_segments["design"]),
        }
        
        segment_counts = {"dev": 0, "data": 0, "design": 0}
        selected = []
        
        for candidate in ranked:
            if len(selected) >= self.cohort_size:
                break
            
            # Infer segment from skills
            segment = self._infer_segment(candidate.get("skills_matched", []))
            
            # Check if segment has space
            if segment_counts[segment] < segment_limits[segment]:
                candidate["segment"] = segment
                candidate["stage"] = 3
                selected.append(candidate)
                segment_counts[segment] += 1
        
        return {
            "stage2_count": len(candidates),
            "selected_count": len(selected),
            "segment_distribution": segment_counts,
            "selected_candidates": selected
        }
    
    def _infer_segment(self, skills: List[str]) -> str:
        """Infer candidate segment from skills"""
        skills_lower = [s.lower() for s in skills]
        
        # Data segment keywords
        data_keywords = ["python", "machine learning", "data analysis", "pandas", 
                        "numpy", "tensorflow", "pytorch", "sql", "power bi", "tableau"]
        
        # Design segment keywords
        design_keywords = ["cad", "solidworks", "autocad", "catia", "fusion 360", 
                          "ansys", "fea", "cfd"]
        
        # Count matches
        data_count = sum(1 for kw in data_keywords if kw in skills_lower)
        design_count = sum(1 for kw in design_keywords if kw in skills_lower)
        
        if data_count > design_count and data_count > 0:
            return "data"
        elif design_count > 0:
            return "design"
        else:
            return "dev"  # Default
    
    def run_full_pipeline(self, candidates: List[Dict]) -> Dict:
        """
        Run complete 3-stage pipeline
        """
        # Stage 1: ATS Screening
        stage1_result = self.stage1_ats_screening(candidates)
        
        # Stage 2: Form Evaluation
        stage2_result = self.stage2_form_evaluation(stage1_result["passed_candidates"])
        
        # Stage 3: Cohort Selection
        stage3_result = self.stage3_cohort_selection(stage2_result["promoted_candidates"])
        
        return {
            "total_applicants": len(candidates),
            "stage1": {
                "passed": stage1_result["passed_to_stage2"],
                "rejected": stage1_result["rejected"],
                "waitlisted": stage1_result["waitlisted"]
            },
            "stage2": {
                "promoted": stage2_result["promoted_to_stage3"]
            },
            "stage3": {
                "selected": stage3_result["selected_count"],
                "segments": stage3_result["segment_distribution"]
            },
            "final_cohort": stage3_result["selected_candidates"]
        }


# Singleton instance
_funnel = None

def get_funnel_pipeline() -> FunnelPipeline:
    """Get or create singleton funnel pipeline"""
    global _funnel
    if _funnel is None:
        _funnel = FunnelPipeline()
    return _funnel
