from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from router.schema.chroma_schma import DocumentIn, MetadataIn, QueryIn, EmbeddingIn
from service.vectorstores.chroma_store import ChromaStore
from service.manage_collection import ChromaCollectionManager
import uuid
from router.extract_text_from_file import extract_text_from_file
import json
from typing import List

router = APIRouter(prefix="/chroma")
manager = ChromaCollectionManager()


@router.post("/add_text_to_collection")
def add_text_to_collection(
    docs: List[DocumentIn],
    metadatas: List[MetadataIn]
):
    manager.store = ChromaStore(
        client_settings=manager.cfg['chroma']['client_settings']
    )
    
    ids = [str(uuid.uuid4()) for _ in docs]
    contents = [d.query_text for d in docs]
    metas = [m.dict() for m in metadatas]
    manager.add_documents(ids, contents, metadatas=metas)
    print(metas)
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
    manager.store = ChromaStore(
        client_settings=manager.cfg['chroma']['client_settings']
    )
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
    
    # parse JSON metadata string -> dict
    try:
        metadatas_list = [MetadataIn(**m) for m in json.loads(metadatas)]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in metadatas")


    text = extract_text_from_file(file)
    if not text.strip():
        return {"status": "error", "message": "Empty file"}
    docs = [DocumentIn(query_text=text)]
    
    manager.store = ChromaStore(
        client_settings=manager.cfg['chroma']['client_settings']
    )
    
    ids = [str(uuid.uuid4()) for _ in docs]
    contents = [d.query_text for d in docs]
    metas = [m.dict() for m in metadatas_list]
    print(metas)
    # add vào DB
    manager.add_documents(ids, contents, metadatas=metas)

    return {
        "status": "success",
        "num": len(docs),
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