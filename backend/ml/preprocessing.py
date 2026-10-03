"""Utilities for preprocessing and training preparation."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def detect_columns(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    numeric_cols: List[str] = []
    categorical_cols: List[str] = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            categorical_cols.append(col)
    return numeric_cols, categorical_cols


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates().reset_index(drop=True)
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
            df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode()
            fill_value = mode.iloc[0] if not mode.empty else "unknown"
            df[col] = df[col].fillna(fill_value)
    return df


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    numeric_cols, categorical_cols = detect_columns(X)
    steps: list[tuple[str, Pipeline | ColumnTransformer, list[str]]] = []

    if numeric_cols:
        steps.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            )
        )

    if categorical_cols:
        steps.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            )
        )

    if not steps:
        raise ValueError("No usable columns found for preprocessing.")

    return ColumnTransformer(transformers=steps, remainder="drop")


def prepare_dataset(
    df: pd.DataFrame,
    target_column: str | None = None,
    random_state: int = 42,
    use_smote: bool = False,
):
    df = normalize_column_names(clean_dataframe(df))

    if target_column is None:
        for candidate in ["label", "attack_type", "threat_label", "target"]:
            if candidate in df.columns:
                target_column = candidate
                break

    if target_column is None or target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")

    X = df.drop(columns=[target_column])
    y = df[target_column].copy()
    preprocessor = build_preprocessor(X)
    X_processed = preprocessor.fit_transform(X)

    label_mapping = {label: idx for idx, label in enumerate(sorted(y.dropna().unique().tolist()))}
    y_encoded = pd.Series(y).map(label_mapping).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y_encoded,
        test_size=0.2,
        random_state=random_state,
        stratify=y_encoded if len(np.unique(y_encoded)) > 1 else None,
    )

    if use_smote and X_train.shape[0] > 0 and len(np.unique(y_train)) > 1:
        try:
            smote = SMOTE(random_state=random_state)
            X_train, y_train = smote.fit_resample(X_train, y_train)
        except Exception as exc:  # pragma: no cover
            logger.warning("SMOTE failed: %s", exc)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "preprocessor": preprocessor,
        "label_encoder": label_mapping,
        "target": target_column,
    }


def save_preprocessor(preprocessor: ColumnTransformer, path: str) -> None:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, path_obj)


def save_label_encoder(label_encoder: dict | None, path: str) -> None:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    if label_encoder is None:
        joblib.dump({}, path_obj)
    else:
        joblib.dump(label_encoder, path_obj)
