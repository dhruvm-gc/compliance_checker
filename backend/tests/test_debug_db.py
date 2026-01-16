from app.vectordb import debug_db

def test_debug_db(monkeypatch):
    class FakeCollection:
        def count(self):
            return 12

    class FakeDB:
        _collection = FakeCollection()

    monkeypatch.setattr(debug_db, "get_chroma", lambda: FakeDB())
    resp = debug_db.debug_db()

    assert resp["count"] == 12
