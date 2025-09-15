# api/main.py

from fastapi import FastAPI
from apps.api.router import router

app = FastAPI()

# Mount router
app.include_router(router)

# For manual run:  python api/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8008, reload=True)