from pathlib import Path

import pandas as pd
import pytest

from index_platform.dashboard.pages.strategy_lab import run_dashboard_backtest
from index_platform.storage import load_backtest_result, save_price_data


def test_strategy_lab_runs_and_saves_backtest(tmp_path: Path) -> None:
    prices = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "symbol": ["000300.SH", "000300.SH", "000300.SH"],
            "open": [100, 100, 100],
            "high": [100, 110, 121],
            "low": [100, 100, 110],
            "close": [100, 110, 121],
            "volume": [1000, 1000, 1000],
            "amount": [100000, 110000, 121000],
            "currency": ["CNY", "CNY", "CNY"],
            "source": ["toy", "toy", "toy"],
        }
    )
    data_dir = tmp_path / "data"
    output_dir = tmp_path / "outputs"
    save_price_data(prices, data_dir)

    run_id = run_dashboard_backtest(
        "buy_hold",
        ["000300.SH"],
        data_dir=data_dir,
        output_dir=output_dir,
    )

    result = load_backtest_result(output_dir, run_id)
    assert result["metrics"]["total_return"] == pytest.approx(0.21)
    assert len(result["nav"]) == 3
