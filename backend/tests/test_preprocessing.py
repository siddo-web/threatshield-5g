import pandas as pd

from backend.ml.preprocessing import prepare_dataset


def test_preprocessor():
    df = pd.DataFrame(
        {
            "duration": [10, 20, 30, 40],
            "protocol": ["TCP", "UDP", "TCP", "UDP"],
            "label": ["Benign", "Benign", "DDoS", "DDoS"],
        }
    )
    prepared = prepare_dataset(df, target_column="label")
    assert prepared["X_train"].shape[0] > 0
    assert prepared["y_train"].shape[0] > 0
