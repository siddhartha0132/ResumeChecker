import csv
import os
import re

from services.documents import FAKE_NAMES


VISIONASTRAA_SKILLS = {
    "api design",
    "aws",
    "azure",
    "cloud computing",
    "css",
    "data engineering",
    "docker",
    "fastapi",
    "flask",
    "gcp",
    "git",
    "html",
    "javascript",
    "kubernetes",
    "llm",
    "machine learning",
    "microservices",
    "mongodb",
    "natural language processing",
    "nlp",
    "postgresql",
    "prompt engineering",
    "python",
    "react",
    "rest api",
    "sql",
    "tensorflow",
    "transformers",
    "typescript",
    "vector database",
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.\-]?)?(?:\(?\d{3}\)?[\s.\-]?)?\d{3}[\s.\-]?\d{4}(?:\s*(?:ext|extension|x)\.?\s*\d{1,5})?")
NOISE_NAME_WORDS = {
    "resume", "curriculum", "vitae", "profile", "summary",
    "experience", "education", "skills", "projects", "work",
    "history", "employment", "qualifications", "objective",
    "references", "address", "phone", "email", "contact",
    "linkedin", "github", "website", "portfolio", "career",
}

RESUME_SECTION_HEADERS = {
    "experience", "education", "skills", "work history",
    "employment", "qualifications", "projects", "certifications",
    "achievements", "accomplishments", "professional summary",
    "career objective", "technical skills", "core competencies",
}
RESUME_KEYWORDS = {
    "developed", "managed", "led", "created", "implemented",
    "engineer", "developer", "analyst", "architect", "designer",
    "university", "bachelor", "master", "gpa", "project", "team",
    "responsible", "achieved", "improved", "built", "designed",
    "programmed", "coded", "maintained", "deployed", "collaborated",
}
DATE_PATTERNS = re.compile(
    r"(?:19|20)\d{2}|"  # 19xx or 20xx
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s.,\-/]?\s*\d{4}|"  # Month YYYY
    r"\d{1,2}[\s./\-]\d{4}|"  # MM/YYYY or M/YYYY
    r"\d{4}[\s./\-]\d{1,2}[\s./\-]\d{1,2}"  # YYYY-MM-DD
)
FAKE_EMAIL_PATTERNS = {
    "test@test.com", "example@domain.com", "fake@fake.com",
    "123@456.com", "a@b.com", "test@example.com",
    "user@test.com", "demo@demo.com",
}
FAKE_PHONE_PATTERNS = {
    "123-456-7890", "111-111-1111", "000-000-0000",
    "555-555-5555", "1234567890", "1111111111",
    "(123) 456-7890", "(111) 111-1111", "(555) 555-5555",
}


def normalize_text(value):
    value = value.lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9+#.]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_skill(value):
    return normalize_text(value.replace("-", " ").replace("_", " "))


def load_skill_vocabulary(path):
    skills = set(VISIONASTRAA_SKILLS)
    if os.path.exists(path):
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                value = row[0].strip()
                if not value or value.lower() == "skill_name":
                    continue
                skills.add(normalize_skill(value))
    return sorted({skill for skill in skills if skill}, key=lambda item: (-len(item), item))


def extract_email(text):
    lowered = (text or "").lower()

    obf1 = re.sub(r"\[at\]|\(at\)", "@", lowered)
    obf2 = re.sub(r"\[dot\]|\(dot\)", ".", obf1)
    obf3 = re.sub(r"\s+at\s+", "@", obf2)
    obf4 = re.sub(r"\s+dot\s+", ".", obf3)
    obf_final = re.sub(r"\s+", "", obf4)

    matches = EMAIL_RE.findall(obf_final)
    if not matches:
        return ""

    for email in matches:
        local, domain = email.rsplit("@", 1)
        if any(skip in local for skip in {"noreply", "no-reply", "donotreply", "test", "fake"}):
            continue
        if any(skip in domain for skip in {"example.com", "test.com", "fake.com", "domain.com"}):
            continue
        return email

    return ""

    for email in matches:
        local, domain = email.rsplit("@", 1)
        if any(skip in local for skip in {"noreply", "no-reply", "donotreply", "test", "fake"}):
            continue
        if any(skip in domain for skip in {"example.com", "test.com", "fake.com", "domain.com"}):
            continue
        return email

    return ""


def extract_phone(text):
    matches = PHONE_RE.findall(text or "")
    cleaned = []
    for match in matches:
        digits = re.sub(r"\D", "", match)
        if 10 <= len(digits) <= 15:
            cleaned.append(match.strip())

    if not cleaned:
        return ""

    phone = cleaned[0]
    phone_no_ext = re.split(r"\s*(?:ext|extension|x)\.?\s*", phone, flags=re.IGNORECASE)[0]
    digits_only = re.sub(r"\D", "", phone_no_ext)

    fake_formatted = any(fake in phone for fake in {"123-456-7890", "111-111-1111", "000-000-0000", "(123) 456-7890"})
    fake_digits = digits_only in {"1234567890", "1111111111", "0000000000"}

    if fake_formatted or fake_digits:
        return ""

    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    if digits_only.startswith("1") and len(digits_only) == 11:
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    return phone_no_ext


