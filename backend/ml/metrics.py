from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score


def false_positive_rate(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    if fp + tn == 0:
        return 0.0
    return float(fp / (fp + tn))


def compute_metrics(y_true, y_pred, model_name: str = "Model"):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    metrics = {
        "model": model_name,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "false_positive_rate": float(false_positive_rate((y_true == 1).astype(int), (y_pred == 1).astype(int))),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "inference_latency_ms": 0.0,
    }
    return metrics


def save_metrics(metrics: dict, path: str):
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)


def measure_latency_ms(func, *args, **kwargs):
    start = perf_counter()
    output = func(*args, **kwargs)
    latency_ms = (perf_counter() - start) * 1000.0
    return output, latency_ms
