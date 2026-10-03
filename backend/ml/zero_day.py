from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import torch

logger = logging.getLogger(__name__)


class AutoencoderAnomalyDetector:
    def __init__(self, input_dim: int, hidden_dim: int = 16, epochs: int = 20, learning_rate: float = 1e-3):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model().to(self.device)
        self.threshold = 0.0

    def _build_model(self):
        import torch.nn as nn

        return nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.input_dim),
            nn.Sigmoid(),
        )

    def fit(self, X: np.ndarray):
        if X.size == 0:
            raise ValueError("No benign data available for training.")

        X_tensor = torch.tensor(X.astype(np.float32), device=self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = torch.nn.MSELoss()

        for _ in range(self.epochs):
            optimizer.zero_grad()
            reconstructed = self.model(X_tensor)
            loss = criterion(reconstructed, X_tensor)
            loss.backward()
            optimizer.step()

        errors = self.reconstruction_error(X)
        self.threshold = float(np.quantile(errors, 0.99))
        return self

    def reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            X_tensor = torch.tensor(X.astype(np.float32), device=self.device)
            reconstructed = self.model(X_tensor)
            loss = torch.nn.functional.mse_loss(reconstructed, X_tensor, reduction="none")
            errors = loss.mean(dim=1).cpu().numpy()
        return errors

    def predict(self, X: np.ndarray):
        errors = self.reconstruction_error(X)
        return np.array([err > self.threshold for err in errors]), errors

    def save(self, path: str):
        directory = Path(path).parent
        directory.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load(self, path: str):
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        return self


def build_autoencoder_model(X: np.ndarray, epochs: int = 20, threshold_percentile: float = 0.99):
    model = AutoencoderAnomalyDetector(input_dim=X.shape[1], epochs=epochs)
    model.fit(X)
    model.threshold = float(np.quantile(model.reconstruction_error(X), threshold_percentile))
    return model
