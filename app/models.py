import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DeadlineType(str, enum.Enum):
    soft = "soft"
    hard = "hard"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    due: Mapped[date | None] = mapped_column(Date, nullable=True)
    deadline_type: Mapped[DeadlineType] = mapped_column(
        Enum(DeadlineType), default=DeadlineType.soft
    )
    done: Mapped[bool] = mapped_column(default=False)
    estimate_minutes: Mapped[int | None] = mapped_column(nullable=True)
    actual_minutes: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
