import aiosqlite
import json

DB_PATH = "antigravity.db"

JD_DESCRIPTION = """VisionAstraa EV Academy is looking for passionate interns to work on electric vehicle
technology, battery systems, motor control, and EV software. Candidates should have knowledge
of Python, embedded systems, or CAD/CAE tools. Experience with Arduino, Raspberry Pi,
or EV components is a plus. Strong problem-solving skills and enthusiasm for sustainable
transportation required."""

JD_SKILLS = json.dumps([
    "Python", "EV", "Arduino", "Raspberry Pi", "CAD", "Battery",
    "Motor Control", "Embedded Systems", "C++", "MATLAB", "SolidWorks"
])


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        with open("db/schema.sql") as f:
            await db.executescript(f.read())
        await db.commit()
        await db.execute("""
            INSERT OR IGNORE INTO job_descriptions (id, title, description, required_skills)
            VALUES (1, 'EV Technology Intern', ?, ?)
        """, (JD_DESCRIPTION, JD_SKILLS))
        await db.commit()


async def save_candidate(
    name, email, raw_text, skills_extracted, skills_matched,
    skills_missing, ats_score, experience_years, hire_signal, summary
):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO candidates
              (name, email, raw_text, skills_extracted, skills_matched, skills_missing,
               ats_score, experience_years, hire_signal, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, raw_text, skills_extracted, skills_matched,
              skills_missing, ats_score, experience_years, hire_signal, summary))
        await db.commit()
        return cursor.lastrowid


async def get_all_candidates():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM candidates ORDER BY ats_score DESC")
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def get_jd(jd_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM job_descriptions WHERE id=?", (jd_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_candidates_by_stage(stage: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM candidates WHERE stage=?", (stage,))
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def update_candidate_stage(candidate_id: int, stage: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE candidates SET stage=? WHERE id=?", (stage, candidate_id))
        await db.commit()


async def reset_candidates_table():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM candidates")
        await db.commit()


async def get_funnel_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT stage, COUNT(*) as count FROM candidates GROUP BY stage
        """)
        rows = await cursor.fetchall()
        stats = {0: 0, 1: 0, 2: 0, 3: 0}
        for r in rows:
            stats[r["stage"]] = r["count"]
        total = await db.execute("SELECT COUNT(*) as total FROM candidates")
        t = await total.fetchone()
        return {"stages": stats, "total": t["total"]}
