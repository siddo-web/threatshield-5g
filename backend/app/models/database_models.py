from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="analyst")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False, default="unknown")
    attack_type = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    severity = Column(String(30), nullable=False, default="medium")
    anomaly_score = Column(Float, nullable=True)
    action = Column(String(100), nullable=False, default="allow")
    status = Column(String(30), nullable=False, default="open")
    details = Column(Text, nullable=True)


class MitigationLog(Base):
    __tablename__ = "mitigation_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False, default="unknown")
    attack_type = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    action = Column(String(100), nullable=False, default="allow")
    status = Column(String(30), nullable=False, default="logged")
    details = Column(Text, nullable=True)


class TrafficEvent(Base):
    __tablename__ = "traffic_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    source = Column(String(100), nullable=False)
    protocol = Column(String(50), nullable=True)
    attack_type = Column(String(100), nullable=False, default="Benign")
    confidence = Column(Float, nullable=False, default=0.0)
    action = Column(String(100), nullable=True)
    severity = Column(String(30), nullable=False, default="low")
    anomaly_score = Column(Float, nullable=True)
    details = Column(Text, nullable=True)
