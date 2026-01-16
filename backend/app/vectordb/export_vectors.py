import json
from pathlib import Path
from app.vectordb.chroma_client import get_chroma

EXPORT_PATH = Path("backend/app/data/exported_vectors.json")


def export_vectors(limit: int = 50, show_values: int = 30):
    """
    Exports the embedded vectors from ChromaDB into a JSON file so you can see them.

    limit: how many records to export
    show_values: how many values of the embedding vector to show (to keep file small)
    """
    db = get_chroma()

    data = db._collection.get(
        limit=limit,
        include=["documents", "metadatas", "embeddings"]
    )

    docs = data.get("documents", [])
    metas = data.get("metadatas", [])
    embs = data.get("embeddings", [])

    export_data = []

    for i in range(len(docs)):
        vec = embs[i] if i < len(embs) else None

        export_data.append({
            "document": docs[i],
            "metadata": metas[i],
            "embedding_vector_length": len(vec) if vec is not None else 0,
            "embedding_vector_first_values": (
                vec[:show_values].tolist()
                if vec is not None and hasattr(vec, "tolist")
                else (vec[:show_values] if vec is not None else [])
            )
        })


    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2)

    return {"exported": len(export_data), "file": str(EXPORT_PATH)}
