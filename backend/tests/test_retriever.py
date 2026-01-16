from app.vectordb import retriever

def test_get_similar_rules(monkeypatch):
    class FakeDoc:
        def __init__(self, content):
            self.page_content = content

    class FakeDB:
        def similarity_search(self, query, k=2):
            return [
                FakeDoc("A"*500),
                FakeDoc("Short rule")
            ]

    monkeypatch.setattr(retriever, "get_chroma", lambda: FakeDB())

    rules = retriever.get_similar_rules("test clause", top_k=2, max_chars=100)
    assert len(rules) == 2
    assert rules[0].endswith("...")
    assert rules[1] == "Short rule"
