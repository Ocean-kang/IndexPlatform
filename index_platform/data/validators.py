"""Validation helpers for price data."""

from __future__ import annotations

import pandas as pd

from index_platform.data.schema import DAILY_PRICE_NUMERIC_FIELDS, DAILY_PRICE_REQUIRED_FIELDS


def validate_required_fields(data: pd.DataFrame) -> None:
    """Validate that all daily price fields are present."""
    missing = [field for field in DAILY_PRICE_REQUIRED_FIELDS if field not in data.columns]
    if missing:
        raise ValueError(f"Daily price data is missing required fields: {', '.join(missing)}")


def normalize_daily_price_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return daily price data with standardized dates and numeric columns."""
    validate_required_fields(data)
    normalized = data.loc[:, DAILY_PRICE_REQUIRED_FIELDS].copy()

    normalized["date"] = pd.to_datetime(
        normalized["date"],
        errors="raise",
        format="mixed",
    ).dt.normalize()
    for field in DAILY_PRICE_NUMERIC_FIELDS:
        normalized[field] = pd.to_numeric(normalized[field], errors="raise")

    return normalized
