"""CSV adapter for FX rates."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.fx.schema import FX_REQUIRED_FIELDS


def normalize_fx_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize FX rate data."""
    missing = [field for field in FX_REQUIRED_FIELDS if field not in data.columns]
    if missing:
        raise ValueError(f"Missing required FX fields: {', '.join(missing)}")
    normalized = data.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="raise").dt.normalize()
    normalized["base_currency"] = normalized["base_currency"].astype(str).str.upper()
    normalized["quote_currency"] = normalized["quote_currency"].astype(str).str.upper()
    normalized["rate"] = pd.to_numeric(normalized["rate"], errors="raise")
    if (normalized["rate"] <= 0).any():
        raise ValueError("FX rates must be positive.")
    return normalized[FX_REQUIRED_FIELDS].sort_values(["date", "base_currency", "quote_currency"]).reset_index(drop=True)


def read_fx_csv(path: str | Path) -> pd.DataFrame:
    """Read and normalize an FX CSV file."""
    return normalize_fx_data(pd.read_csv(path))
