"""DuckDB-backed local Parquet query helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.storage.parquet_store import DEFAULT_PRICE_FILE_NAME


def query_price_data(
    storage_dir: str | Path,
    symbol: str | None = None,
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Query local price Parquet data with optional symbol and date filters."""
    try:
        import duckdb
    except ImportError as exc:
        raise ImportError("duckdb is not installed. Install project dependencies to use DuckDB queries.") from exc

    source_file = Path(storage_dir) / DEFAULT_PRICE_FILE_NAME
    if not source_file.exists():
        raise FileNotFoundError(f"Price Parquet file not found: {source_file}")

    clauses: list[str] = []
    params: list[object] = []
    if symbol is not None:
        clauses.append("symbol = ?")
        params.append(symbol)
    if start_date is not None:
        clauses.append("date >= ?")
        params.append(pd.Timestamp(start_date).normalize())
    if end_date is not None:
        clauses.append("date <= ?")
        params.append(pd.Timestamp(end_date).normalize())

    where_sql = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = f"SELECT * FROM read_parquet(?) {where_sql} ORDER BY symbol, date"
    result = duckdb.connect(database=":memory:").execute(query, [str(source_file), *params]).df()
    if "date" in result.columns:
        result["date"] = pd.to_datetime(result["date"]).dt.normalize()
    return result.reset_index(drop=True)
