"""
Input validation utilities
"""

import re
import hashlib
from typing import Tuple, Optional
from app.config.settings import settings
from app.config.constants import EXPECTED_MIME, FAKE_EMAIL_PATTERNS, FAKE_PHONE_PATTERNS

try:
    import magic as _magic
    _MAGIC_AVAILABLE = True
except ImportError:
    _magic = None
    _MAGIC_AVAILABLE = False


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    
    # Check for fake emails
    email_lower = email.lower()
    for fake in FAKE_EMAIL_PATTERNS:
        if fake in email_lower:
            return False
    
    return True


def validate_phone(phone: str) -> bool:
    """Validate phone format"""
    if not phone:
        return False
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Check length
    if not (10 <= len(digits) <= 15):
        return False
    
    # Check for fake patterns
    if digits in FAKE_PHONE_PATTERNS:
        return False
    
    return True


def validate_file_size(file_bytes: bytes) -> Tuple[bool, Optional[str]]:
    """Validate file size"""
    size = len(file_bytes)
    
    if size == 0:
        return False, "File is empty"
    
    if size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        actual_mb = size // (1024 * 1024)
        return False, f"File exceeds {max_mb}MB limit ({actual_mb}MB)"
    
    return True, None


def validate_file_signature(file_bytes: bytes, extension: str) -> Tuple[bool, Optional[str]]:
    """
    Validate file signature matches extension
    Security check to prevent malicious files
    """
    if not _MAGIC_AVAILABLE:
        # Skip MIME check if python-magic not installed
        return True, None
    
    try:
        mime = _magic.Magic(mime=True)
        detected_mime = mime.from_buffer(file_bytes)
    except Exception as e:
        return False, f"Could not determine file type: {str(e)}"
    
    expected = EXPECTED_MIME.get(extension, set())
    if detected_mime not in expected:
        return False, f"File type mismatch: extension is .{extension} but file is {detected_mime}"
    
    # Check for executable headers
    if len(file_bytes) >= 4:
        header = file_bytes[:4]
        
        # Windows executable (MZ)
        if header[:2] == b"MZ":
            return False, "Security check failed: file appears to be a Windows executable"
        
        # Linux executable (ELF)
        if header[:4] == b"\x7fELF":
            return False, "Security check failed: file appears to be a Linux executable"
    
    return True, None


def compute_file_hash(file_bytes: bytes) -> str:
    """Compute SHA256 hash of file"""
    return hashlib.sha256(file_bytes).hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def validate_job_description(jd: str) -> Tuple[bool, Optional[str]]:
    """Validate job description"""
    if not jd or not jd.strip():
        return False, "Job description is required"
    
    if len(jd.strip()) < 50:
        return False, "Job description is too short (minimum 50 characters)"
    
    if len(jd) > 10000:
        return False, "Job description is too long (maximum 10,000 characters)"
    
    return True, None
