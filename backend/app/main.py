from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import init_db
from backend.app.routes import router as api_router

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


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "ready"}


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


app.include_router(api_router)
