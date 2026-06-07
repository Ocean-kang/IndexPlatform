"""Data ingestion and validation package."""

from index_platform.data.csv_adapter import read_price_csv
from index_platform.data.validators import normalize_daily_price_data, validate_required_fields

__all__ = [
    "normalize_daily_price_data",
    "read_price_csv",
    "validate_required_fields",
]
