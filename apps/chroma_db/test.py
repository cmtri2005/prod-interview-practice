# api/main.py

from fastapi import FastAPI
from router.router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chroma API",
    version="1.0.0"
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="0.0.0.0", port=8008, reload=True)
