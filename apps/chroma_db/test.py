# api/main.py

from fastapi import FastAPI
from router.chroma_router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chroma API",
    version="1.0.0"
)

# Mount router
app.include_router(router)
# bật CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# For manual run:  python api/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="0.0.0.0", port=8008, reload=True)
