from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import SessionLocal, get_db, init_db
from backend.app.models.database_models import Alert, TrafficEvent
from backend.app.services.mitigation_service import get_mitigation_action
from backend.ml.detector import ThreatDetector
from backend.ml.zero_day import AutoencoderAnomalyDetector


class TrafficSample(BaseModel):
    duration: float
    protocol: str
    src_bytes: float
    dst_bytes: float
    packets: int = Field(..., ge=1)
    src_port: int
    dst_port: int
    packet_rate: float
    byte_rate: float
    flow_duration: float
    tcp_flags: int
    ttl: int
    connection_count: int
    failed_connections: int
    payload_size: float


class PredictionRequest(BaseModel):
    samples: list[TrafficSample]


class AlertCreate(BaseModel):
    source: str = "unknown"
    attack_type: str = "DDoS"
    confidence: float = 0.8
    severity: str = "medium"
    anomaly_score: float | None = None
    action: str | None = None
    status: str = "open"
    details: str | None = None


app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/metrics")
def get_metrics():
    metrics_path = Path("models/metrics/random_forest.json")
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"status": "demo", "models": []}


def _load_detector() -> ThreatDetector | None:
    detector_path = Path("models/detector")
    if not detector_path.exists():
        return None
    rf_path = detector_path / "random_forest.joblib"
    if not rf_path.exists():
        return None

    detector = ThreatDetector(model_type="random_forest")
    detector.load(str(detector_path))
    return detector


def _load_autoencoder() -> AutoencoderAnomalyDetector | None:
    model_path = Path("models/zero_day/autoencoder.pt")
    if not model_path.exists():
        return None

    detector = AutoencoderAnomalyDetector(input_dim=15)
    detector.load(str(model_path))
    return detector


@app.post("/predict")
def predict(payload: PredictionRequest):
    detector = _load_detector()
    if detector is None:
        raise HTTPException(status_code=503, detail="Model not trained yet. Run the seed script first.")

    if not payload.samples:
        raise HTTPException(status_code=400, detail="At least one sample is required.")

    frame = pd.DataFrame([sample.model_dump() for sample in payload.samples])
    labels = detector.predict(frame)
    probs = detector.predict_proba(frame)
    inverse_label_map = {idx: label for label, idx in detector.label_encoder.items()}

    autoencoder = _load_autoencoder()
    anomaly_scores = None
    if autoencoder is not None:
        anomaly_scores = autoencoder.reconstruction_error(frame.to_numpy(dtype=float))

    predictions: list[dict[str, Any]] = []
    for index, value in enumerate(labels):
        label = inverse_label_map[int(value)]
        confidence = float(probs[index].max())
        anomaly_score = float(anomaly_scores[index]) if anomaly_scores is not None else None
        predictions.append(
            {
                "label": label,
                "confidence": confidence,
                "mitigation_action": get_mitigation_action(label),
                "anomaly_score": anomaly_score,
            }
        )

    return {"predictions": predictions}


@app.get("/alerts")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
    return [{
        "id": alert.id,
        "source": alert.source,
        "attack_type": alert.attack_type,
        "confidence": alert.confidence,
        "severity": alert.severity,
        "anomaly_score": alert.anomaly_score,
        "action": alert.action,
        "status": alert.status,
        "details": alert.details,
    } for alert in alerts]


@app.post("/alerts")
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    alert = Alert(
        source=payload.source,
        attack_type=payload.attack_type,
        confidence=payload.confidence,
        severity=payload.severity,
        anomaly_score=payload.anomaly_score,
        action=payload.action or get_mitigation_action(payload.attack_type),
        status=payload.status,
        details=payload.details,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id, "status": alert.status, "attack_type": alert.attack_type}


@app.get("/traffic")
def list_traffic(db: Session = Depends(get_db), limit: int = 20):
    events = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).limit(limit).all()
    return [{
        "id": event.id,
        "source": event.source,
        "protocol": event.protocol,
        "attack_type": event.attack_type,
        "confidence": event.confidence,
        "severity": event.severity,
        "action": event.action,
        "anomaly_score": event.anomaly_score,
    } for event in events]


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "ready"}
