from app.db import SessionLocal
from app.ml import duration

with SessionLocal() as db:
    model = duration.train(db)
print(f"Trained on {model['n']} tasks")
print(f"Overall: actual = {model['overall_ratio']:.2f} x estimate")
for cat, ratio in sorted(model["category_ratio"].items()):
    print(f"  {cat:8s} {ratio:.2f} x estimate")
