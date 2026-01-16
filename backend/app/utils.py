import re
from typing import List

# Keywords common in real clauses
CLAUSE_KEYWORDS = [
    "shall", "must", "will", "may", "agree", "provider", "customer",
    "data", "security", "audit", "retention", "delete", "access", "mfa",
    "encryption", "logs", "breach", "consent"
]

def looks_like_heading(text: str) -> bool:
    """
    Heuristic to detect titles/headings that are not clauses.
    """
    t = text.strip()

    # Very short line, likely heading
    if len(t) < 60:
        return True

    # Title Case (many words capitalized) and no clause punctuation
    words = t.split()
    cap_ratio = sum(1 for w in words if w[:1].isupper()) / max(len(words), 1)

    if cap_ratio > 0.7 and "." not in t and ":" not in t:
        return True

    # If no key compliance keywords at all, likely heading
    lower = t.lower()
    if not any(k in lower for k in CLAUSE_KEYWORDS):
        return True

    return False


def split_into_clauses(text: str) -> List[str]:
    """
    Split contract text into clauses using numbering patterns.
    Removes document headings/titles automatically.
    """
    # Normalize
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Insert newline before numbered patterns if PDF has everything in one line
    text = re.sub(r"(\s)(\d+(?:\.\d+)*[\).\:]?)\s+", r"\n\2 ", text)

    # Detect clause starts: 1., 1), 1:, Clause 1:, 1.1 etc
    pattern = r"(?=\n?\s*(?:Clause\s+)?\d+(?:\.\d+)*[\).\-\:]?\s+)"

    parts = re.split(pattern, text)

    clauses = []
    for p in parts:
        p = p.strip()

        # discard tiny chunks
        if len(p) < 30:
            continue

        # discard headings/titles
        if looks_like_heading(p):
            continue

        clauses.append(p)

    # Fallback: paragraph split (still remove headings)
    if not clauses:
        paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
        clauses = [p for p in paras if not looks_like_heading(p)]

    return clauses
