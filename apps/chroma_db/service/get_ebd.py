from service.vectorstores.chroma_store import ChromaStore
import yaml

# load config
with open("./configs/config.yml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

chroma_cfg = cfg["chroma"]

store = ChromaStore(
    collection_name=chroma_cfg["collection_name"],
    client_settings=chroma_cfg["client_settings"],
)

data = store.collection.get(include=["documents", "embeddings", "metadatas"])
for idx, _id in enumerate(data["ids"]):
    doc = data["documents"][idx]
    emb = data["embeddings"][idx]               
    
    

    meta = data["metadatas"][idx]

    emb_preview = f"{emb[:5]} ... (len={len(emb)})"

    print(f"ID: {_id}" + f"   Doc: {doc}" + f"   Embedding: {emb_preview}" + f"   Metadata: {meta}")
    print("-" * 40)
