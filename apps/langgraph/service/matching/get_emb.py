import os
from typing import Any, Dict
from langchain_huggingface import HuggingFaceInferenceAPIEmbeddings

def get_emb() -> Dict[str, Any]:
    model_embedding = HuggingFaceInferenceAPIEmbeddings(
        api_key=os.environ.get("HUGGINGFACE_API_KEY"),
        model_id=os.environ.get("EMBEDDING_MODEL_ID")
    )
    return {"model_embeddings": model_embedding}
    

    
    
