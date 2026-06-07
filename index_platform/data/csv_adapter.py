"""CSV adapter for local daily price files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data


def read_price_csv(path: str | Path) -> pd.DataFrame:
    """Read and normalize a local daily price CSV file."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Price CSV file not found: {csv_path}")

    raw = pd.read_csv(csv_path)
    return normalize_daily_price_data(raw)

