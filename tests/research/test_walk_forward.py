from pathlib import Path

import pandas as pd
import pytest

from index_platform.config import BacktestConfig
from index_platform.research import generate_walk_forward_windows, run_walk_forward
from index_platform.storage import save_backtest_result


def test_generate_walk_forward_windows() -> None:
    windows = generate_walk_forward_windows("2024-01-01", "2024-01-10", train_days=3, test_days=2)

    assert windows == [
        {
            "train_start": "2024-01-01",
            "train_end": "2024-01-03",
            "test_start": "2024-01-04",
            "test_end": "2024-01-05",
        },
        {
            "train_start": "2024-01-03",
            "train_end": "2024-01-05",
            "test_start": "2024-01-06",
            "test_end": "2024-01-07",
        },
        {
            "train_start": "2024-01-05",
            "train_end": "2024-01-07",
            "test_start": "2024-01-08",
            "test_end": "2024-01-09",
        },
    ]


def test_run_walk_forward_summarizes_oos_metrics(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"

    def fake_runner(*args, **kwargs) -> str:
        run_id = f"run_{kwargs['start_date']}"
        nav = pd.DataFrame({"date": pd.to_datetime([kwargs["start_date"], kwargs["end_date"]]), "nav": [1.0, 1.05]})
        positions = pd.DataFrame({"date": nav["date"], "symbol": "000300.SH", "position": 1.0})
        orders = pd.DataFrame(columns=["date", "symbol", "trade_value", "price", "quantity", "cost"])
        save_backtest_result(output_dir, {"strategy": "buy_hold"}, nav, positions, orders, {"total_return": 0.05}, run_id)
        return run_id

    config = BacktestConfig(
        strategy_name="buy_hold",
        symbols=["000300.SH"],
        start_date="2024-01-01",
        end_date="2024-01-08",
    )
    summary = run_walk_forward(config, train_days=3, test_days=2, output_dir=output_dir, runner=fake_runner)

    assert list(summary["window"]) == [1, 2]
    assert list(summary["total_return"]) == [0.05, 0.05]
    assert list(summary["test_start"]) == ["2024-01-04", "2024-01-06"]


def test_run_walk_forward_requires_dates() -> None:
    config = BacktestConfig(strategy_name="buy_hold", symbols=["000300.SH"])

    with pytest.raises(ValueError, match="requires start_date and end_date"):
        run_walk_forward(config, train_days=3, test_days=2)
