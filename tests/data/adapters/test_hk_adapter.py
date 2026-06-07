import pandas as pd

from index_platform.data.adapters.hk_adapter import HongKongIndexAdapter


class _FakeYFinance:
    @staticmethod
    def download(symbol, start=None, end=None, progress=False, auto_adjust=False):
        assert symbol == "^HSI"
        return pd.DataFrame(
            {
                "Open": [18000.0, 18100.0],
                "High": [18200.0, 18300.0],
                "Low": [17900.0, 18050.0],
                "Close": [18100.0, 18250.0],
                "Volume": [1000, 1200],
            },
            index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
        ).rename_axis("Date")


def test_hk_adapter_standardizes_currency_as_hkd_without_network() -> None:
    adapter = HongKongIndexAdapter(yfinance_module=_FakeYFinance())

    data = adapter.fetch_daily("HSI.HK")

    assert data["symbol"].tolist() == ["HSI.HK", "HSI.HK"]
    assert data["currency"].tolist() == ["HKD", "HKD"]
    assert data["source"].tolist() == ["hk_yfinance", "hk_yfinance"]
