from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionRecord(BaseModel):
    duration: float
    protocol: str = "TCP"
    src_bytes: float
    dst_bytes: float
    packets: float
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


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    anomaly_score: float
    is_anomaly: bool
    shap: list
    recommended_mitigation: str


class AlertFilter(BaseModel):
    limit: int = 20
    offset: int = 0
    severity: Optional[str] = None
    attack_type: Optional[str] = None
    search: Optional[str] = None


class AdversarialRequest(BaseModel):
    epsilon: float = Field(default=0.1, ge=0.0, le=0.3)
    defense: bool = True
