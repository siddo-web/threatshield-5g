"""Seed script for generating synthetic demo data and initial artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.database import SessionLocal, init_db
from backend.app.models.database_models import Alert, User
from backend.ml.detector import ThreatDetector, train_random_forest
from backend.ml.metrics import compute_metrics, save_metrics
from backend.ml.synthetic_data import generate_traffic
from backend.ml.zero_day import build_autoencoder_model


def seed_demo_data():
    init_db()
    dataset = generate_traffic(n_samples=1500, random_state=42)
    path = Path("data/sample/5g_nidd_sample.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(path, index=False)

    X = dataset.drop(columns=["label"])
    y = dataset["label"]

    detector = train_random_forest(X, y, save_dir="models/detector")
    autoencoder = build_autoencoder_model(X.to_numpy(dtype=float), epochs=10)
    autoencoder.save("models/zero_day/autoencoder.pt")

    predictions = detector.predict(X)
    metrics = compute_metrics(y, predictions, model_name="RandomForest")
    save_metrics(metrics, "models/metrics/random_forest.json")

    db = SessionLocal()
    try:
        db.add(User(username="admin", password_hash="demo-admin-hash", role="admin"))
        db.add(User(username="analyst", password_hash="demo-analyst-hash", role="analyst"))
        db.add(
            Alert(
                source="10.0.0.25",
                attack_type="DDoS",
                confidence=0.94,
                severity="high",
                anomaly_score=0.87,
                action="rate-limit",
                status="open",
                details="Auto-generated demo alert.",
            )
        )
        db.commit()
    finally:
        db.close()

    return {"rows": len(dataset), "metrics": metrics}


if __name__ == "__main__":
    result = seed_demo_data()
    print(json.dumps(result, indent=2))
