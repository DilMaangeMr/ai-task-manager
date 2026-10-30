import random

from sklearn.linear_model import LinearRegression

from app.db import SessionLocal
from app.ml import duration


def mae(preds, actuals) -> float:
    return sum(abs(p - a) for p, a in zip(preds, actuals)) / len(actuals)


with SessionLocal() as db:
    history = duration.load_history(db)

random.seed(0)
random.shuffle(history)
cut = int(len(history) * 0.8)
train, test = history[:cut], history[cut:]       # never judge on data you trained on
actuals = [a for _, _, a in test]

model = duration.fit(train)
no_cat = {**model, "category_ratio": {}}

# sklearn linear regression: estimate plus one 0/1 column per category
cats = sorted({c for c, _, _ in train if c})
def features(cat, est):
    return [est] + [1.0 if cat == k else 0.0 for k in cats]
lr = LinearRegression().fit(
    [features(c, e) for c, e, _ in train], [a for _, _, a in train]
)

results = {
    "1. Baseline: actual = estimate": [e for _, e, _ in test],
    "2. One overall ratio": [duration.predict_with(no_cat, e, c) for c, e, _ in test],
    "3. Ratio per category": [duration.predict_with(model, e, c) for c, e, _ in test],
    "4. sklearn linear regression": list(lr.predict([features(c, e) for c, e, _ in test])),
}
print(f"Trained on {len(train)} tasks, tested on {len(test)} unseen tasks\n")
for name, preds in results.items():
    print(f"{name:35s} typical error: {mae(preds, actuals):5.1f} min")
