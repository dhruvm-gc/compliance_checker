from pathlib import Path
from app.vectordb import ingest_regulations_pdf

def test_ingest_regulations_pdf(monkeypatch, tmp_path: Path):
    fake_pdf = tmp_path / "reg.pdf"
    fake_pdf.write_text("dummy")

    # mock file_parser.read_pdf
    monkeypatch.setattr(ingest_regulations_pdf, "read_pdf", lambda _: "A long regulation text " * 200)

    # mock splitter
    class FakeSplitter:
        def __init__(self, chunk_size=None, chunk_overlap=None): pass
        def split_text(self, text):
            return ["chunk1", "chunk2", "chunk3"]

    monkeypatch.setattr(ingest_regulations_pdf, "RecursiveCharacterTextSplitter", FakeSplitter)

    # mock chroma db
    class FakeCollection:
        def __init__(self): self._count = 0
        def count(self): return 3

    class FakeDB:
        _collection = FakeCollection()
        def add_documents(self, docs): pass

    monkeypatch.setattr(ingest_regulations_pdf, "get_chroma", lambda: FakeDB())

    resp = ingest_regulations_pdf.ingest_regulations_pdf(str(fake_pdf), reset=False, max_chunks=10, batch_size=2)
    assert resp["chunks_ingested"] == 3
