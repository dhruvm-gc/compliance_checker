from pathlib import Path
import pytest

from app.services.file_parser import parse_uploaded_file
from app.exceptions import FileParseError

def test_parser_invalid_extension(tmp_path: Path):
    f = tmp_path / "bad.txt"
    f.write_text("hello")
    with pytest.raises(FileParseError):
        parse_uploaded_file(f)

def test_parse_pdf_mock(monkeypatch, tmp_path):
    # mock PdfReader
    class FakePage:
        def extract_text(self):
            return "Hello PDF"

    class FakeReader:
        pages = [FakePage(), FakePage()]

    def fake_pdfreader(_):
        return FakeReader()

    from app.services import file_parser
    monkeypatch.setattr(file_parser, "PdfReader", fake_pdfreader)

    f = tmp_path / "sample.pdf"
    f.write_text("dummy")  # existence

    txt = parse_uploaded_file(f)
    assert "Hello PDF" in txt

def test_parse_docx_mock(monkeypatch, tmp_path):
    class FakePara:
        def __init__(self, text): self.text = text

    class FakeDoc:
        paragraphs = [FakePara("One"), FakePara(""), FakePara("Two")]

    def fake_docx_document(_):
        return FakeDoc()

    from app.services import file_parser
    monkeypatch.setattr(file_parser.docx, "Document", fake_docx_document)

    f = tmp_path / "sample.docx"
    f.write_text("dummy")

    txt = parse_uploaded_file(f)
    assert "One" in txt and "Two" in txt
