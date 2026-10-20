import logging

from fastapi import FastAPI

from app import models  # noqa: F401
from app.db import Base, engine
from app.routers import ai, tasks

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(engine)

app = FastAPI(title="AI Task Manager")
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
