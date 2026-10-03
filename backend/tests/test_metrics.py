import numpy as np

from backend.ml.metrics import compute_metrics, false_positive_rate


def test_metric_calculation():
    y_true = np.array([0, 1, 1, 0])
    y_pred = np.array([0, 1, 0, 0])
    metrics = compute_metrics(y_true, y_pred, model_name="Test")
    assert "accuracy" in metrics
    assert metrics["false_positive_rate"] >= 0
    assert metrics["inference_latency_ms"] >= 0


def test_fpr_calculation():
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([1, 0, 1, 0])
    assert abs(false_positive_rate(y_true, y_pred) - 0.5) < 1e-9
