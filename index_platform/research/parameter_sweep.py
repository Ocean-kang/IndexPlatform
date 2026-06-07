"""Parameter sweep helpers."""

from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Callable

import pandas as pd

from index_platform.backtest.runner import run_strategy_backtest
from index_platform.config import BacktestConfig, load_backtest_config
from index_platform.config.backtest_config import _load_simple_yaml
from index_platform.storage import load_backtest_result


def expand_parameter_grid(parameter_grid: dict[str, list[object]]) -> list[dict[str, object]]:
    """Expand a parameter grid into concrete parameter dictionaries."""
    if not parameter_grid:
        return [{}]
    keys = list(parameter_grid)
    values = []
    for key in keys:
        options = parameter_grid[key]
        if not isinstance(options, list) or not options:
            raise ValueError(f"Parameter grid value must be a non-empty list: {key}")
        values.append(options)
    return [dict(zip(keys, combination, strict=True)) for combination in product(*values)]


def run_parameter_sweep(
    config: BacktestConfig,
    parameter_grid: dict[str, list[object]],
    data_dir: str | Path = "data/parquet",
    output_dir: str | Path = "outputs/backtests",
    runner: Callable[..., str] = run_strategy_backtest,
) -> pd.DataFrame:
    """Run a batch of backtests and summarize each run's metrics."""
    rows: list[dict[str, object]] = []
    for params in expand_parameter_grid(parameter_grid):
        strategy_params = {**config.strategy_params, **params}
        run_id = runner(
            config.strategy_name,
            config.symbols,
            data_dir=data_dir,
            output_dir=output_dir,
            start_date=config.start_date,
            end_date=config.end_date,
            initial_nav=config.initial_nav,
            strategy_params=strategy_params,
        )
        result = load_backtest_result(output_dir, run_id)
        row = {"run_id": run_id, **strategy_params, **result["metrics"]}
        rows.append(row)
    return pd.DataFrame(rows)


def load_sweep_config(path: str | Path) -> tuple[BacktestConfig, dict[str, list[object]]]:
    """Load a sweep config file containing a parameter_grid section."""
    raw = _load_simple_yaml(Path(path))
    parameter_grid = raw.pop("parameter_grid", {})
    if not isinstance(parameter_grid, dict):
        raise ValueError("parameter_grid must be a mapping.")
    config = load_backtest_config(path)
    return config, dict(parameter_grid)
