from app.vectordb.chroma_client import get_chroma


def debug_db():
    """
    Debug helper to view basic Chroma collection statistics.
    """
    db = get_chroma()
    try:
        count = db._collection.count()
    except Exception:
        count = 0

    return {
        "count": count,
        "collection_name": getattr(db, "collection_name", "regulations")
    }
