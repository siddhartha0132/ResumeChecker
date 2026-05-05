import google.generativeai as genai
import os
import json
import time

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

ATS_SYSTEM_PROMPT = """You are an expert technical recruiter for VisionAstraa EV Academy —
an electric vehicle education startup. You score resumes against job descriptions.

You will be given:
- The full resume text
- The job description
- A pre-extracted list of skills found via NLP/regex

Your job: validate and enrich that extraction, then produce a score.

Return ONLY valid JSON. No explanation text outside the JSON.

JSON format:
{
  "ats_score": <0-100 integer>,
  "skills_matched": ["skill1", "skill2"],
  "skills_missing": ["skill1", "skill2"],
  "experience_years": <float>,
  "education_score": <0-25>,
  "skills_score": <0-40>,
  "experience_score": <0-25>,
  "format_score": <0-10>,
  "summary": "<2 sentence honest assessment>",
  "hire_signal": "<strong|moderate|weak>"
}"""


async def score_resume(resume_text: str, jd_text: str, nlp_skills: list) -> dict:
    prompt = f"""{ATS_SYSTEM_PROMPT}

JOB DESCRIPTION:
{jd_text}

NLP-EXTRACTED SKILLS (pre-detected by regex):
{json.dumps(nlp_skills)}

FULL RESUME TEXT:
{resume_text[:3000]}
"""
    for attempt in range(4):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait = (2 ** attempt) * 10  # 10s, 20s, 40s, 80s
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini rate limit exceeded after retries. Try again in 1 minute.")

