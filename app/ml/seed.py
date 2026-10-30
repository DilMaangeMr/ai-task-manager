import random
from datetime import datetime, timedelta

from sqlalchemy import delete

from app.db import Base, SessionLocal, engine
from app.models import DeadlineType, Task

# The hidden "truth" the model must discover: how much each category overruns
OVERRUN = {"email": 2.0, "coding": 1.5, "writing": 1.7, "meeting": 1.0, "admin": 1.2}
ESTIMATES = [10, 15, 20, 30, 45, 60, 90, 120]


def main(n: int = 150) -> None:
    Base.metadata.create_all(engine)
    random.seed(42)
    with SessionLocal() as db:
        db.execute(delete(Task).where(Task.title.like("[seed]%")))
        for i in range(n):
            cat = random.choice(list(OVERRUN))
            est = random.choice(ESTIMATES)
            noise = random.lognormvariate(0, 0.15)
            actual = max(1, round(est * OVERRUN[cat] * noise))
            db.add(Task(
                title=f"[seed] {cat} task {i}", category=cat, done=True,
                estimate_minutes=est, actual_minutes=actual,
                deadline_type=DeadlineType.soft,
                completed_at=datetime.now() - timedelta(days=random.randint(0, 60)),
            ))
        db.commit()
    print(f"Seeded {n} completed tasks")


if __name__ == "__main__":
    main()
