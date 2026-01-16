from app.vectordb.chroma_client import get_chroma

def get_similar_rules(query: str, top_k: int = 2, max_chars: int = 350):
    db = get_chroma()
    docs = db.similarity_search(query, k=top_k)

    cleaned = []
    for d in docs:
        text = (d.page_content or "").strip().replace("\n", " ")
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        cleaned.append(text)

    return cleaned
