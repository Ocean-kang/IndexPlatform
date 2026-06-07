from pathlib import Path

import pandas as pd

from index_platform.config import BacktestConfig
from index_platform.research import expand_parameter_grid, run_parameter_sweep
from index_platform.storage import save_backtest_result


def test_expand_parameter_grid() -> None:
    rows = expand_parameter_grid({"window": [5, 10], "execution_delay": [0, 1]})

    assert rows == [
        {"window": 5, "execution_delay": 0},
        {"window": 5, "execution_delay": 1},
        {"window": 10, "execution_delay": 0},
        {"window": 10, "execution_delay": 1},
    ]


def test_run_parameter_sweep_summarizes_metrics(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"

    def fake_runner(*args, **kwargs) -> str:
        params = kwargs["strategy_params"]
        run_id = f"run_{params['window']}"
        nav = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-02"]), "nav": [1.0, 1.1]})
        positions = pd.DataFrame({"date": nav["date"], "symbol": "000300.SH", "position": 1.0})
        orders = pd.DataFrame(columns=["date", "symbol", "trade_value", "price", "quantity", "cost"])
        save_backtest_result(output_dir, {"strategy": "moving_average"}, nav, positions, orders, {"total_return": 0.1}, run_id)
        return run_id

    config = BacktestConfig(strategy_name="moving_average", symbols=["000300.SH"])
    summary = run_parameter_sweep(config, {"window": [5, 10]}, output_dir=output_dir, runner=fake_runner)

    assert list(summary["run_id"]) == ["run_5", "run_10"]
    assert list(summary["window"]) == [5, 10]
    assert list(summary["total_return"]) == [0.1, 0.1]
