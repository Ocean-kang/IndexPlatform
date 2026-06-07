"""Local storage package."""

from index_platform.storage.backtest_store import generate_run_id, load_backtest_result, save_backtest_result
from index_platform.storage.duckdb_query import query_price_data
from index_platform.storage.parquet_store import load_price_data, save_price_data

__all__ = [
    "generate_run_id",
    "load_backtest_result",
    "load_price_data",
    "query_price_data",
    "save_backtest_result",
    "save_price_data",
]
