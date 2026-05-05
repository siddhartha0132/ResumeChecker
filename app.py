import csv
import logging
import os
import uuid
from datetime import datetime
from logging.handlers import RotatingFileHandler

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename

from services.documents import ALLOWED_EXTENSIONS, allowed_file, extract_text_from_file
from services.scoring import score_documents


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
RUNS_DIR = os.path.join(FILES_DIR, "runs")
OUTPUT_DIR = os.path.join(FILES_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "Data")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample_resumes")
SKILL_CSV_PATH = os.path.join(DATA_DIR, "skill_red.csv")
LOG_PATH = os.path.join(BASE_DIR, "flask.log")

MIN_RESUMES = 5
MAX_RESUMES = 10


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "visionastraa-dev-secret")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
    storage_uri="memory://",
)


for directory in (FILES_DIR, RUNS_DIR, OUTPUT_DIR):
    os.makedirs(directory, exist_ok=True)


handler = RotatingFileHandler(LOG_PATH, maxBytes=10 * 1024 * 1024, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s [%(request_id)s] %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


def sample_resume_names():
    if not os.path.isdir(SAMPLE_DIR):
        return []
    return sorted(filename for filename in os.listdir(SAMPLE_DIR) if filename.endswith(".txt"))


def validate_score_request(resume_files, job_description):
    errors = []
    uploads = [file for file in resume_files if file and file.filename]

    if not job_description.strip():
        errors.append("Job description is required.")
    if len(uploads) < MIN_RESUMES or len(uploads) > MAX_RESUMES:
        errors.append(f"Upload {MIN_RESUMES}-{MAX_RESUMES} resumes for this demo.")

    unsupported = [file.filename for file in uploads if not allowed_file(file.filename)]
    if unsupported:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS)).upper()
        errors.append(f"Unsupported file type: {', '.join(unsupported)}. Allowed formats: {allowed}.")

    return uploads, errors


def save_uploads(uploads, run_dir):
    saved_files = []
    for upload in uploads:
        safe_name = secure_filename(upload.filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        destination = os.path.join(run_dir, unique_name)
        upload.save(destination)
        saved_files.append((destination, safe_name))
    return saved_files


def check_duplicates(saved_files):
    seen_hashes = {}
    duplicates = []
    for path, original_name in saved_files:
        doc = extract_text_from_file(path, original_name)
        if doc.file_hash and doc.file_hash in seen_hashes:
            duplicates.append((original_name, seen_hashes[doc.file_hash]))
        elif doc.file_hash:
            seen_hashes[doc.file_hash] = original_name
    return duplicates


def write_results_csv(run_id, candidates, summary):
    csv_path = os.path.join(OUTPUT_DIR, f"{run_id}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Rank",
                "Candidate",
                "Email",
                "Phone",
                "Resume File",
                "Final Score",
                "Text Score",
                "Skill Score",
                "Matched Skills",
                "Missing Skills",
                "Detected Skills",
                "Warnings",
                "Red Flags",
                "OCR Used",
            ]
        )
        for candidate in candidates:
            writer.writerow(
                [
                    candidate["rank"],
                    candidate["name"],
                    candidate["email"],
                    candidate["phone"],
                    candidate["filename"],
                    candidate["score"],
                    candidate["text_score"],
                    candidate["skill_score"],
                    "; ".join(candidate["matched_skills"]),
                    "; ".join(candidate["missing_skills"]),
                    "; ".join(candidate["skills"]),
                    "; ".join(candidate["warnings"]),
                    "; ".join(candidate["red_flags"]),
                    "Yes" if candidate.get("is_ocr") else "No",
                ]
            )
        writer.writerow([])
        writer.writerow(["Total Candidates", summary["total"]])
        writer.writerow(["Top Candidate", summary["top_candidate"]])
        writer.writerow(["Top Score", summary["top_score"]])
        writer.writerow(["Average Score", summary["average_score"]])
        writer.writerow(["Candidates with Warnings", summary.get("candidates_with_warnings", 0)])
        writer.writerow(["Candidates with Red Flags", summary.get("candidates_with_red_flags", 0)])
    return csv_path


@app.before_request
def before_request():
    request_id = uuid.uuid4().hex[:8]
    request.environ["request_id"] = request_id


@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        min_resumes=MIN_RESUMES,
        max_resumes=MAX_RESUMES,
        allowed_extensions=sorted(ALLOWED_EXTENSIONS),
        sample_resumes=sample_resume_names(),
    )


@app.route("/score", methods=["POST"])
@limiter.limit("10 per minute")
def score():
    request_id = request.environ.get("request_id", "unknown")
    job_description = request.form.get("job_description", "").strip()
    uploads, errors = validate_score_request(request.files.getlist("resumes"), job_description)
    if errors:
        for error in errors:
            flash(error, "error")
            app.logger.warning(f"[{request_id}] Validation error: {error}")
        return redirect(url_for("index"))

    run_id = uuid.uuid4().hex
    run_dir = os.path.join(RUNS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)

    saved_files = save_uploads(uploads, run_dir)
    duplicates = check_duplicates(saved_files)
    for original_name, duplicate_of in duplicates:
        flash(f"Duplicate detected: {original_name} is identical to {duplicate_of}", "warning")

    parsed_documents = [extract_text_from_file(path, original_name) for path, original_name in saved_files]
    valid_documents = [document for document in parsed_documents if document.is_valid]
    failed_documents = [document for document in parsed_documents if not document.is_valid]

    for document in failed_documents:
        flash(f"{document.filename}: {document.error}", "error")
        app.logger.warning(f"[{request_id}] Failed document: {document.filename} - {document.error}")

    if len(valid_documents) < MIN_RESUMES:
        flash(f"Only {len(valid_documents)} readable resumes were found. Please upload at least {MIN_RESUMES} readable PDF, TXT, or DOCX resumes.", "error")
        return redirect(url_for("index"))

    app.logger.info(f"[{request_id}] Scoring {len(valid_documents)} documents for run {run_id}")
    candidates, summary = score_documents(valid_documents, job_description, SKILL_CSV_PATH)
    write_results_csv(run_id, candidates, summary)

    app.logger.info(f"[{request_id}] Completed run {run_id}: {summary['total']} candidates, top={summary['top_candidate']}")

    return render_template(
        "results.html",
        run_id=run_id,
        generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p"),
        candidates=candidates,
        summary=summary,
        failed_documents=failed_documents,
        duplicates=duplicates,
    )


@app.route("/download/<run_id>", methods=["GET"])
def download_results(run_id):
    safe_run_id = secure_filename(run_id)
    csv_path = os.path.join(OUTPUT_DIR, f"{safe_run_id}.csv")
    if not os.path.exists(csv_path):
        flash("Results file was not found. Please score the resumes again.", "error")
        return redirect(url_for("index"))
    return send_file(csv_path, as_attachment=True, download_name="visionastraa_candidates.csv")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}, 200


@app.route("/process", methods=["GET", "POST"])
def legacy_process_redirect():
    flash("Use the VisionAstraa scorer form to upload resumes and a job description together.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(port=8080, debug=False)
