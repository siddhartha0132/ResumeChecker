# ⚡ EV Hiring Platform

An AI-powered resume parser and candidate ranking system built specifically for the **Electric Vehicle industry**.

## Features

- 📄 **Resume Parsing** — Extracts name, email, phone, skills, education, and experience from PDFs (text + scanned via OCR)
- 🧠 **EV-Specific NER** — Detects 50+ EV industry skills (BMS, CAN Bus, ADAS, ISO 26262, etc.)
- 📊 **TF-IDF Ranking** — Ranks candidates by cosine similarity against the job description
- 🤖 **AI Summarization** — Generates concise resume summaries using DistilBART
- ⭐ **Shortlist Management** — Shortlist/reject candidates and export to CSV
- 🎯 **Skill Gap Analysis** — Shows matching and missing skills per candidate

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 18, Tailwind CSS, Vite, react-dropzone    |
| Backend  | Flask, spaCy, scikit-learn, HuggingFace Transformers |
| NLP      | spaCy NER, TF-IDF, DistilBART summarization     |
| OCR      | Tesseract + pdf2image (for scanned PDFs)        |

## Project Structure

```
ev-hiring/
├── backend/
│   ├── app.py              # Flask REST API
│   ├── resume_parser.py    # NER + OCR resume parsing
│   ├── ranker.py           # TF-IDF cosine similarity ranking
│   ├── summarizer.py       # BART summarization + EV insights
│   ├── requirements.txt
│   └── uploads/            # Temporary PDF storage
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── Header.jsx
    │   │   ├── UploadForm.jsx
    │   │   ├── RankingTable.jsx
    │   │   ├── CandidateCard.jsx
    │   │   └── ShortlistPanel.jsx
    │   └── services/api.js
    ├── package.json
    ├── vite.config.js
    └── tailwind.config.js
```

## Setup & Running

### Prerequisites

- Python 3.9+
- Node.js 18+
- Tesseract OCR (for scanned PDFs)

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

### Backend

```bash
cd ev-hiring/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start the API server
python app.py
# Runs on http://localhost:5000
```

### Frontend

```bash
cd ev-hiring/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Runs on http://localhost:3000
```

## API Endpoints

| Method | Endpoint                    | Description                        |
|--------|-----------------------------|------------------------------------|
| GET    | `/api/health`               | Health check                       |
| POST   | `/api/upload`               | Upload resumes + job description   |
| GET    | `/api/candidates`           | List all parsed candidates         |
| POST   | `/api/shortlist/:id`        | Mark candidate as shortlisted      |
| POST   | `/api/reject/:id`           | Mark candidate as rejected         |

### Upload Request

```
POST /api/upload
Content-Type: multipart/form-data

resumes: [file1.pdf, file2.pdf, ...]
job_description: "Senior Battery Engineer with BMS experience..."
```

## Notes

- The first request will download the DistilBART model (~300MB). Subsequent requests use the cached model.
- For production, replace the in-memory `candidates_db` with a proper database (PostgreSQL, MongoDB, etc.).
- The `uploads/` folder stores PDFs temporarily. Add a cleanup job for production use.
