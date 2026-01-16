from langchain_chroma import Chroma
from app.llm.ollama_client import get_embeddings

PERSIST_DIR = "chroma_store"
COLLECTION_NAME = "regulations"

def get_chroma():
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=get_embeddings()
    )
