import pandas as pd

from index_platform.data.adapters.akshare_adapter import AkShareIndexAdapter, standardize_akshare_daily
from index_platform.data.schema import DAILY_PRICE_REQUIRED_FIELDS


class _NoAkshareAdapter(AkShareIndexAdapter):
    def _load_akshare(self):
        raise ImportError("AKShare is not installed. Install optional dependency 'akshare' to use this adapter.")


def test_akshare_standardizes_daily_price_schema() -> None:
    raw = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "open": [10, 11],
            "high": [11, 12],
            "low": [9, 10],
            "close": [10.5, 11.5],
            "volume": [1000, 1200],
            "amount": [10000, 13000],
        }
    )

    data = standardize_akshare_daily(raw, symbol="000300.SH")

    assert list(data.columns) == DAILY_PRICE_REQUIRED_FIELDS
    assert data["symbol"].tolist() == ["000300.SH", "000300.SH"]
    assert data["currency"].tolist() == ["CNY", "CNY"]
    assert data["source"].tolist() == ["akshare", "akshare"]


def test_akshare_missing_dependency_has_clear_error() -> None:
    adapter = _NoAkshareAdapter()

    try:
        adapter.fetch_daily("000300.SH")
    except ImportError as exc:
        assert "AKShare is not installed" in str(exc)
    else:
        raise AssertionError("Expected missing AKShare to raise ImportError")
