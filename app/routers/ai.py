from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Task
from app.services import llm

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/tasks/{task_id}/breakdown", response_model=llm.Breakdown)
def breakdown(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    try:
        return llm.break_down(task.title, task.due, task.estimate_minutes)
    except llm.LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/overwhelmed", response_model=llm.OverwhelmedPlan)
def overwhelmed(hours_available: float | None = None, db: Session = Depends(get_db)):
    open_tasks = db.scalars(select(Task).where(Task.done.is_(False))).all()
    if not open_tasks:
        return llm.OverwhelmedPlan(essential=[], message="Nothing open. Enjoy the break!")
    tasks = [
        {
            "id": t.id,
            "title": t.title,
            "due": t.due,
            "deadline_type": t.deadline_type.value,
            "estimate_minutes": t.estimate_minutes,
        }
        for t in open_tasks
    ]
    try:
        return llm.overwhelmed(tasks, hours_available)
    except llm.LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
