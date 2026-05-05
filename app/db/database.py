"""
Async SQLite database layer using aiosqlite
Schema + CRUD operations for candidates and job descriptions
"""

import json
import aiosqlite
from typing import List, Dict, Optional
from datetime import datetime

DB_PATH = "antigravity.db"

# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS job_descriptions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT DEFAULT '[]',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS candidates (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT,
    email               TEXT,
    phone               TEXT,
    filename            TEXT,
    raw_text            TEXT,
    skills_extracted    TEXT DEFAULT '[]',
    skills_matched      TEXT DEFAULT '[]',
    skills_missing      TEXT DEFAULT '[]',
    ats_score           INTEGER DEFAULT 0,
    experience_years    REAL DEFAULT 0.0,
    hire_signal         TEXT DEFAULT 'weak',
    summary             TEXT DEFAULT '',
    parsing_method      TEXT DEFAULT '',
    scoring_method      TEXT DEFAULT '',
    stage               INTEGER DEFAULT 0,
    created_at          TEXT DEFAULT (datetime('now')),
    updated_at          TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates(ats_score DESC);
CREATE INDEX IF NOT EXISTS idx_candidates_stage ON candidates(stage);
CREATE INDEX IF NOT EXISTS idx_candidates_hire  ON candidates(hire_signal);
"""

DEFAULT_JD_SQL = """
INSERT OR IGNORE INTO job_descriptions (id, title, description, required_skills)
VALUES (1, 'EV Technology Intern',
    'VisionAstraa EV Academy is looking for passionate interns to work on electric vehicle technology, battery systems, motor control, and EV software. Candidates should have knowledge of Python, embedded systems, or CAD/CAE tools.',
    '["Python","EV","Arduino","Raspberry Pi","CAD","Battery","Motor Control","Embedded Systems","C++","MATLAB","SolidWorks"]'
);
"""


# ── Init ──────────────────────────────────────────────────────────────────────

async def init_db():
    """Create tables and seed default job description."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA_SQL)
        await db.execute(DEFAULT_JD_SQL)
        await db.commit()


# ── Context manager helper ────────────────────────────────────────────────────

async def get_db():
    """Yield an aiosqlite connection (use as async context manager)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


# ── Candidates CRUD ───────────────────────────────────────────────────────────

async def save_candidate(
    name: str,
    email: str,
    phone: str,
    filename: str,
    raw_text: str,
    skills_extracted: List[str],
    skills_matched: List[str],
    skills_missing: List[str],
    ats_score: int,
    experience_years: float,
    hire_signal: str,
    summary: str,
    parsing_method: str = "",
    scoring_method: str = "",
    stage: int = 0,
) -> int:
    """Insert a candidate and return the new row id."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO candidates
              (name, email, phone, filename, raw_text,
               skills_extracted, skills_matched, skills_missing,
               ats_score, experience_years, hire_signal, summary,
               parsing_method, scoring_method, stage)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                name, email, phone, filename, raw_text[:5000],
                json.dumps(skills_extracted),
                json.dumps(skills_matched),
                json.dumps(skills_missing),
                ats_score, experience_years, hire_signal, summary,
                parsing_method, scoring_method, stage,
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_all_candidates(limit: int = 200, offset: int = 0) -> List[Dict]:
    """Return all candidates ordered by ATS score descending."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM candidates ORDER BY ats_score DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            for field in ("skills_extracted", "skills_matched", "skills_missing"):
                try:
                    d[field] = json.loads(d[field] or "[]")
                except Exception:
                    d[field] = []
            result.append(d)
        return result


async def get_candidate_by_id(candidate_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM candidates WHERE id = ?", (candidate_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        for field in ("skills_extracted", "skills_matched", "skills_missing"):
            try:
                d[field] = json.loads(d[field] or "[]")
            except Exception:
                d[field] = []
        return d


async def update_candidate_stage(candidate_id: int, stage: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE candidates SET stage=?, updated_at=datetime('now') WHERE id=?",
            (stage, candidate_id),
        )
        await db.commit()


async def delete_candidate(candidate_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM candidates WHERE id=?", (candidate_id,))
        await db.commit()


async def clear_all_candidates():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM candidates")
        await db.commit()


# ── Job Descriptions CRUD ─────────────────────────────────────────────────────

async def get_all_jds() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM job_descriptions ORDER BY id")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            try:
                d["required_skills"] = json.loads(d["required_skills"] or "[]")
            except Exception:
                d["required_skills"] = []
            result.append(d)
        return result


async def get_jd_by_id(jd_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM job_descriptions WHERE id=?", (jd_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["required_skills"] = json.loads(d["required_skills"] or "[]")
        except Exception:
            d["required_skills"] = []
        return d


async def create_jd(title: str, description: str, required_skills: List[str]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO job_descriptions (title, description, required_skills) VALUES (?,?,?)",
            (title, description, json.dumps(required_skills)),
        )
        await db.commit()
        return cursor.lastrowid


# ── Stats ─────────────────────────────────────────────────────────────────────

async def get_funnel_stats() -> Dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        total_cur = await db.execute("SELECT COUNT(*) as total FROM candidates")
        total_row = await total_cur.fetchone()
        total = total_row["total"] if total_row else 0

        stage_cur = await db.execute(
            "SELECT stage, COUNT(*) as count FROM candidates GROUP BY stage"
        )
        stage_rows = await stage_cur.fetchall()
        stages = {-1: 0, 0: 0, 1: 0, 2: 0, 3: 0}
        for row in stage_rows:
            stages[row["stage"]] = row["count"]

        signal_cur = await db.execute(
            "SELECT hire_signal, COUNT(*) as count FROM candidates GROUP BY hire_signal"
        )
        signal_rows = await signal_cur.fetchall()
        signals = {row["hire_signal"]: row["count"] for row in signal_rows}

        avg_cur = await db.execute(
            "SELECT AVG(ats_score) as avg_score FROM candidates"
        )
        avg_row = await avg_cur.fetchone()
        avg_score = round(avg_row["avg_score"] or 0, 1)

        return {
            "total_candidates": total,
            "by_stage": stages,
            "by_hire_signal": signals,
            "average_ats_score": avg_score,
        }
