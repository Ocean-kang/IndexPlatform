"""FX storage and conversion helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.fx.csv_adapter import normalize_fx_data

DEFAULT_FX_FILE_NAME = "fx_rates.parquet"


def save_fx_data(data: pd.DataFrame, storage_dir: str | Path) -> Path:
    """Save FX rates to Parquet."""
    target_dir = Path(storage_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / DEFAULT_FX_FILE_NAME
    normalize_fx_data(data).to_parquet(target, index=False)
    return target


def load_fx_data(storage_dir: str | Path) -> pd.DataFrame:
    """Load FX rates from Parquet."""
    source = Path(storage_dir) / DEFAULT_FX_FILE_NAME
    if not source.exists():
        raise FileNotFoundError(f"FX Parquet file not found: {source}")
    return normalize_fx_data(pd.read_parquet(source))


def convert_amount(
    amount: float,
    from_currency: str,
    to_currency: str,
    date: str | pd.Timestamp,
    fx_rates: pd.DataFrame,
) -> float:
    """Convert an amount using a same-day direct or inverse FX rate."""
    source_currency = from_currency.upper()
    target_currency = to_currency.upper()
    if source_currency == target_currency:
        return float(amount)

    rates = normalize_fx_data(fx_rates)
    target_date = pd.Timestamp(date).normalize()
    same_day = rates[rates["date"] == target_date]

    direct = same_day[
        (same_day["base_currency"] == source_currency) & (same_day["quote_currency"] == target_currency)
    ]
    if not direct.empty:
        return float(amount) * float(direct.iloc[0]["rate"])

    inverse = same_day[
        (same_day["base_currency"] == target_currency) & (same_day["quote_currency"] == source_currency)
    ]
    if not inverse.empty:
        return float(amount) / float(inverse.iloc[0]["rate"])

    raise ValueError(f"Missing FX rate for {source_currency}/{target_currency} on {target_date.date().isoformat()}")
