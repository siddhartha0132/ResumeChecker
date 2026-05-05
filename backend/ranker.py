from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict


# EV-domain skill weights — more important skills count more
SKILL_WEIGHTS = {
    'battery management': 3, 'bms': 3, 'lithium-ion': 2, 'solid state battery': 3,
    'battery thermal management': 2, 'cell balancing': 2,
    'electric motor': 2, 'inverter': 2, 'powertrain': 2, 'regenerative braking': 2,
    'ev charging': 2, 'fast charging': 2, 'ccs': 2, 'chademo': 2, 'v2g': 3,
    'can bus': 3, 'autosar': 3, 'matlab': 2, 'simulink': 2, 'iso 26262': 3,
    'aspice': 2, 'embedded c': 2, 'model based design': 2,
    'adas': 3, 'autonomous driving': 3, 'sensor fusion': 3, 'lidar': 2, 'radar': 2,
    'hil testing': 2, 'sil testing': 2, 'dspace': 2,
    'python': 1, 'c++': 1, 'java': 1, 'power electronics': 2,
}


def weighted_skill_score(job_skills: List[str], candidate_skills: List[str]) -> float:
    """Weighted skill overlap — domain-critical skills count more."""
    if not job_skills:
        return 0.0
    job_lower = {s.lower() for s in job_skills}
    total_weight = sum(SKILL_WEIGHTS.get(s.lower(), 1) for s in job_skills)
    if total_weight == 0:
        return 0.0
    matched_weight = sum(
        SKILL_WEIGHTS.get(s.lower(), 1)
        for s in candidate_skills
        if s.lower() in job_lower
    )
    return min(matched_weight / total_weight, 1.0)


def experience_score(years: int) -> float:
    """Normalise experience years to 0-1."""
    if years <= 0:  return 0.0
    if years >= 10: return 1.0
    return years / 10.0


def rank_candidates(job_description: str, resumes: List[Dict]) -> List[Dict]:
    """
    Composite ranking:
      50% TF-IDF cosine similarity  (full-text relevance)
      30% Weighted skill match      (EV-specific skills)
      20% Experience                (years)
    """
    if not resumes:
        return []

    # ── TF-IDF ────────────────────────────────────────────────────────────────
    documents = [job_description] + [
        f"{' '.join(r.get('skills', []))} {r.get('full_text', '')}"
        for r in resumes
    ]

    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=2000,
        ngram_range=(1, 2),
        sublinear_tf=True,          # dampens very frequent terms
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # ── Extract job skills for skill-match component ───────────────────────────
    from resume_parser import extract_skills
    job_skills = extract_skills(job_description)

    # ── Build ranked results ───────────────────────────────────────────────────
    results = []
    for i, (resume, tfidf_sim) in enumerate(zip(resumes, similarities)):
        cand_skills = resume.get('skills', [])
        exp_years   = resume.get('experience_years', resume.get('experience', 0))

        w_skill = weighted_skill_score(job_skills, cand_skills)
        w_exp   = experience_score(exp_years)

        # Composite score (0-100)
        composite = (
            tfidf_sim  * 0.50 +
            w_skill    * 0.30 +
            w_exp      * 0.20
        ) * 100

        results.append({
            "rank": 0,
            "candidate_id": i,
            "name":             resume.get('name', 'Unknown'),
            "email":            resume.get('email', ''),
            "phone":            resume.get('phone', ''),
            "skills":           cand_skills,
            "experience_years": exp_years,
            "education":        resume.get('education', []),
            "match_score":      round(composite, 1),
            "tfidf_score":      round(tfidf_sim * 100, 1),
            "skill_score":      round(w_skill * 100, 1),
            "exp_score":        round(w_exp * 100, 1),
            "status":           "pending",
        })

    results.sort(key=lambda x: x['match_score'], reverse=True)
    for idx, c in enumerate(results):
        c['rank'] = idx + 1

    return results


def calculate_skill_match(job_skills: List[str], candidate_skills: List[str]) -> Dict:
    """Detailed skill gap analysis."""
    job_lower  = {s.lower() for s in job_skills}
    cand_lower = {s.lower() for s in candidate_skills}

    matching = [s for s in candidate_skills if s.lower() in job_lower]
    missing  = [s for s in job_skills      if s.lower() not in cand_lower]

    pct = (len(matching) / len(job_skills) * 100) if job_skills else 0.0

    return {
        "matching_skills": matching,
        "missing_skills":  missing,
        "match_percent":   round(pct, 1),
    }
