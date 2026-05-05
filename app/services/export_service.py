"""
Export service — CSV and JSON export of candidate results
"""

import csv
import json
import io
from typing import List, Dict
from datetime import datetime


def export_to_csv(candidates: List[Dict], jd_skills: List[str] = None) -> str:
    """
    Export candidates to CSV string.
    Returns the CSV content as a string.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Rank", "Name", "Email", "Phone", "Filename",
        "ATS Score", "Hire Signal", "Experience Years",
        "Matched Skills", "Missing Skills", "All Skills",
        "Parsing Method", "Is OCR", "Summary",
    ])

    for c in candidates:
        candidate_info = c.get("candidate", {})
        writer.writerow([
            c.get("rank", ""),
            candidate_info.get("name", c.get("name", "")),
            candidate_info.get("email", c.get("email", "")),
            candidate_info.get("phone", c.get("phone", "")),
            c.get("filename", ""),
            c.get("ats_score", 0),
            c.get("hire_signal", ""),
            candidate_info.get("experience_years", c.get("experience_years", 0)),
            "; ".join(c.get("skills_matched", [])),
            "; ".join(c.get("skills_missing", [])),
            "; ".join(c.get("skills", c.get("skills_matched", []))),
            c.get("parsing_method", c.get("parsing", {}).get("method", "")),
            "Yes" if c.get("is_ocr", c.get("parsing", {}).get("is_ocr", False)) else "No",
            c.get("summary", ""),
        ])

    # Summary footer
    if candidates:
        writer.writerow([])
        writer.writerow(["--- Summary ---"])
        writer.writerow(["Total Candidates", len(candidates)])
        writer.writerow(["Top Candidate", candidates[0].get("candidate", {}).get("name", candidates[0].get("name", ""))])
        writer.writerow(["Top Score", candidates[0].get("ats_score", 0)])
        avg = sum(c.get("ats_score", 0) for c in candidates) / len(candidates)
        writer.writerow(["Average Score", round(avg, 1)])
        if jd_skills:
            writer.writerow(["JD Skills", "; ".join(jd_skills)])
        writer.writerow(["Exported At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    return output.getvalue()


def export_to_json(candidates: List[Dict], jd_skills: List[str] = None) -> str:
    """Export candidates to JSON string."""
    payload = {
        "exported_at": datetime.now().isoformat(),
        "total_candidates": len(candidates),
        "jd_skills": jd_skills or [],
        "candidates": candidates,
    }
    return json.dumps(payload, indent=2, default=str)
