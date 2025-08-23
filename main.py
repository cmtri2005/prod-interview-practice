# api/main.py

from fastapi import FastAPI
from router.chroma_router import router

app = FastAPI(
    title="Chroma API",
    version="1.0.0"
)

# Mount router
app.include_router(router)

# For manual run:  python api/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8008, reload=True)
