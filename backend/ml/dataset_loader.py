"""CSV loading utilities for sample and real datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.ml.preprocessing import clean_dataframe, normalize_column_names, prepare_dataset


def load_csv_dataset(path: str | Path, target_column: str | None = None) -> pd.DataFrame:
    dataset_path = Path(path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"CSV dataset not found: {dataset_path}")
    df = pd.read_csv(dataset_path)
    df = normalize_column_names(clean_dataframe(df))
    if target_column is not None and target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")
    return df


def load_and_prepare_dataset(
    path: str | Path,
    target_column: str | None = None,
    random_state: int = 42,
    use_smote: bool = False,
):
    df = load_csv_dataset(path, target_column)
    return prepare_dataset(df, target_column=target_column, random_state=random_state, use_smote=use_smote)
