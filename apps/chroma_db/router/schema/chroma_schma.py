from pydantic import BaseModel
from typing import List, Optional

class DocumentIn(BaseModel):
    query_text:  str

class MetadataIn(BaseModel):
    list_string: List[str]  
    
class EmbeddingIn(BaseModel):
    array: List[List[float]]
    
class QueryIn(BaseModel):
    query: str
    top_k: Optional[int] = None