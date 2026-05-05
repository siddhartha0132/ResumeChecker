-- Full schema. Run once: sqlite3 antigravity.db < db/schema.sql

CREATE TABLE IF NOT EXISTS job_descriptions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  company TEXT DEFAULT 'VisionAstraa EV Academy',
  description TEXT NOT NULL,
  required_skills TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  phone TEXT,
  college TEXT,
  city TEXT,
  state TEXT,
  raw_text TEXT NOT NULL,
  skills_extracted TEXT,
  skills_matched TEXT,
  skills_missing TEXT,
  experience_years REAL DEFAULT 0,
  ats_score INTEGER DEFAULT 0,
  essay_score INTEGER DEFAULT 0,
  availability_match BOOLEAN DEFAULT 0,
  geographic_distance_km REAL,
  final_score REAL DEFAULT 0,
  stage INTEGER DEFAULT 0,
  selected BOOLEAN DEFAULT 0,
  hire_signal TEXT DEFAULT 'moderate',
  summary TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id INTEGER REFERENCES candidates(id),
  jd_id INTEGER REFERENCES job_descriptions(id),
  why_essay TEXT,
  availability_start DATE,
  availability_end DATE,
  github_link TEXT,
  portfolio_link TEXT,
  ev_project_description TEXT,
  vision_build_idea TEXT,
  form_submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scoring_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  candidate_id INTEGER REFERENCES candidates(id),
  jd_id INTEGER REFERENCES job_descriptions(id),
  ats_breakdown TEXT,
  gemini_reasoning TEXT,
  scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cohort_selections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  candidate_id INTEGER REFERENCES candidates(id),
  selection_reason TEXT,
  segment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_candidates_stage ON candidates(stage);
CREATE INDEX IF NOT EXISTS idx_candidates_ats_score ON candidates(ats_score);
CREATE INDEX IF NOT EXISTS idx_candidates_final_score ON candidates(final_score);
CREATE INDEX IF NOT EXISTS idx_applications_candidate ON applications(candidate_id);
