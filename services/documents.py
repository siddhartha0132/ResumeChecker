import hashlib
import io
import os
import zipfile
from dataclasses import dataclass

import magic
import mammoth
import pytesseract
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer3.pdfpage import PDFPage
from pdf2image import convert_from_path

from PIL import Image


ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
PER_FILE_SIZE_LIMIT = 10 * 1024 * 1024  # 10MB per file
OCR_CONFIDENCE_THRESHOLD = 30
OCR_MIN_TEXT_LENGTH = 50

FAKE_NAMES = {
    "john doe", "jane doe", "test user", "fake user",
    "john smith", "jane smith", "test test", "demo user",
}


EXPECTED_MIME = {
    "pdf": {"application/pdf"},
    "txt": {"text/plain", "application/octet-stream"},
    "docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    },
}


@dataclass(frozen=True)
class ParsedDocument:
    filename: str
    extension: str
    text: str
    file_hash: str = ""
    error: str = ""
    warning: str = ""
    is_ocr: bool = False

    @property
    def is_valid(self):
        return bool(self.text.strip()) and not self.error

    @property
    def is_suspicious(self):
        return bool(self.warning)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_file_signature(path, extension):
    """
    Validate that the file's real MIME type matches its extension.
    Also checks for executable magic bytes.
    Returns (is_valid, error_message).
    """
    try:
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_file(path)
    except Exception:
        return False, "Could not determine file type"

    expected = EXPECTED_MIME.get(extension, set())
    if detected_mime not in expected:
        return False, f"File type mismatch: extension is .{extension} but file is {detected_mime}"

    with open(path, "rb") as f:
        header = f.read(4)

    if header[:2] == b"MZ":
        return False, "Security check failed: file appears to be a Windows executable"
    if header[:4] == b"\x7fELF":
        return False, "Security check failed: file appears to be a Linux executable"

    if extension == "docx":
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = zf.namelist()
                if "[Content_Types].xml" not in names:
                    return False, "Invalid .docx file: missing [Content_Types].xml"
                if not any("word/" in n for n in names):
                    return False, "Invalid .docx file: missing word document content"
        except zipfile.BadZipFile:
            return False, "Invalid .docx file: not a valid ZIP archive"

    return True, ""


def check_file_size(path):
    size = os.path.getsize(path)
    if size > PER_FILE_SIZE_LIMIT:
        return False, f"File exceeds {PER_FILE_SIZE_LIMIT // (1024 * 1024)}MB limit ({size // (1024*1024)}MB)"
    if size == 0:
        return False, "File is empty"
    return True, ""


def extract_text_from_pdf(path):
    resource_manager = PDFResourceManager()
    output = io.StringIO()
    converter = TextConverter(resource_manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, converter)

    try:
        with open(path, "rb") as file:
            for page in PDFPage.get_pages(file, caching=True, check_extractable=True):
                interpreter.process_page(page)
        text = output.getvalue()
    finally:
        converter.close()
        output.close()

    if len(text.strip()) < OCR_MIN_TEXT_LENGTH:
        text = _ocr_pdf(path)

    return text


def _ocr_pdf(path):
    try:
        images = convert_from_path(path, dpi=200)
    except Exception as exc:
        return ""

    ocr_texts = []
    confident_words = 0
    total_words = 0

    for img in images:
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            page_text = []
            for word, conf in zip(data["text"], data["conf"]):
                if conf >= OCR_CONFIDENCE_THRESHOLD:
                    page_text.append(word)
                    confident_words += 1
                total_words += 1
            if page_text:
                ocr_texts.append(" ".join(page_text))
        except Exception:
            try:
                page_text = pytesseract.image_to_string(img, config="--psm 6")
                if page_text.strip():
                    ocr_texts.append(page_text)
            except Exception:
                continue

    combined = "\n".join(ocr_texts).strip()
    if not combined:
        return ""

    return "<!-- OCR_EXTRACTED -->\n" + combined


def extract_text_from_docx(path):
    with open(path, "rb") as docx_file:
        result = mammoth.extract_raw_text(docx_file)
    return result.value


def extract_text_from_txt(path):
    encodings = ("utf-8", "utf-8-sig", "latin-1")
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", errors="ignore") as file:
        return file.read()


def extract_text_from_file(path, original_filename=None):
    filename = original_filename or os.path.basename(path)
    extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        return ParsedDocument(
            filename=filename, extension=extension, text="",
            error=f"Unsupported file type: .{extension}",
        )

    size_ok, size_err = check_file_size(path)
    if not size_ok:
        return ParsedDocument(filename=filename, extension=extension, text="", error=size_err)

    sig_ok, sig_err = validate_file_signature(path, extension)
    if not sig_ok:
        return ParsedDocument(filename=filename, extension=extension, text="", error=sig_err)

    file_hash = compute_sha256(path)

    try:
        if extension == "pdf":
            text = extract_text_from_pdf(path)
            is_ocr = "<!-- OCR_EXTRACTED -->" in text
            if is_ocr:
                text = text.replace("<!-- OCR_EXTRACTED -->\n", "")
        elif extension == "docx":
            text = extract_text_from_docx(path)
            is_ocr = False
        else:
            text = extract_text_from_txt(path)
            is_ocr = False
    except Exception as exc:
        return ParsedDocument(
            filename=filename, extension=extension, text="",
            file_hash=file_hash, error=f"Could not read file: {exc}",
        )

    if not text.strip():
        return ParsedDocument(
            filename=filename, extension=extension, text="",
            file_hash=file_hash, error="No readable text found",
        )

    return ParsedDocument(
        filename=filename, extension=extension,
        text=text, file_hash=file_hash,
        is_ocr=is_ocr,
    )
