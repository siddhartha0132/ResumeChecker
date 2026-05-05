import re
import shutil
import PyPDF2
import spacy
from typing import Dict, List

# ── spaCy model ───────────────────────────────────────────────────────────────
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import os
    os.system("python3 -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# ── EV skill taxonomy ─────────────────────────────────────────────────────────
EV_SKILLS = [
    # Battery
    'Battery Management', 'BMS', 'Lithium-ion', 'Solid State Battery',
    'Battery Thermal Management', 'Cell Balancing', 'State of Charge',
    # Powertrain
    'Electric Motor', 'Inverter', 'Converter', 'Powertrain',
    'Regenerative Braking', 'Traction Control', 'Differential',
    # Charging
    'EV Charging', 'Fast Charging', 'Wireless Charging', 'CCS', 'CHAdeMO',
    'Type 2 Connector', 'V2G', 'Bidirectional Charging',
    # Software & Controls
    'CAN Bus', 'AUTOSAR', 'MATLAB', 'Simulink', 'Vector CANoe',
    'Model Based Design', 'Embedded C', 'ASPICE', 'ISO 26262',
    # Vehicle Systems
    'ADAS', 'Autonomous Driving', 'Sensor Fusion', 'LIDAR', 'Radar',
    'Camera Systems', 'Path Planning', 'Vehicle Dynamics',
    # Protocols
    'ISO 15118', 'DIN 70121', 'OCPP', 'MQTT', 'WebSocket',
    # Cloud & Telematics
    'AWS IoT', 'Azure IoT', 'Google Cloud', 'Telematics', 'Fleet Management',
    # Testing
    'HIL Testing', 'SIL Testing', 'MIL Testing', 'dSPACE', 'NI LabVIEW',
    # Core Engineering
    'Python', 'C++', 'Java', 'Control Systems', 'Power Electronics',
    'PCB Design', 'EMC/EMI', 'Thermal Management',
]

# ── OCR availability ──────────────────────────────────────────────────────────
def _tesseract_available() -> bool:
    return shutil.which('tesseract') is not None

def _poppler_available() -> bool:
    return shutil.which('pdftoppm') is not None


# ── Text extraction ───────────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    # 1. Try direct text extraction (works for digital PDFs)
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
    except Exception as e:
        print(f"PyPDF2 error: {e}")

    # 2. OCR fallback for scanned PDFs
    if not text.strip():
        if not _tesseract_available():
            return "[Scanned PDF detected. Install Tesseract for OCR: brew install tesseract poppler]"
        if not _poppler_available():
            return "[Scanned PDF detected. Install poppler for OCR: brew install poppler]"
        try:
            import pytesseract
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        except Exception as e:
            print(f"OCR error: {e}")
            return f"[OCR failed: {e}]"

    return text.strip()


# ── Field extractors ──────────────────────────────────────────────────────────
def extract_email(text: str) -> str:
    m = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    return m.group(0) if m else ""

def extract_phone(text: str) -> str:
    m = re.search(r'(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    return m.group(0).strip() if m else ""

def extract_experience(text: str) -> int:
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?experience',
        r'experience\s*[:\-]?\s*(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:work|industry|professional)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return 0

def extract_skills(text: str) -> List[str]:
    """Return deduplicated list of matched EV skills."""
    text_lower = text.lower()
    seen = set()
    found = []
    for skill in EV_SKILLS:
        key = skill.lower()
        if key not in seen and key in text_lower:
            seen.add(key)
            found.append(skill)
    return found

def extract_education(text: str) -> List[str]:
    keywords = [
        'Bachelor', 'Master', 'PhD', 'Ph.D', 'B.Tech', 'M.Tech',
        'B.E', 'M.E', 'B.Sc', 'M.Sc', 'BCA', 'MCA', 'Diploma', 'Doctorate',
    ]
    found = []
    for kw in keywords:
        idx = text.lower().find(kw.lower())
        if idx != -1:
            snippet = text[max(0, idx - 10): min(len(text), idx + 60)].strip()
            found.append(snippet)
    return found[:3]

def extract_name(text: str) -> str:
    doc = nlp(text[:800])
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.start_char < 300:
            parts = ent.text.split()
            if 2 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p):
                return ent.text
    # Fallback: first non-empty line that looks like a name
    for line in text.splitlines():
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and line.replace(' ', '').isalpha():
            return line
    return ""


# ── Main pipeline ─────────────────────────────────────────────────────────────
def parse_resume(pdf_path: str) -> Dict:
    text = extract_text_from_pdf(pdf_path)

    if not text.strip() or text.startswith('['):
        return {
            "success": False,
            "error": text or "Could not extract text from PDF",
        }

    return {
        "success":    True,
        "text":       text[:3000],
        "full_text":  text,
        "name":       extract_name(text),
        "email":      extract_email(text),
        "phone":      extract_phone(text),
        "experience": extract_experience(text),
        "skills":     extract_skills(text),
        "education":  extract_education(text),
        "ocr_used":   not bool(text) or '[OCR' in text,
    }
