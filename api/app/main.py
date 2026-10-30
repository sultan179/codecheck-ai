from fastapi import FastAPI

from app.config import Settings
from app.database import is_database_reachable

app=FastAPI(title="CodeCheck AI")
settings=Settings()

@app.get("/health")
def health()->dict:
    return {"status":"ok","db":is_database_reachable(settings)}