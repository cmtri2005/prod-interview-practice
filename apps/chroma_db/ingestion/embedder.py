from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

def build_embedder(model_name: str = "all-MiniLM-L6-v2"):
    """
    Trả về một embedding function dùng SentenceTransformer cho Chroma.
    Mặc định là all-MiniLM-L6-v2.
    """
    return SentenceTransformerEmbeddingFunction(model_name=model_name)
 