"""API routes for threat detection and alert management."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.database_models import Alert, MitigationLog, TrafficEvent
from backend.app.services.mitigation_service import get_mitigation_action
from backend.ml.detector import ThreatDetector
from backend.ml.zero_day import AutoencoderAnomalyDetector

router = APIRouter(prefix="/api", tags=["detection"])


class TrafficSample(BaseModel):
    """Network traffic sample for prediction."""

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
    """Request body for threat prediction."""

    samples: list[TrafficSample]


class PredictionResponse(BaseModel):
    """Response body for threat prediction."""

    label: str
    confidence: float
    mitigation_action: str
    anomaly_score: float | None


class AlertCreate(BaseModel):
    """Request body for creating an alert."""

    source: str = "unknown"
    attack_type: str = "DDoS"
    confidence: float = 0.8
    severity: str = "medium"
    anomaly_score: float | None = None
    action: str | None = None
    status: str = "open"
    details: str | None = None


class AlertResponse(BaseModel):
    """Response body for alert."""

    id: int
    source: str
    attack_type: str
    confidence: float
    severity: str
    anomaly_score: float | None
    action: str
    status: str
    details: str | None


def load_detector() -> ThreatDetector | None:
    """Load trained threat detector from disk."""
    detector_path = Path("models/detector")
    if not detector_path.exists():
        return None
    rf_path = detector_path / "random_forest.joblib"
    if not rf_path.exists():
        return None

    detector = ThreatDetector(model_type="random_forest")
    detector.load(str(detector_path))
    return detector


def load_autoencoder() -> AutoencoderAnomalyDetector | None:
    """Load trained autoencoder model from disk."""
    model_path = Path("models/zero_day/autoencoder.pt")
    if not model_path.exists():
        return None

    detector = AutoencoderAnomalyDetector(input_dim=15)
    detector.load(str(model_path))
    return detector


@router.post("/predict", response_model=dict[str, list[PredictionResponse]])
def predict(payload: PredictionRequest):
    """Predict threat labels for traffic samples."""
    detector = load_detector()
    if detector is None:
        raise HTTPException(
            status_code=503, detail="Model not trained yet. Run the seed script first."
        )

    if not payload.samples:
        raise HTTPException(status_code=400, detail="At least one sample is required.")

    frame = pd.DataFrame([sample.model_dump() for sample in payload.samples])
    labels = detector.predict(frame)
    probs = detector.predict_proba(frame)
    inverse_label_map = {idx: label for label, idx in detector.label_encoder.items()}

    autoencoder = load_autoencoder()
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


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(db: Session = Depends(get_db), limit: int = 50):
    """List all alerts."""
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    return [
        AlertResponse(
            id=alert.id,
            source=alert.source,
            attack_type=alert.attack_type,
            confidence=alert.confidence,
            severity=alert.severity,
            anomaly_score=alert.anomaly_score,
            action=alert.action,
            status=alert.status,
            details=alert.details,
        )
        for alert in alerts
    ]


@router.post("/alerts", response_model=dict[str, Any])
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert."""
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

    mitigation_log = MitigationLog(
        source=alert.source,
        attack_type=alert.attack_type,
        confidence=alert.confidence,
        action=alert.action,
        details=f"Auto-logged: {alert.details or 'N/A'}",
    )
    db.add(mitigation_log)
    db.commit()

    return {"id": alert.id, "status": alert.status, "attack_type": alert.attack_type}


@router.get("/traffic")
def list_traffic(db: Session = Depends(get_db), limit: int = 20):
    """List recent traffic events."""
    events = db.query(TrafficEvent).order_by(TrafficEvent.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": event.id,
            "source": event.source,
            "protocol": event.protocol,
            "attack_type": event.attack_type,
            "confidence": event.confidence,
            "severity": event.severity,
            "action": event.action,
            "anomaly_score": event.anomaly_score,
        }
        for event in events
    ]


@router.post("/traffic")
def create_traffic_event(
    source: str,
    protocol: str,
    attack_type: str = "Benign",
    confidence: float = 0.5,
    db: Session = Depends(get_db),
):
    """Create a traffic event."""
    event = TrafficEvent(
        source=source,
        protocol=protocol,
        attack_type=attack_type,
        confidence=confidence,
        action=get_mitigation_action(attack_type),
        severity="high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"id": event.id, "attack_type": event.attack_type}


@router.get("/mitigation-logs")
def list_mitigation_logs(db: Session = Depends(get_db), limit: int = 50):
    """List mitigation actions taken."""
    logs = (
        db.query(MitigationLog).order_by(MitigationLog.timestamp.desc()).limit(limit).all()
    )
    return [
        {
            "id": log.id,
            "source": log.source,
            "attack_type": log.attack_type,
            "confidence": log.confidence,
            "action": log.action,
            "status": log.status,
            "details": log.details,
        }
        for log in logs
    ]


@router.get("/metrics")
def get_model_metrics():
    """Get trained model metrics."""
    metrics_path = Path("models/metrics/random_forest.json")
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {"status": "demo", "models": []}
