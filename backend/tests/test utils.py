from app.utils import split_into_clauses


def test_split_into_clauses_numbered():
    text = "1. Hello\n2. World\n3. Test"
    clauses = split_into_clauses(text)
    assert len(clauses) == 3


def test_split_into_clauses_paragraph_fallback():
    text = "This is a paragraph.\n\nThis is another paragraph."
    clauses = split_into_clauses(text)
    assert len(clauses) >= 1
