from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid

from resume_parser import parse_resume, extract_skills
from ranker import rank_candidates, calculate_skill_match
from summarizer import summarize_resume, generate_ev_specific_insights, start_loading, is_ready
from storage import save_candidates, load_candidates

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=False)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Persistent candidate store — survives page refreshes, lost on server restart
candidates_db: dict = load_candidates()

# Start loading the summarizer model in the background immediately
start_loading()


# ── Health ────────────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "summarizer_ready": is_ready(),
        "candidates_stored": len(candidates_db),
    })


# ── Upload & Rank ─────────────────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
def upload_resumes():
    if 'resumes' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist('resumes')
    job_description = request.form.get('job_description', '').strip()

    parsed_resumes = []

    for file in files:
        if not file or not file.filename:
            continue

        file_id  = str(uuid.uuid4())
        filepath = os.path.join(UPLOAD_FOLDER, f"{file_id}.pdf")
        file.save(filepath)

        parsed = parse_resume(filepath)
        print(f"[parse] {file.filename}: success={parsed.get('success')} "
              f"name='{parsed.get('name')}' skills={len(parsed.get('skills', []))}")

        if parsed['success']:
            candidate = {
                "id":             file_id,
                "filename":       file.filename,
                "name":           parsed['name'] or file.filename.replace('.pdf', '').replace('_', ' ').title(),
                "email":          parsed['email'],
                "phone":          parsed['phone'],
                "experience_years": parsed['experience'],
                "skills":         parsed['skills'],
                "education":      parsed['education'],
                "full_text":      parsed['full_text'],
                "text_preview":   parsed['text'],
                "summary":        summarize_resume(parsed['full_text']),
                "ev_insights":    generate_ev_specific_insights(parsed['full_text'], parsed['skills']),
            }
            parsed_resumes.append(candidate)
            candidates_db[file_id] = candidate
        else:
            print(f"[parse] FAILED {file.filename}: {parsed.get('error')}")

    if not parsed_resumes:
        return jsonify({
            "success": True,
            "total_parsed": 0,
            "ranked_candidates": [],
            "job_skills": [],
            "message": "No resumes could be parsed. Ensure PDFs contain readable text.",
        })

    # ── Rank ──────────────────────────────────────────────────────────────────
    if job_description:
        ranked    = rank_candidates(job_description, parsed_resumes)
        job_skills = extract_skills(job_description)

        resume_by_idx = {i: parsed_resumes[i] for i in range(len(parsed_resumes))}

        for c in ranked:
            orig = resume_by_idx.get(c['candidate_id'], {})
            c['skill_match'] = calculate_skill_match(job_skills, c['skills'])
            c['summary']     = orig.get('summary', '')
            c['ev_insights'] = orig.get('ev_insights', {})
            c['education']   = orig.get('education', [])

        save_candidates(candidates_db)

        return jsonify({
            "success":          True,
            "total_parsed":     len(parsed_resumes),
            "ranked_candidates": ranked,
            "job_skills":       job_skills,
            "summarizer_ready": is_ready(),
        })

    # No job description — return with zero scores
    unranked = []
    for i, c in enumerate(parsed_resumes):
        unranked.append({
            **c,
            "rank": i + 1,
            "match_score": 0,
            "tfidf_score": 0,
            "skill_score": 0,
            "exp_score":   0,
            "candidate_id": i,
            "skill_match": {"matching_skills": [], "missing_skills": [], "match_percent": 0},
        })

    save_candidates(candidates_db)
    return jsonify({
        "success":           True,
        "total_parsed":      len(parsed_resumes),
        "ranked_candidates": unranked,
        "job_skills":        [],
    })


# ── Candidates list ───────────────────────────────────────────────────────────
@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    return jsonify({"candidates": list(candidates_db.values())})


# ── Shortlist / Reject ────────────────────────────────────────────────────────
@app.route('/api/shortlist/<candidate_id>', methods=['POST'])
def shortlist_candidate(candidate_id):
    if candidate_id in candidates_db:
        candidates_db[candidate_id]['status'] = 'shortlisted'
        save_candidates(candidates_db)
        return jsonify({"success": True, "status": "shortlisted"})
    return jsonify({"error": "Candidate not found"}), 404


@app.route('/api/reject/<candidate_id>', methods=['POST'])
def reject_candidate(candidate_id):
    if candidate_id in candidates_db:
        candidates_db[candidate_id]['status'] = 'rejected'
        save_candidates(candidates_db)
        return jsonify({"success": True, "status": "rejected"})
    return jsonify({"error": "Candidate not found"}), 404


# ── Clear all (dev utility) ───────────────────────────────────────────────────
@app.route('/api/clear', methods=['POST'])
def clear_candidates():
    candidates_db.clear()
    save_candidates(candidates_db)
    return jsonify({"success": True, "message": "All candidates cleared"})


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0', use_reloader=False)
