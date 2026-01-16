from pathlib import Path
from app.vectordb import export_vectors


def test_export_vectors(monkeypatch, tmp_path):
    class FakeCollection:
        def get(self, limit=None, include=None):
            return {
                "ids": ["1"],
                "documents": ["doc text"],
                "metadatas": [{"source": "reg.pdf"}],
                "embeddings": [[0.1, 0.2, 0.3]]
            }

    class FakeDB:
        _collection = FakeCollection()

    monkeypatch.setattr(export_vectors, "get_chroma", lambda: FakeDB())

    # ✅ Patch EXPORT_PATH as Path object (not string)
    monkeypatch.setattr(export_vectors, "EXPORT_PATH", Path(tmp_path / "export.json"))

    out = export_vectors.export_vectors(limit=5, show_values=2)

    assert out["exported"] == 1
    assert out["file"].endswith(".json")
