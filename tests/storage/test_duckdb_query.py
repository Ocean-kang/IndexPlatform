import importlib.util

import pandas as pd
import pytest

from index_platform.storage.duckdb_query import query_price_data
from index_platform.storage.parquet_store import save_price_data


def _prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03", "2024-01-02"],
            "symbol": ["AAA", "AAA", "BBB"],
            "open": [10, 11, 20],
            "high": [11, 12, 21],
            "low": [9, 10, 19],
            "close": [10.5, 11.5, 20.5],
            "volume": [1000, 1100, 1200],
            "amount": [10000, 11000, 12000],
            "currency": ["CNY", "CNY", "CNY"],
            "source": ["toy", "toy", "toy"],
        }
    )


@pytest.mark.skipif(importlib.util.find_spec("duckdb") is None, reason="duckdb is not installed")
def test_query_price_data_filters_symbol_and_dates(tmp_path) -> None:
    save_price_data(_prices(), tmp_path)

    result = query_price_data(tmp_path, symbol="AAA", start_date="2024-01-03", end_date="2024-01-03")

    assert result["symbol"].tolist() == ["AAA"]
    assert result["date"].tolist() == [pd.Timestamp("2024-01-03")]
    assert result["close"].tolist() == [11.5]
