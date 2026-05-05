#!/usr/bin/env python3
"""
Installation Test Script
Verifies that all dependencies are installed correctly
"""

import sys
from typing import List, Tuple

def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all required imports"""
    results = []
    
    # Core dependencies
    tests = [
        ("FastAPI", "fastapi", "Web framework"),
        ("Uvicorn", "uvicorn", "ASGI server"),
        ("Pydantic", "pydantic", "Data validation"),
        
        # PDF parsing
        ("pdfplumber", "pdfplumber", "PDF parsing method 1"),
        ("PyPDF2", "PyPDF2", "PDF parsing method 2"),
        ("pdfminer3", "pdfminer3", "PDF parsing method 3"),
        
        # OCR
        ("pytesseract", "pytesseract", "OCR support"),
        ("pdf2image", "pdf2image", "PDF to image conversion"),
        ("PIL", "PIL", "Image processing"),
        
        # NLP & ML
        ("spacy", "spacy", "NLP library"),
        ("sklearn", "sklearn", "Machine learning"),
        
        # AI
        ("google.generativeai", "google.generativeai", "Gemini AI"),
        
        # Database
        ("aiosqlite", "aiosqlite", "Async SQLite"),
        ("sqlalchemy", "sqlalchemy", "ORM"),
        
        # Security
        ("magic", "magic", "File type detection"),
        
        # Document processing
        ("mammoth", "mammoth", "DOCX parsing"),
        
        # Utilities
        ("dotenv", "dotenv", "Environment variables"),
    ]
    
    for name, module, description in tests:
        try:
            __import__(module)
            results.append((name, True, description))
        except ImportError as e:
            results.append((name, False, f"{description} - {str(e)}"))
    
    return results


def test_spacy_model() -> Tuple[bool, str]:
    """Test if spaCy model is downloaded"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        return True, "spaCy model 'en_core_web_sm' loaded successfully"
    except Exception as e:
        return False, f"spaCy model not found: {str(e)}"


def test_tesseract() -> Tuple[bool, str]:
    """Test if Tesseract is installed"""
    import shutil
    if shutil.which('tesseract'):
        return True, "Tesseract OCR found"
    else:
        return False, "Tesseract not found. Install: brew install tesseract (macOS) or sudo apt-get install tesseract-ocr (Ubuntu)"


def test_poppler() -> Tuple[bool, str]:
    """Test if Poppler is installed"""
    import shutil
    if shutil.which('pdftoppm'):
        return True, "Poppler found"
    else:
        return False, "Poppler not found. Install: brew install poppler (macOS) or sudo apt-get install poppler-utils (Ubuntu)"


def main():
    print("=" * 70)
    print("AntiGravity God-Level Backend - Installation Test")
    print("=" * 70)
    print()
    
    # Test Python version
    print("Python Version:")
    print(f"  {sys.version}")
    if sys.version_info < (3, 9):
        print("  ⚠️  WARNING: Python 3.9+ recommended")
    else:
        print("  ✅ OK")
    print()
    
    # Test imports
    print("Testing Python Dependencies:")
    print("-" * 70)
    results = test_imports()
    
    success_count = 0
    fail_count = 0
    
    for name, success, description in results:
        status = "✅" if success else "❌"
        print(f"  {status} {name:25} - {description}")
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    print()
    print(f"Results: {success_count} passed, {fail_count} failed")
    print()
    
    # Test spaCy model
    print("Testing spaCy Model:")
    print("-" * 70)
    success, message = test_spacy_model()
    status = "✅" if success else "❌"
    print(f"  {status} {message}")
    if not success:
        print("  Fix: python -m spacy download en_core_web_sm")
    print()
    
    # Test system dependencies
    print("Testing System Dependencies:")
    print("-" * 70)
    
    tesseract_ok, tesseract_msg = test_tesseract()
    status = "✅" if tesseract_ok else "❌"
    print(f"  {status} {tesseract_msg}")
    
    poppler_ok, poppler_msg = test_poppler()
    status = "✅" if poppler_ok else "❌"
    print(f"  {status} {poppler_msg}")
    print()
    
    # Final summary
    print("=" * 70)
    all_ok = (fail_count == 0 and success and tesseract_ok and poppler_ok)
    
    if all_ok:
        print("✅ All tests passed! You're ready to run the backend.")
        print()
        print("Next steps:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your GEMINI_API_KEY to .env")
        print("  3. Run: python -m app.main")
        print("  4. Visit: http://localhost:8000/docs")
        return 0
    else:
        print("❌ Some tests failed. Please install missing dependencies.")
        print()
        print("Quick fix:")
        if fail_count > 0:
            print("  pip install -r requirements/dev.txt")
        if not success:
            print("  python -m spacy download en_core_web_sm")
        if not tesseract_ok:
            print("  brew install tesseract  # macOS")
            print("  # or: sudo apt-get install tesseract-ocr  # Ubuntu")
        if not poppler_ok:
            print("  brew install poppler  # macOS")
            print("  # or: sudo apt-get install poppler-utils  # Ubuntu")
        return 1


if __name__ == "__main__":
    sys.exit(main())
