from typing import List
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain.text_splitter import RecursiveCharacterTextSplitter


def chunk_text(text: str, CHUNK_SIZE: int, CHUNK_OVERLAP: int) -> List[str]:
    """Chia nhỏ text thành chunks hợp lý"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.split_text(text)









