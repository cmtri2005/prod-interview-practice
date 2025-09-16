# api/main.py

from fastapi import FastAPI
from apps.api.router import router

app = FastAPI(
    title="Interview Practice API",
    description="API for interview practice with quiz generation and learning progress",
    version="1.0.0",
)


app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)
