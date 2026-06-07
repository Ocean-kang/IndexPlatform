import pandas as pd

from index_platform.data.adapters.yfinance_adapter import YFinanceAdapter, standardize_yfinance_daily
from index_platform.data.schema import DAILY_PRICE_REQUIRED_FIELDS


class _NoYFinanceAdapter(YFinanceAdapter):
    def _load_yfinance(self):
        raise ImportError("yfinance is not installed. Install optional dependency 'yfinance' to use this adapter.")


def _raw_yfinance() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        },
        index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
    ).rename_axis("Date")


def test_yfinance_standardizes_daily_price_schema() -> None:
    data = standardize_yfinance_daily(_raw_yfinance(), symbol="SPY")

    assert list(data.columns) == DAILY_PRICE_REQUIRED_FIELDS
    assert data["symbol"].tolist() == ["SPY", "SPY"]
    assert data["currency"].tolist() == ["USD", "USD"]
    assert data["amount"].tolist() == [0.0, 0.0]


def test_yfinance_missing_dependency_has_clear_error() -> None:
    adapter = _NoYFinanceAdapter()

    try:
        adapter.fetch_daily("SPY")
    except ImportError as exc:
        assert "yfinance is not installed" in str(exc)
    else:
        raise AssertionError("Expected missing yfinance to raise ImportError")
