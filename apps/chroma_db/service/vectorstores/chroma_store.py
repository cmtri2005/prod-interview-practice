from chromadb import PersistentClient
from threading import Lock
import yaml
import chromadb

class ChromaStore:
    _instance = None
    _lock = Lock()

    def __new__(cls,client_settings, collection_name = None):
        with cls._lock: 
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                
                if (collection_name is None):
                    with open('./configs/config_path', "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f)
                        collection_name = cfg["chroma"]["collection_name"]

                # Dùng PersistentClient cho local
                # persist_dir = client_settings.get("persist_directory", "./chroma_db")
                # cls._instance.client = PersistentClient(path=persist_dir)
                cls._instance.client = chromadb.HttpClient(host="localhost", port=8000)
            

                cls._instance.collection = cls._instance.client.get_or_create_collection(
                    name=collection_name
                )
        return cls._instance

    def add(self, ids, documents, embeddings, metadatas=None):

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def similarity_search(self, query_embedding, top_k=4):
        """
        Find top_k documents nearest to query_embedding.
        """
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return result
