"""Walk-forward validation helpers."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable

import pandas as pd

from index_platform.backtest.runner import run_strategy_backtest
from index_platform.config import BacktestConfig
from index_platform.storage import load_backtest_result


def generate_walk_forward_windows(
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
    train_days: int,
    test_days: int,
    step_days: int | None = None,
) -> list[dict[str, str]]:
    """Generate rolling train/test windows."""
    if train_days <= 0 or test_days <= 0:
        raise ValueError("train_days and test_days must be positive.")
    step_days = step_days or test_days
    if step_days <= 0:
        raise ValueError("step_days must be positive.")

    start = pd.Timestamp(start_date).normalize()
    end = pd.Timestamp(end_date).normalize()
    windows: list[dict[str, str]] = []
    train_start = start
    while True:
        train_end = train_start + pd.Timedelta(days=train_days - 1)
        test_start = train_end + pd.Timedelta(days=1)
        test_end = test_start + pd.Timedelta(days=test_days - 1)
        if test_end > end:
            break
        windows.append(
            {
                "train_start": train_start.date().isoformat(),
                "train_end": train_end.date().isoformat(),
                "test_start": test_start.date().isoformat(),
                "test_end": test_end.date().isoformat(),
            }
        )
        train_start += pd.Timedelta(days=step_days)
    return windows


def run_walk_forward(
    config: BacktestConfig,
    train_days: int,
    test_days: int,
    step_days: int | None = None,
    data_dir: str | Path = "data/parquet",
    output_dir: str | Path = "outputs/backtests",
    runner: Callable[..., str] = run_strategy_backtest,
) -> pd.DataFrame:
    """Run independent backtests over each out-of-sample window."""
    if config.start_date is None or config.end_date is None:
        raise ValueError("Walk-forward config requires start_date and end_date.")

    rows: list[dict[str, object]] = []
    windows = generate_walk_forward_windows(config.start_date, config.end_date, train_days, test_days, step_days)
    for number, window in enumerate(windows, start=1):
        segment_config = replace(config, start_date=window["test_start"], end_date=window["test_end"])
        run_id = runner(
            segment_config.strategy_name,
            segment_config.symbols,
            data_dir=data_dir,
            output_dir=output_dir,
            start_date=segment_config.start_date,
            end_date=segment_config.end_date,
            initial_nav=segment_config.initial_nav,
            strategy_params=segment_config.strategy_params,
        )
        result = load_backtest_result(output_dir, run_id)
        rows.append({"window": number, "run_id": run_id, **window, **result["metrics"]})
    return pd.DataFrame(rows)
