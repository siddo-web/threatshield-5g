import joblib
from pathlib import Path


def load_detector():
    model_path = Path("models/detector/random_forest.joblib")
    if model_path.exists():
        return joblib.load(model_path)
    return None


def load_autoencoder():
    model_path = Path("models/zero_day/autoencoder.pt")
    if model_path.exists():
        return model_path
    return None


def load_preprocessor():
    model_path = Path("models/preprocessor.joblib")
    if model_path.exists():
        return joblib.load(model_path)
    return None
