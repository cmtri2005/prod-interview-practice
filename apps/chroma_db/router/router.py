from email.mime import text
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from schema.chroma_schema import DocumentIn, MetadataIn, QueryIn, EmbeddingIn
from service.vectorstores.chroma_store import ChromaStore
from service.manage_collection import ChromaCollectionManager
import uuid
from service.ingestion.extract_text_from_file import extract_text_from_file
import json
from typing import List

router = APIRouter(prefix="/chroma")

manager = ChromaCollectionManager()
manager.store = ChromaStore(
    client_settings=manager.cfg['chroma']['client_settings']
)

@router.post("/add_text_to_collection")
def add_text_to_collection(
    docs: List[DocumentIn],
    metadatas: List[MetadataIn]
):

    ids = [str(uuid.uuid4()) for _ in docs]
    contents = [d.query_text for d in docs]
    metas = [m.dict() for m in metadatas]
    
    print (ids, contents, metas)
    manager.add_documents(ids, contents, metadatas=metas)

    return {
        "status": "success",
        "num": len(docs),
        "metadatas": metas
    }
    
@router.post("/add_embedding_to_collection")
def add_embedding_to_collection(
    embeddings: List[EmbeddingIn],
    metadatas: List[MetadataIn]
):

    ids = [str(uuid.uuid4()) for _ in embeddings]
    docs = ["## add by embedding ##" for d in embeddings]
    embeddings = [e.array for e in embeddings]
    metas = [m.dict() for m in metadatas]
    
    manager.add_embeddings(ids, embeddings, docs, metadatas=metas)
    return {
        "status": "success",
        "metadatas": metas
    }

@router.post("/add_file_to_collection")
def add_file_to_collection(
    metadatas: str = Form(...), ## error 400: FastAPI không hỗ trợ UploadFile trong body JSON (basemodel)
    file: UploadFile = File(...)
):



    contents = extract_text_from_file(file)
    ids = [str(uuid.uuid4())]
    metas = [m for m in json.loads(metadatas)]
    # print (ids, contents, metas)
    # add vào DB
    manager.add_file(ids, contents, metadatas=metas)
    return {
        "status": "success",
        "file": file.filename,
        "metadatas": metas
    }

@router.post("/search")
def search(query: QueryIn):
    """
    Semantic search trong Chroma collection.
    """
    result = manager.query(query.query, top_k=query.top_k)
    return {"matches": result}

@router.post("/reset_collection")
def reset_collection():
    """
    Delete data in "knowledge" collection
    """
    manager.reset_collection()
    return {"status": "success"}