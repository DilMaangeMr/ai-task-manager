import json
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import DATA_DIR
from app.models import Task

MODEL_PATH = DATA_DIR / "duration_model.json"
MIN_TASKS = 20          # below this, we do not trust the history yet
MIN_PER_CATEGORY = 5    # below this, a category falls back to the overall ratio


def load_history(db: Session) -> list[tuple[str | None, int, int]]:
    """Completed tasks that have both an estimate and an actual time."""
    rows = db.scalars(
        select(Task).where(
            Task.done.is_(True),
            Task.estimate_minutes.is_not(None),
            Task.actual_minutes.is_not(None),
        )
    ).all()
    return [(t.category, t.estimate_minutes, t.actual_minutes) for t in rows]


def fit(history) -> dict:
    """'Training': learn how much longer than your estimate tasks really take."""
    by_cat: dict[str, list[float]] = {}
    for cat, est, actual in history:
        if cat:
            by_cat.setdefault(cat, []).append(actual / est)
    return {
        "n": len(history),
        "overall_ratio": mean(actual / est for _, est, actual in history),
        "category_ratio": {
            c: mean(r) for c, r in by_cat.items() if len(r) >= MIN_PER_CATEGORY
        },
    }


def predict_with(model: dict | None, estimate: int, category: str | None) -> int:
    if model is None or model["n"] < MIN_TASKS:
        return estimate                         # cold start: trust the estimate
    ratio = model["category_ratio"].get(category or "", model["overall_ratio"])
    return round(estimate * ratio)


def train(db: Session) -> dict:
    model = fit(load_history(db))
    MODEL_PATH.write_text(json.dumps(model, indent=2))
    return model


def load_model() -> dict | None:
    return json.loads(MODEL_PATH.read_text()) if MODEL_PATH.exists() else None


def predict(estimate: int, category: str | None) -> int:
    return predict_with(load_model(), estimate, category)
