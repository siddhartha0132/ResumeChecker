from dataclasses import asdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from services.entities import (
    extract_candidate_profile,
    extract_skills,
    humanize_skill,
    is_resume_like,
    load_skill_vocabulary,
    validate_resume_plausibility,
)


TEXT_WEIGHT = 0.72
SKILL_WEIGHT = 0.28


def _safe_percent(value):
    return round(max(0.0, min(1.0, value)) * 100, 1)


def _text_similarity_scores(resume_texts, job_description):
    if not resume_texts or not job_description.strip():
        return []

    corpus = resume_texts + [job_description]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
    try:
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return [0.0 for _ in resume_texts]
    similarities = cosine_similarity(matrix[:-1], matrix[-1:]).flatten()
    return [float(score) for score in similarities]


def score_documents(documents, job_description, skill_csv_path):
    vocabulary = load_skill_vocabulary(skill_csv_path)
    jd_skills = set(extract_skills(job_description, vocabulary))
    text_scores = _text_similarity_scores([document.text for document in documents], job_description)
    candidates = []

    for index, document in enumerate(documents):
        profile = extract_candidate_profile(document.text, document.filename, vocabulary)
        resume_skills = set(profile["skills"])
        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)
        skill_score = len(matched_skills) / len(jd_skills) if jd_skills else 0.0
        text_score = text_scores[index] if index < len(text_scores) else 0.0
        final_score = (TEXT_WEIGHT * text_score) + (SKILL_WEIGHT * skill_score)

        is_resume, resume_reasons = is_resume_like(document.text, vocabulary)
        warnings, red_flags = validate_resume_plausibility(profile, document.text, vocabulary)

        if not is_resume:
            warnings.extend(resume_reasons)
            if resume_reasons:
                red_flags.append("File does not appear to be a resume")

        candidates.append(
            {
                "rank": 0,
                "filename": document.filename,
                "extension": document.extension.upper(),
                "name": profile["name"],
                "email": profile["email"] or "Not found",
                "phone": profile["phone"] or "Not found",
                "score": _safe_percent(final_score),
                "text_score": _safe_percent(text_score),
                "skill_score": _safe_percent(skill_score),
                "skills": [humanize_skill(skill) for skill in sorted(resume_skills)],
                "matched_skills": [humanize_skill(skill) for skill in matched_skills],
                "missing_skills": [humanize_skill(skill) for skill in missing_skills],
                "matched_count": len(matched_skills),
                "missing_count": len(missing_skills),
                "warnings": warnings,
                "red_flags": red_flags,
                "is_resume_like": is_resume,
                "is_ocr": document.is_ocr,
            }
        )

    candidates.sort(key=lambda candidate: candidate["score"], reverse=True)
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank

    summary = summarize_results(candidates, [humanize_skill(skill) for skill in sorted(jd_skills)])
    return candidates, summary


def summarize_results(candidates, jd_skills):
    if not candidates:
        return {"total": 0, "top_score": 0, "average_score": 0, "jd_skills": jd_skills, "top_candidate": ""}

    scores = [candidate["score"] for candidate in candidates]
    return {
        "total": len(candidates),
        "top_score": max(scores),
        "average_score": round(sum(scores) / len(scores), 1),
        "jd_skills": jd_skills,
        "top_candidate": candidates[0]["name"],
        "candidates_with_warnings": sum(1 for c in candidates if c["warnings"]),
        "candidates_with_red_flags": sum(1 for c in candidates if c["red_flags"]),
    }


def parsed_document_to_dict(document):
    return asdict(document)
