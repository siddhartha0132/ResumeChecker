import pdfplumber
import re
from io import BytesIO

SKILL_VOCAB = [
    # Programming
    "Python", "C++", "C", "Java", "JavaScript", "TypeScript", "MATLAB", "R", "Rust",
    # EV / Hardware
    "EV", "Electric Vehicle", "Battery", "BMS", "Motor Control", "Inverter",
    "Charging", "CAN Bus", "BLDC", "PMSM", "Regenerative Braking",
    # Embedded / IoT
    "Arduino", "Raspberry Pi", "STM32", "ESP32", "RTOS", "Embedded Systems",
    "Firmware", "Microcontroller", "PCB", "KiCad", "Altium",
    # CAD / Simulation
    "SolidWorks", "AutoCAD", "CATIA", "Fusion 360", "ANSYS", "CAD", "CAE",
    "FEA", "CFD", "LTspice",
    # Data / ML
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas",
    "NumPy", "Data Analysis", "SQL", "Power BI", "Tableau",
    # Web / Cloud
    "React", "Node.js", "FastAPI", "Flask", "Django", "Docker", "AWS", "GCP",
    # Soft skills
    "Team Leadership", "Project Management", "Agile", "Research",
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def extract_text_from_string(raw: str) -> str:
    return raw.strip()


def extract_candidate_info(text: str) -> dict:
    email_match = re.search(r'[\w.+-]+@[\w-]+\.\w+', text)
    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,15}', text)
    college_match = re.search(
        r'(IIT|NIT|BITS|VIT|SRM|Amrita|Anna University|'
        r'University of|College of|Institute of Technology)[^\n]*',
        text, re.IGNORECASE
    )
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    name = lines[0] if lines else "Unknown"
    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0).strip() if phone_match else None,
        "college": college_match.group(0).strip() if college_match else None,
    }


def extract_skills_nlp(text: str) -> list:
    found = []
    text_lower = text.lower()
    for skill in SKILL_VOCAB:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill)
    return list(dict.fromkeys(found))


def extract_experience_years(text: str) -> float:
    explicit = re.search(
        r'(\d+\.?\d*)\s*\+?\s*years?\s*(of)?\s*(experience|exp)',
        text, re.IGNORECASE
    )
    if explicit:
        return float(explicit.group(1))
    years = re.findall(r'\b(20[1-2][0-9])\b', text)
    unique_years = sorted(set(int(y) for y in years))
    if len(unique_years) >= 2:
        return float(unique_years[-1] - unique_years[0])
    return 0.0
