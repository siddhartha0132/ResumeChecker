"""
Feedback Generator
Produces actionable, role-specific improvement suggestions for candidates.
Uses RAG context when available.
"""

from typing import Dict, List


# ── Certification map ─────────────────────────────────────────────────────────

CERT_MAP = {
    "bms":           "EV Battery Management Systems (NPTEL / Coursera)",
    "battery":       "EV Battery Technology Fundamentals (edX)",
    "can bus":       "CAN Protocol Training (Vector Academy)",
    "autosar":       "AUTOSAR Fundamentals (Vector Academy)",
    "matlab":        "MATLAB Onramp for EV Applications (MathWorks)",
    "python":        "Python for Engineers (Coursera / freeCodeCamp)",
    "embedded":      "Embedded Systems Certification (IEEE / Coursera)",
    "iso 26262":     "Functional Safety for Automotive (TÜV SÜD)",
    "aspice":        "ASPICE Practitioner (intacs™)",
    "adas":          "ADAS & Autonomous Driving Fundamentals (Udemy)",
    "ros":           "ROS2 for Robotics (The Construct)",
    "charging":      "EV Charging Infrastructure (CharIN / EVSE Academy)",
    "ocpp":          "OCPP 2.0 Certification (Open Charge Alliance)",
    "v2g":           "V2G Technology & Grid Integration (Coursera)",
    "hil":           "HIL Testing with dSPACE (dSPACE Academy)",
    "solidworks":    "SolidWorks CSWA Certification",
    "docker":        "Docker & Kubernetes Fundamentals (Linux Foundation)",
    "machine learning": "Machine Learning Specialization (Andrew Ng / Coursera)",
}


class FeedbackGenerator:
    """Generates structured, actionable feedback for a scored candidate."""

    def generate(
        self,
        score_result: Dict,
        parsed_info: Dict,
        role_type: str = "general",
        rag_context: str = "",
    ) -> Dict:
        """
        Build a complete feedback object.

        Args:
            score_result : output from EnsembleScorer.score()
            parsed_info  : {name, email, skills, experience_years, ...}
            role_type    : EV role slug
            rag_context  : retrieved knowledge base text (optional)

        Returns:
            {summary, strengths, improvements, certifications, next_steps, score_breakdown}
        """
        final_score   = score_result.get("ats_score", 0)
        matched       = score_result.get("skills_matched", [])
        missing       = score_result.get("skills_missing", [])
        hire_signal   = score_result.get("hire_signal", "weak")
        gemini_summary = score_result.get("summary", "")
        name          = parsed_info.get("name", "Candidate")
        exp_years     = parsed_info.get("experience_years", 0)

        return {
            "summary":          self._summary(name, final_score, hire_signal, gemini_summary),
            "strengths":        self._strengths(matched, exp_years, score_result),
            "improvements":     self._improvements(missing, final_score, role_type),
            "certifications":   self._certifications(missing),
            "next_steps":       self._next_steps(final_score, hire_signal),
            "score_breakdown":  self._breakdown(score_result),
            "rag_enhanced":     bool(rag_context),
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    def _summary(self, name: str, score: int, signal: str, gemini_text: str) -> str:
        if gemini_text:
            return gemini_text
        if score >= 80:
            return (
                f"{name} shows strong alignment with the EV role requirements. "
                "Technical skills and experience match well with our needs."
            )
        if score >= 60:
            return (
                f"{name} has good potential but has gaps in key technical areas. "
                "With targeted skill development this could be a strong fit."
            )
        return (
            f"{name} does not currently meet the minimum requirements for this EV role. "
            "Significant skill development would be needed before reapplying."
        )

    def _strengths(self, matched: List[str], exp_years: float, score_result: Dict) -> List[str]:
        strengths = []
        if matched:
            strengths.append(f"✅ Matched {len(matched)} required skills: {', '.join(matched[:5])}")
        if exp_years >= 3:
            strengths.append(f"✅ {exp_years:.0f} years of relevant experience")
        elif exp_years >= 1:
            strengths.append(f"✅ {exp_years:.0f} year(s) of industry experience")
        gemini_strengths = score_result.get("raw_gemini_result", {}).get("strengths", [])
        strengths.extend(gemini_strengths[:2])
        if not strengths:
            strengths.append("📄 Application received and reviewed")
        return strengths[:5]

    def _improvements(self, missing: List[str], score: int, role_type: str) -> List[str]:
        suggestions = []
        if missing:
            suggestions.append(
                f"📚 Add these missing skills to your resume: **{', '.join(missing[:4])}**"
            )
        suggestions.append(
            "📊 Quantify your achievements — use numbers (e.g., 'Improved efficiency by 20%')"
        )
        suggestions.append(
            "🔋 Highlight EV-specific projects — personal or academic EV work demonstrates passion"
        )
        if score < 60:
            suggestions.append(
                f"🎓 Consider upskilling in {role_type.replace('_', ' ')} fundamentals before reapplying"
            )
        if score >= 60:
            suggestions.append(
                "🔗 Add a GitHub link with EV-related code or projects"
            )
        return suggestions[:5]

    def _certifications(self, missing: List[str]) -> List[str]:
        certs = []
        for skill in missing:
            for key, cert in CERT_MAP.items():
                if key in skill.lower() and cert not in certs:
                    certs.append(cert)
        return certs[:3]

    def _next_steps(self, score: int, signal: str) -> List[str]:
        if score >= 75 or signal == "strong":
            return [
                "✅ You have been shortlisted! Our HR team will contact you within 3-5 business days.",
                "📞 Prepare for a technical interview focusing on EV fundamentals",
                "📁 Review VisionAstraa's EV technology stack on our website",
            ]
        if score >= 60:
            return [
                "🔄 Your application is under review — we may reach out for further assessment",
                "📚 Work on the missing skills listed above to strengthen your profile",
                "🔔 Watch for future openings that may be a better fit",
            ]
        return [
            "📚 Upskill: Take EV technology courses on Coursera / NPTEL / Udemy",
            "🔧 Build projects: Create a portfolio of EV-related projects on GitHub",
            "🔄 Reapply: After developing missing skills, reapply for future openings",
        ]

    def _breakdown(self, score_result: Dict) -> Dict:
        gemini = score_result.get("raw_gemini_result", {})
        breakdown = gemini.get("breakdown", {})
        individual = score_result.get("individual_scores", {})
        return {
            "ats_score":        score_result.get("ats_score", 0),
            "hire_signal":      score_result.get("hire_signal", "weak"),
            "education_score":  breakdown.get("education", "N/A"),
            "skills_score":     breakdown.get("technical_skills", "N/A"),
            "experience_score": breakdown.get("experience", "N/A"),
            "format_score":     breakdown.get("format_score", "N/A"),
            "gemini_score":     round(individual.get("gemini", 0) * 100, 1) if individual.get("gemini") else "N/A",
            "tfidf_score":      round(individual.get("tfidf", 0) * 100, 1) if individual.get("tfidf") else "N/A",
            "rule_score":       round(individual.get("rule_based", 0) * 100, 1) if individual.get("rule_based") else "N/A",
        }


# ── Convenience function ──────────────────────────────────────────────────────

_gen = FeedbackGenerator()

def generate_feedback(
    score_result: Dict,
    parsed_info: Dict,
    role_type: str = "general",
    rag_context: str = "",
) -> Dict:
    return _gen.generate(score_result, parsed_info, role_type, rag_context)
