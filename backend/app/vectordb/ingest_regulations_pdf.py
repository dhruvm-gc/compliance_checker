from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.vectordb.chroma_client import get_chroma
from app.services.file_parser import read_pdf

def ingest_regulations_pdf(pdf_path: str, reset: bool = False, max_chunks: int = 300, batch_size: int = 50):
    db = get_chroma()

    if reset:
        try:
            db._collection.delete(where={})
        except Exception:
            pass

    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(pdf_path)

    text = read_pdf(path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_text(text)

    if len(chunks) > max_chunks:
        chunks = chunks[:max_chunks]

    docs = [
        Document(page_content=c, metadata={"source": path.name, "chunk_id": i})
        for i, c in enumerate(chunks) if c.strip()
    ]

    for i in range(0, len(docs), batch_size):
        db.add_documents(docs[i:i+batch_size])

    return {
        "message": "Embedded regulations",
        "chunks_ingested": len(docs),
        "collection_count": db._collection.count(),
        "source": path.name
    }
