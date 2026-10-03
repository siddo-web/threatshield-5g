import numpy as np
from backend.ml.zero_day import AutoencoderAnomalyDetector


def test_anomaly_detector():
    x = np.random.randn(100, 5).astype(float)
    model = AutoencoderAnomalyDetector(input_dim=5, epochs=2)
    model.fit(x)
    pred, scores = model.predict(x)
    assert pred.shape[0] == x.shape[0]
    assert scores.shape[0] == x.shape[0]
