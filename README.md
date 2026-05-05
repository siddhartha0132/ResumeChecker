# AntiGravity — VisionAstraa EV Academy Hiring Engine

AI resume scorer + 50k applicant funnel. Gemini 1.5 Flash + FastAPI + React.

## Quick Start

```bash
# Backend
cd backend
cp .env.example .env        # add your GEMINI_API_KEY
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install && npm run dev  # → http://localhost:5173
```

## Page 1 — ATS Scorer
Upload PDFs or paste text → NLP regex extracts skills → Gemini scores → ranked dashboard.

## Page 2 — 50k Funnel
1. Seed mock data → Run Stage 1 (ATS) → Stage 2 (Form) → Stage 3 (Cohort 500)
2. Export final CSV

## Stack
- **Backend**: FastAPI, aiosqlite, pdfplumber, google-generativeai
- **Frontend**: React 18, Vite, Chart.js, Axios
# ResumeChecker
# ResumeChecker
