"""Local Parquet storage for daily price data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data

DEFAULT_PRICE_FILE_NAME = "prices.parquet"


def save_price_data(data: pd.DataFrame, storage_dir: str | Path) -> Path:
    """Save normalized daily price data to a local Parquet file.

    Repeated writes replace the existing file, making the first storage version
    deterministic and easy to reason about.
    """
    target_dir = Path(storage_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / DEFAULT_PRICE_FILE_NAME

    normalized = normalize_daily_price_data(data).sort_values(["symbol", "date"]).reset_index(drop=True)
    normalized.to_parquet(target_file, index=False)
    return target_file


def load_price_data(
    storage_dir: str | Path,
    symbol: str | None = None,
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Load local price data with optional symbol and date filters."""
    source_file = Path(storage_dir) / DEFAULT_PRICE_FILE_NAME
    if not source_file.exists():
        raise FileNotFoundError(f"Price Parquet file not found: {source_file}")

    data = pd.read_parquet(source_file)
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()

    if symbol is not None:
        data = data[data["symbol"] == symbol]
    if start_date is not None:
        start = pd.Timestamp(start_date).normalize()
        data = data[data["date"] >= start]
    if end_date is not None:
        end = pd.Timestamp(end_date).normalize()
        data = data[data["date"] <= end]

    return data.reset_index(drop=True)

