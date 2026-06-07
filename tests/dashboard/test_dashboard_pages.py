from pathlib import Path

import pandas as pd

from index_platform.dashboard.pages.backtest_result import list_backtest_runs
from index_platform.dashboard.pages.data_status import get_data_status
from index_platform.dashboard.pages.index_view import get_index_options, get_index_price_data
from index_platform.storage import save_price_data


def _prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03"],
            "symbol": ["000300.SH", "000300.SH"],
            "open": [100, 101],
            "high": [101, 102],
            "low": [99, 100],
            "close": [100, 102],
            "volume": [1000, 1000],
            "amount": [100000, 102000],
            "currency": ["CNY", "CNY"],
            "source": ["toy", "toy"],
        }
    )


def test_data_status_reuses_storage_and_quality(tmp_path: Path) -> None:
    save_price_data(_prices(), tmp_path)

    status = get_data_status(tmp_path)

    assert status["exists"] is True
    assert len(status["prices"]) == 2
    assert status["summary"].iloc[0]["symbol"] == "000300.SH"
    assert status["issues"] == []


def test_index_view_helpers_load_registry_and_prices(tmp_path: Path) -> None:
    save_price_data(_prices(), tmp_path)

    assert "000300.SH" in get_index_options()
    prices = get_index_price_data("000300.SH", tmp_path)

    assert len(prices) == 2


def test_list_backtest_runs(tmp_path: Path) -> None:
    (tmp_path / "run_b").mkdir()
    (tmp_path / "run_a").mkdir()

    assert list_backtest_runs(tmp_path) == ["run_a", "run_b"]