def extract_name(text, fallback_filename=""):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    for line in lines[:15]:
        line = EMAIL_RE.sub("", line)
        line = PHONE_RE.sub("", line)
        line = re.sub(r"[^A-Za-z .'\-]", " ", line)
        line = re.sub(r"\s+", " ", line).strip(" -|.,")

        if not line or len(line) < 3:
            continue

        words = line.split()
        lowered = {word.lower().strip(".:-") for word in words}

        if lowered & NOISE_NAME_WORDS:
            continue
        if not (2 <= len(words) <= 5):
            continue
        if not all(word[:1].isupper() or word.isupper() for word in words if word):
            continue
        if any(char.isdigit() for char in line):
            continue
        if any(w.lower() in FAKE_NAMES for w in words):
            continue

        return line

    stem = os.path.splitext(os.path.basename(fallback_filename))[0]
    stem = re.sub(r"[_-]+", " ", stem)
    stem = re.sub(r"\b(resume|cv)\b", " ", stem, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", stem).strip().title() or "Unknown Candidate"


def extract_skills(text, vocabulary):
    normalized = normalize_text(text or "")
    found = []
    for skill in vocabulary:
        pattern = r"(?<![a-z0-9+#.])" + re.escape(skill) + r"(?![a-z0-9+#.])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))


def humanize_skill(skill):
    acronyms = {"api", "aws", "css", "docx", "gcp", "html", "jd", "llm", "nlp", "pdf", "sql", "ui"}
    return " ".join(part.upper() if part in acronyms else part.capitalize() for part in skill.split())


def is_resume_like(text, vocabulary):
    """
    Check if the text looks like a resume.
    Returns (is_resume, reasons) where reasons is a list of failure reasons.
    """
    reasons = []
    text_stripped = (text or "").strip()

    words = text_stripped.split()
    word_count = len(words)
    char_count = len(text_stripped)

    if word_count < 150 or char_count < 500:
        reasons.append(f"Content too short ({word_count} words, {char_count} chars, need 150+ words and 500+ chars)")

    text_lower = text_stripped.lower()
    section_count = sum(1 for header in RESUME_SECTION_HEADERS if header in text_lower)
    if section_count < 2:
        reasons.append(f"Only {section_count} resume section headers found (need at least 2)")

    date_count = len(DATE_PATTERNS.findall(text))
    if date_count < 2:
        reasons.append(f"Only {date_count} date patterns found (need at least 2)")

    skill_matches = extract_skills(text, vocabulary)
    resume_kw_count = sum(1 for kw in RESUME_KEYWORDS if kw in text_lower)

    if len(skill_matches) < 3 and resume_kw_count < 5:
        reasons.append(f"Only {len(skill_matches)} skills and {resume_kw_count} resume keywords found")

    lines = text_stripped.splitlines()
    if len(lines) < 10:
        reasons.append(f"Only {len(lines)} lines of text (resumes typically have 20+)")

    one_paragraph_ratio = max(len(max(text_stripped.split("\n\n"), key=len)), 1) / max(char_count, 1)
    if one_paragraph_ratio > 0.9:
        reasons.append("Text appears to be mostly one paragraph (not typical resume format)")

    return (len(reasons) == 0, reasons)


def validate_resume_plausibility(profile, text, vocabulary):
    """
    Check if the resume content appears plausible (not fake).
    Returns (warnings, red_flags) as separate lists.
    """
    warnings = []
    red_flags = []

    email = profile.get("email", "")
    phone = profile.get("phone", "")
    name = profile.get("name", "")
    skills = profile.get("skills", [])

    if not email or email == "Not found":
        warnings.append("No email address found")
    else:
        if any(fake in email.lower() for fake in {"test@", "example@", "fake@", "123@"}):
            red_flags.append(f"Fake email address detected: {email}")

    if not phone or phone == "Not found":
        warnings.append("No phone number found")
    else:
        digits_only = re.sub(r"\D", "", phone)
        if digits_only in FAKE_PHONE_PATTERNS:
            red_flags.append(f"Fake phone number detected: {phone}")

    if not name or name == "Unknown Candidate":
        warnings.append("Could not extract candidate name")
    else:
        name_lower = name.lower()
        if any(fake in name_lower for fake in FAKE_NAMES):
            red_flags.append(f"Suspicious name: {name}")
        if len(name.split()) < 2:
            warnings.append("Name appears incomplete (single word)")

    if not skills:
        warnings.append("No skills detected in resume")
    else:
        non_vocab_ratio = sum(1 for s in skills if s not in vocabulary) / max(len(skills), 1)
        if non_vocab_ratio > 0.6:
            red_flags.append(f"Over {int(non_vocab_ratio*100)}% of skills are not in vocabulary ({len(skills)} total)")
        if len(skills) > 50 and len(text.split()) < 500:
            red_flags.append("Skill dumping detected: many skills but little content")

    return warnings, red_flags


def extract_candidate_profile(text, filename, vocabulary):
    return {
        "name": extract_name(text, filename),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text, vocabulary),
    }
