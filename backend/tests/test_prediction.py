import pandas as pd

from backend.ml.detector import ThreatDetector


def test_detector_prediction():
    df = pd.DataFrame(
        {
            "duration": [10, 12, 50, 60, 11, 55],
            "src_bytes": [100, 110, 5000, 6000, 120, 8000],
            "dst_bytes": [90, 100, 6000, 7000, 110, 9000],
            "packets": [10, 20, 300, 250, 15, 320],
            "label": ["Benign", "Benign", "DDoS", "DDoS", "Benign", "DDoS"],
        }
    )
    detector = ThreatDetector(model_type="random_forest")
    detector.fit(df.drop(columns=["label"]), df["label"])
    preds = detector.predict(df.drop(columns=["label"]))
    assert len(preds) == len(df)
