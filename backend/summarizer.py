import re
import threading
from typing import Dict

# ── Background model loader ────────────────────────────────────────────────────
_summarizer = None
_summarizer_lock = threading.Lock()
_summarizer_ready = False

def _load_summarizer():
    global _summarizer, _summarizer_ready
    try:
        from transformers import pipeline
        with _summarizer_lock:
            # text2text-generation works with t5-small in newer transformers
            _summarizer = pipeline(
                "text2text-generation",
                model="t5-small",   # 60MB — loads in seconds
                device=-1,
            )
            _summarizer_ready = True
        print("✅ Summarizer (t5-small) loaded.")
    except Exception as e:
        print(f"⚠️  Summarizer failed to load: {e}")
        _summarizer_ready = False

def start_loading():
    threading.Thread(target=_load_summarizer, daemon=True).start()

def is_ready() -> bool:
    return _summarizer_ready


# ── Extractive fallback (zero dependencies, instant) ──────────────────────────
_SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'matlab', 'simulink', 'bms', 'battery',
    'powertrain', 'charging', 'embedded', 'can bus', 'autosar', 'adas',
    'lidar', 'radar', 'iso 26262', 'hil', 'sil', 'inverter', 'motor',
    'experience', 'engineer', 'developer', 'manager', 'lead',
]

def extractive_summary(text: str, num_sentences: int = 3) -> str:
    """Score sentences by keyword density and return the top ones."""
    # Normalise whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = [s.strip() for s in re.split(r'[.\n]', text) if len(s.strip()) > 20]

    scored = []
    for sent in sentences:
        lower = sent.lower()
        score = sum(1 for kw in _SKILL_KEYWORDS if kw in lower)
        scored.append((score, sent))

    scored.sort(reverse=True)
    top = [s for _, s in scored[:num_sentences] if s]
    summary = '. '.join(top)
    return (summary[:350] + '…') if len(summary) > 350 else summary


def summarize_resume(resume_text: str) -> str:
    """
    Return a summary of the resume.
    - If t5-small is loaded → use it (better quality)
    - Otherwise → instant extractive fallback (always works)
    """
    if not resume_text or len(resume_text) < 50:
        return resume_text or "No content available."

    # Always try extractive first as the fast path
    fallback = extractive_summary(resume_text)

    if not _summarizer_ready:
        return fallback

    try:
        with _summarizer_lock:
            prompt = "summarize: " + resume_text[:600]
            result = _summarizer(
                prompt,
                max_new_tokens=80,
                min_new_tokens=20,
                truncation=True,
            )
        return result[0].get('generated_text', fallback)
    except Exception as e:
        print(f"Summarizer inference error: {e}")
        return fallback


def generate_ev_specific_insights(resume_text: str, skills: list) -> Dict:
    """Detect EV domain expertise and experience level."""
    insights = {
        "ev_experience_level": "entry",
        "relevant_domains": [],
        "certifications": [],
    }

    domains = {
        "Battery":    ['battery', 'cell', 'li-ion', 'lithium', 'bms', 'thermal management', 'state of charge'],
        "Powertrain": ['motor', 'inverter', 'converter', 'powertrain', 'drive', 'traction', 'regenerative'],
        "Charging":   ['charging', 'charger', 'ccs', 'chademo', 'v2g', 'ocpp', 'iso 15118'],
        "Autonomy":   ['adas', 'autonomous', 'sensor fusion', 'lidar', 'radar', 'path planning'],
        "Telematics": ['telematics', 'fleet management', 'iot', 'cloud', 'mqtt', 'aws iot'],
        "Testing":    ['hil', 'sil', 'mil', 'dspace', 'validation', 'testing', 'labview'],
        "Software":   ['can bus', 'autosar', 'matlab', 'simulink', 'embedded c', 'iso 26262', 'aspice'],
    }

    text_lower = resume_text.lower()
    for domain, keywords in domains.items():
        if any(kw in text_lower for kw in keywords):
            insights["relevant_domains"].append(domain)

    n = len(insights["relevant_domains"])
    if n >= 4:
        insights["ev_experience_level"] = "senior"
    elif n >= 2:
        insights["ev_experience_level"] = "mid"

    # Detect certifications
    cert_keywords = ['iso 26262', 'aspice', 'autosar', 'pmp', 'six sigma', 'certified']
    insights["certifications"] = [kw for kw in cert_keywords if kw in text_lower]

    return insights
