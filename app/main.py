from fastapi import FastAPI

from app import models  # noqa: F401
from app.db import Base, engine
from app.routers import tasks

Base.metadata.create_all(engine)

app = FastAPI(title="AI Task Manager")
app.include_router(tasks.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
