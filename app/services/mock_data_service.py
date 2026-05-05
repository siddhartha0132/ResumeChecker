"""
Mock data service — generate realistic test resumes using Faker
"""

import random
from typing import List, Dict
from datetime import datetime

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

from app.config.constants import MAIN_SKILLS, EV_SKILLS, VISIONASTRAA_SKILLS


DEGREE_LEVELS = ["B.Tech", "M.Tech", "B.E", "M.E", "B.Sc", "M.Sc", "PhD"]
UNIVERSITIES = [
    "IIT Bombay", "IIT Delhi", "IIT Madras", "NIT Trichy",
    "BITS Pilani", "VIT Vellore", "Anna University", "SRM University",
]
COMPANIES = [
    "Tata Motors", "Mahindra Electric", "Ola Electric", "Ather Energy",
    "Hero Electric", "Revolt Motors", "Infosys", "TCS", "Wipro",
    "Amazon", "Google", "Microsoft", "Bosch", "Continental",
]
ROLES = [
    "Software Engineer", "EV Engineer", "Battery Engineer",
    "Embedded Systems Engineer", "Data Scientist", "ML Engineer",
    "Full Stack Developer", "Backend Developer", "Research Engineer",
]

ALL_SKILLS = list(set(MAIN_SKILLS + EV_SKILLS + list(VISIONASTRAA_SKILLS)))


def _pick_skills(n: int = 8) -> List[str]:
    return random.sample(ALL_SKILLS, min(n, len(ALL_SKILLS)))


def generate_resume_text(
    name: str,
    email: str,
    phone: str,
    skills: List[str],
    experience_years: int,
    degree: str,
    university: str,
    company: str,
    role: str,
) -> str:
    """Generate a realistic resume text."""
    skills_str = ", ".join(skills)
    return f"""{name}
{email} | {phone}

EDUCATION
{degree} in Electronics & Communication Engineering
{university} | 2018 - 2022 | CGPA: {random.uniform(7.0, 9.5):.2f}

EXPERIENCE
{role} — {company}
{2024 - experience_years} - Present ({experience_years} years)
- Developed and maintained systems using {skills[0]} and {skills[1] if len(skills) > 1 else 'Python'}
- Led a team of {random.randint(2, 8)} engineers on {random.choice(['EV charging', 'battery management', 'motor control', 'data pipeline'])} project
- Improved system performance by {random.randint(15, 45)}% through optimization
- Collaborated with cross-functional teams on product development

SKILLS
Technical: {skills_str}
Soft Skills: Team Leadership, Problem Solving, Agile, Communication

PROJECTS
{random.choice(['EV Battery Management System', 'Motor Control Algorithm', 'Charging Station Software', 'Fleet Telematics Platform'])}
- Built using {skills[0]}, {skills[1] if len(skills) > 1 else 'Python'}
- Achieved {random.randint(80, 99)}% efficiency improvement

CERTIFICATIONS
- {random.choice(['AWS Certified', 'Google Cloud Professional', 'ISO 26262 Functional Safety', 'AUTOSAR Certified'])}
"""


def generate_mock_candidates(count: int = 10) -> List[Dict]:
    """
    Generate `count` mock candidate records.
    Uses Faker if available, otherwise uses static data.
    """
    if count > 1000:
        count = 1000

    candidates = []

    if FAKER_AVAILABLE:
        fake = Faker("en_IN")
        for i in range(count):
            name = fake.name()
            email = fake.email()
            phone = fake.phone_number()[:15]
            skills = _pick_skills(random.randint(5, 15))
            exp = random.randint(0, 10)
            degree = random.choice(DEGREE_LEVELS)
            university = random.choice(UNIVERSITIES)
            company = random.choice(COMPANIES)
            role = random.choice(ROLES)

            text = generate_resume_text(
                name, email, phone, skills, exp, degree, university, company, role
            )
            candidates.append({
                "id": i + 1,
                "name": name,
                "email": email,
                "phone": phone,
                "skills": skills,
                "experience_years": exp,
                "degree": degree,
                "university": university,
                "company": company,
                "role": role,
                "resume_text": text,
                "generated_at": datetime.now().isoformat(),
            })
    else:
        # Fallback without Faker
        for i in range(count):
            name = f"Candidate {i + 1}"
            email = f"candidate{i + 1}@example.com"
            phone = f"+91 98{random.randint(10000000, 99999999)}"
            skills = _pick_skills(random.randint(5, 12))
            exp = random.randint(0, 8)
            degree = random.choice(DEGREE_LEVELS)
            university = random.choice(UNIVERSITIES)
            company = random.choice(COMPANIES)
            role = random.choice(ROLES)

            text = generate_resume_text(
                name, email, phone, skills, exp, degree, university, company, role
            )
            candidates.append({
                "id": i + 1,
                "name": name,
                "email": email,
                "phone": phone,
                "skills": skills,
                "experience_years": exp,
                "degree": degree,
                "university": university,
                "company": company,
                "role": role,
                "resume_text": text,
                "generated_at": datetime.now().isoformat(),
            })

    return candidates
