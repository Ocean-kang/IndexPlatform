"""Local storage package."""

from index_platform.storage.parquet_store import load_price_data, save_price_data

__all__ = [
    "load_price_data",
    "save_price_data",
]
