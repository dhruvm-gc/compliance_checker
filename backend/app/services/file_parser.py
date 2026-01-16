from pathlib import Path
from pypdf import PdfReader
import docx

from app.exceptions import FileParseError

def read_pdf(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts).strip()
    except Exception as e:
        raise FileParseError(f"Failed to parse PDF: {path.name}. Reason: {e}")

def read_docx(path: Path) -> str:
    try:
        d = docx.Document(str(path))
        return "\n".join([p.text for p in d.paragraphs if p.text.strip()]).strip()
    except Exception as e:
        raise FileParseError(f"Failed to parse DOCX: {path.name}. Reason: {e}")

def parse_uploaded_file(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return read_pdf(path)
    if ext == ".docx":
        return read_docx(path)
    raise FileParseError("Unsupported file type. Only PDF and DOCX are supported.")
