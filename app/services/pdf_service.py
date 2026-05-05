"""
Hybrid PDF Parser - Combines all three parsing methods
Handles digital PDFs, scanned PDFs, and corrupted files
"""

import io
import re
import shutil
from typing import Dict, Optional, Tuple
from io import BytesIO

# Method 1: pdfplumber (from main)
import pdfplumber

# Method 2: PyPDF2 + OCR (from ev-hiring)
import PyPDF2

# Method 3: pdfminer3 (from shashwat)
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer3.pdfpage import PDFPage

# OCR support
try:
    import pytesseract
    from pdf2image import convert_from_path, convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from app.config.settings import settings


class HybridPDFParser:
    """
    Three-method PDF parser with automatic fallback:
    1. pdfplumber (best for tables and structured PDFs)
    2. PyPDF2 (fast, good for simple PDFs)
    3. pdfminer3 (best for complex layouts)
    4. OCR (fallback for scanned PDFs)
    """
    
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE and self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is installed"""
        return shutil.which('tesseract') is not None
    
    def parse_pdfplumber(self, file_bytes: bytes) -> Tuple[str, bool]:
        """
        Method 1: pdfplumber (from main branch)
        Best for: Tables, structured documents
        """
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
                text = "\n".join(pages).strip()
                
                if len(text) > 100:  # Minimum viable text
                    return text, True
                
                return text, False
        except Exception as e:
            print(f"pdfplumber error: {e}")
            return "", False
    
    def parse_pypdf2(self, file_bytes: bytes) -> Tuple[str, bool]:
        """
        Method 2: PyPDF2 (from ev-hiring branch)
        Best for: Simple PDFs, fast extraction
        """
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            text = ""
            
            for page in reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            
            text = text.strip()
            
            if len(text) > 100:
                return text, True
            
            return text, False
        except Exception as e:
            print(f"PyPDF2 error: {e}")
            return "", False
    
    def parse_pdfminer(self, file_bytes: bytes) -> Tuple[str, bool]:
        """
        Method 3: pdfminer3 (from shashwat branch)
        Best for: Complex layouts, academic papers
        """
        try:
            resource_manager = PDFResourceManager()
            output = io.StringIO()
            converter = TextConverter(resource_manager, output, laparams=LAParams())
            interpreter = PDFPageInterpreter(resource_manager, converter)
            
            pdf_file = BytesIO(file_bytes)
            
            for page in PDFPage.get_pages(pdf_file, caching=True, check_extractable=True):
                interpreter.process_page(page)
            
            text = output.getvalue()
            converter.close()
            output.close()
            
            if len(text) > 100:
                return text, True
            
            return text, False
        except Exception as e:
            print(f"pdfminer3 error: {e}")
            return "", False
    
    def parse_ocr(self, file_bytes: bytes, file_path: Optional[str] = None) -> Tuple[str, bool]:
        """
        Method 4: OCR fallback (from ev-hiring + shashwat)
        Best for: Scanned PDFs, images
        """
        if not self.ocr_available:
            return "[OCR not available. Install: brew install tesseract poppler]", False
        
        try:
            # Convert PDF to images
            if file_path:
                images = convert_from_path(
                    file_path,
                    dpi=settings.OCR_DPI
                )
            else:
                images = convert_from_bytes(
                    file_bytes,
                    dpi=settings.OCR_DPI
                )
            
            ocr_texts = []
            confident_words = 0
            total_words = 0
            
            for img in images:
                try:
                    # Get OCR with confidence scores
                    data = pytesseract.image_to_data(
                        img,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    page_text = []
                    for word, conf in zip(data["text"], data["conf"]):
                        if conf >= settings.OCR_CONFIDENCE_THRESHOLD:
                            page_text.append(word)
                            confident_words += 1
                        total_words += 1
                    
                    if page_text:
                        ocr_texts.append(" ".join(page_text))
                
                except Exception:
                    # Fallback to simple OCR
                    try:
                        page_text = pytesseract.image_to_string(img, config="--psm 6")
                        if page_text.strip():
                            ocr_texts.append(page_text)
                    except Exception:
                        continue
            
            combined = "\n".join(ocr_texts).strip()
            
            if len(combined) >= settings.OCR_MIN_TEXT_LENGTH:
                return combined, True
            
            return combined, False
        
        except Exception as e:
            print(f"OCR error: {e}")
            return f"[OCR failed: {e}]", False
    
    def parse(
        self,
        file_bytes: bytes,
        file_path: Optional[str] = None,
        prefer_ocr: bool = False
    ) -> Dict:
        """
        Main parsing method with automatic fallback
        
        Args:
            file_bytes: PDF file as bytes
            file_path: Optional file path (for OCR)
            prefer_ocr: Force OCR even if text extraction works
        
        Returns:
            {
                "text": Extracted text,
                "success": Boolean,
                "method": Method used,
                "is_ocr": Whether OCR was used,
                "error": Error message if failed
            }
        """
        if prefer_ocr and self.ocr_available:
            text, success = self.parse_ocr(file_bytes, file_path)
            if success:
                return {
                    "text": text,
                    "success": True,
                    "method": "ocr",
                    "is_ocr": True,
                    "error": None
                }
        
        # Try all three methods in order
        methods = [
            ("pdfplumber", self.parse_pdfplumber),
            ("pypdf2", self.parse_pypdf2),
            ("pdfminer3", self.parse_pdfminer),
        ]
        
        for method_name, method_func in methods:
            text, success = method_func(file_bytes)
            
            if success:
                return {
                    "text": text,
                    "success": True,
                    "method": method_name,
                    "is_ocr": False,
                    "error": None
                }
        
        # All methods failed - try OCR as last resort
        if self.ocr_available:
            text, success = self.parse_ocr(file_bytes, file_path)
            
            if success:
                return {
                    "text": text,
                    "success": True,
                    "method": "ocr",
                    "is_ocr": True,
                    "error": None
                }
            
            return {
                "text": text,
                "success": False,
                "method": "ocr",
                "is_ocr": True,
                "error": "OCR extraction failed or insufficient text"
            }
        
        return {
            "text": "",
            "success": False,
            "method": "none",
            "is_ocr": False,
            "error": "All parsing methods failed. PDF may be corrupted or encrypted."
        }
    
    def extract_metadata(self, file_bytes: bytes) -> Dict:
        """Extract PDF metadata"""
        try:
            reader = PyPDF2.PdfReader(BytesIO(file_bytes))
            metadata = reader.metadata
            
            return {
                "pages": len(reader.pages),
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "encrypted": reader.is_encrypted,
            }
        except Exception:
            return {"pages": 0, "encrypted": False}


# Singleton instance
_parser = None

def get_pdf_parser() -> HybridPDFParser:
    """Get or create singleton PDF parser"""
    global _parser
    if _parser is None:
        _parser = HybridPDFParser()
    return _parser
