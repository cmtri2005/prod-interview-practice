import uuid
import yaml
from service.vectorstores.chroma_store import ChromaStore
from postgres.postgres import SessionLocal, Document
from service.ingestion.embedder import build_embedder 
from service.ingestion.chunk import chunk_text


class ChromaCollectionManager:
    def __init__(self,  collection_name: str = None):
        self.config_path =  "./configs/config.yml"
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f)

        # build local embedder
        embed_cfg = self.cfg["embeddings"]
        
        self.embedder = build_embedder(model_name=embed_cfg["model_name"])

        # init chroma store
        chroma_cfg = self.cfg["chroma"]
        col_name = collection_name or chroma_cfg["collection_name"]

        collection_name = self.cfg["chroma"]["collection_name"]
        self.collection_name = collection_name
        self.store = ChromaStore(
            client_settings=chroma_cfg["client_settings"],
            collection_name=col_name
        )

    def add_documents(self, ids, documents, metadatas=None, collection_name=None):
        vectors = self.embedder(documents)
     
        
        vectors1 = [e.tolist() for e in vectors]
        collection_name =  self.collection_name
    
        # add to Chroma
        self.store.add(
            ids=ids if self.cfg['chroma']['save_ids'] else None,
            documents=documents if self.cfg['chroma']['save_documents'] else None,
            embeddings=vectors1,
            metadatas=metadatas if self.cfg['chroma']['save_metadata'] else None
        )
        # sync Postgres
        sess = SessionLocal()
        for _id, doc, meta in zip(ids, documents, metadatas):
            db_obj = Document(
                id=_id,
                collection=collection_name,
                content=doc,
                meta=meta
            )
            sess.merge(db_obj)
        sess.commit()
        sess.close()

    def add_embeddings(self, ids, embeddings, documents, metadatas=None, collection_name=None):

        collection_name =  self.collection_name
      
        # add to Chroma
        self.store.add(
            ids=ids if self.cfg['chroma']['save_ids'] else None,
            documents=documents,
            embeddings=embeddings[0],
            metadatas=metadatas if self.cfg['chroma']['save_metadata'] else None
        )
        # sync Postgres
        sess = SessionLocal()
        try:
            for _id, doc, meta in zip(ids, documents, metadatas):
                db_obj = Document(
                    id=_id,
                    collection=collection_name,
                    content=doc,
                    meta=meta
                )
                sess.merge(db_obj)

            sess.commit()
        except Exception as e:
            sess.rollback()
            print("Postgres error:", e)
        finally:
            sess.close()
            
    def add_file(self, ids, document, metadatas=None, collection_name=None):
        
        CHUNK_SIZE = self.cfg['text_splitter']['chunk_size']
        CHUNK_OVERLAP = self.cfg['text_splitter']['chunk_overlap']
        documents = chunk_text(document, CHUNK_SIZE=CHUNK_SIZE, CHUNK_OVERLAP=CHUNK_OVERLAP)
        vectors = self.embedder(documents)
        vectors1 = [e.tolist() for e in vectors]
        
        collection_name =  self.collection_name
        
        
        ids = [str(uuid.uuid4()) for _ in vectors1]
        metadatas = [metadatas for _ in vectors1]
        
        
        self.store.add(
            ids=ids if self.cfg['chroma']['save_ids'] else None,
            documents=documents if self.cfg['chroma']['save_documents'] else None,
            embeddings=vectors1,
            metadatas=metadatas if self.cfg['chroma']['save_metadata'] else None
        )
        # sync Postgres
        sess = SessionLocal()
        for _id, doc, meta in zip(ids, documents, metadatas):
            db_obj = Document(
                id=_id,
                collection=collection_name,
                content=doc,
                meta=meta
            )
            sess.merge(db_obj)
        sess.commit()
        sess.close()


    def reset_collection(self, ids=None, embeddings=None, documents=None, metadatas=None, collection_name=None):
        
        all_data = self.store.collection.get()
        self.store.collection.delete(ids=all_data["ids"])
        
        session = SessionLocal()
        try:
            deleted = session.query(Document).delete()
            session.commit()
            print(f"Reset {deleted} DB")
        except Exception as e:
            session.rollback()
            print("Postgres error:", e)
        finally:
            session.close()

    def query(self, text, top_k=None):
        if top_k is None:
            top_k = self.cfg['retrieval']['top_k']
        q_emb = self.embedder.encode([text])[0]
        return self.store.similarity_search(query_embedding=q_emb, top_k=top_k)
