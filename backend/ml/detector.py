import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from backend.ml.preprocessing import build_preprocessor, save_label_encoder, save_preprocessor

logger = logging.getLogger(__name__)


class ThreatDetector:
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type.lower()
        self.model = None
        self.preprocessor = None
        self.label_encoder = None
        self.feature_names = None

    def _make_model(self):
        if self.model_type == "random_forest":
            return RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
        raise ValueError(f"Unsupported model type: {self.model_type}")

    def fit(self, X: pd.DataFrame, y: pd.Series):
        self.preprocessor = build_preprocessor(X)
        X_processed = self.preprocessor.fit_transform(X)
        self.feature_names = [f"feature_{idx}" for idx in range(X_processed.shape[1])]

        labels = sorted(y.unique().tolist())
        self.label_encoder = {label: idx for idx, label in enumerate(labels)}
        y_encoded = pd.Series(y).map(self.label_encoder).to_numpy()

        self.model = self._make_model()
        self.model.fit(X_processed, y_encoded)
        return self

    def predict(self, X: pd.DataFrame):
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model has not been trained yet.")
        X_processed = self.preprocessor.transform(X)
        return self.model.predict(X_processed)

    def predict_proba(self, X: pd.DataFrame):
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model has not been trained yet.")
        X_processed = self.preprocessor.transform(X)
        return self.model.predict_proba(X_processed)

    def save(self, directory: str):
        directory_path = Path(directory)
        directory_path.mkdir(parents=True, exist_ok=True)
        save_preprocessor(self.preprocessor, str(directory_path / "preprocessor.joblib"))
        save_label_encoder(self.label_encoder, str(directory_path / "label_encoder.joblib"))
        joblib.dump(self.model, str(directory_path / "random_forest.joblib"))

    def load(self, directory: str):
        directory_path = Path(directory)
        self.preprocessor = joblib.load(str(directory_path / "preprocessor.joblib"))
        self.label_encoder = joblib.load(str(directory_path / "label_encoder.joblib"))
        self.model = joblib.load(str(directory_path / "random_forest.joblib"))
        return self


def train_random_forest(X: pd.DataFrame, y: pd.Series, save_dir: str = "models/detector"):
    detector = ThreatDetector(model_type="random_forest")
    detector.fit(X, y)
    detector.save(save_dir)
    return detector
