from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import DeadlineType


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    due: date | None = None
    deadline_type: DeadlineType = DeadlineType.soft
    estimate_minutes: int | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=50)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    due: date | None = None
    deadline_type: DeadlineType | None = None
    estimate_minutes: int | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=50)


class TaskComplete(BaseModel):
    actual_minutes: int | None = Field(default=None, gt=0)


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    due: date | None
    deadline_type: DeadlineType
    done: bool
    estimate_minutes: int | None
    actual_minutes: int | None
    category: str | None
    predicted_minutes: int | None
    created_at: datetime
    completed_at: datetime | None
