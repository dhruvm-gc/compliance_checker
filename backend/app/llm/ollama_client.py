from langchain_ollama import ChatOllama, OllamaEmbeddings

# ✅ Fast config
LLM_MODEL = "llama3"
EMBED_MODEL = "nomic-embed-text"

def get_llm():
    # ✅ Keep temperature low for consistent JSON
    return ChatOllama(model=LLM_MODEL, temperature=0)

def get_embeddings():
    # ✅ Must be embedding model (fast)
    return OllamaEmbeddings(model=EMBED_MODEL)
