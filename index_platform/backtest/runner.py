"""Reusable backtest orchestration helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.backtest.engine import run_backtest, run_multi_asset_backtest
from index_platform.metrics import calculate_performance_metrics
from index_platform.monitor import append_run_log, update_run_state
from index_platform.storage import load_price_data
from index_platform.storage.backtest_store import generate_run_id, save_backtest_result
from index_platform.strategy import BuyAndHoldStrategy, MomentumRotationStrategy, MovingAverageStrategy


def run_strategy_backtest(
    strategy_name: str,
    symbols: list[str],
    data_dir: str | Path = "data/parquet",
    output_dir: str | Path = "outputs/backtests",
    start_date: str | None = None,
    end_date: str | None = None,
    initial_nav: float = 1.0,
    strategy_params: dict[str, object] | None = None,
    state_dir: str | Path | None = None,
    log_dir: str | Path | None = None,
) -> str:
    """Run a supported strategy, save the result, and return its run_id."""
    if not symbols:
        raise ValueError("symbols must not be empty.")
    strategy_params = strategy_params or {}
    strategy_name = strategy_name.strip().lower()
    run_id = generate_run_id()
    resolved_state_dir = Path(state_dir) if state_dir is not None else Path(output_dir).parent / "run_state"
    resolved_log_dir = Path(log_dir) if log_dir is not None else Path(output_dir).parent / "logs"
    update_run_state(run_id, "running", resolved_state_dir)
    append_run_log(run_id, f"Started {strategy_name} backtest.", resolved_log_dir)

    try:
        prices = _load_symbols(data_dir, symbols, start_date, end_date)
        if strategy_name == "buy_hold":
            result = run_backtest(prices, BuyAndHoldStrategy())
            positions = result[["date", "symbol", "position"]]
            orders = pd.DataFrame(columns=["date", "symbol", "trade_value", "price", "quantity", "cost"])
            nav = result[["date", "nav"]]
        elif strategy_name == "moving_average":
            strategy = MovingAverageStrategy(
                window=int(strategy_params.get("window", 20)),
                hold_when_above=bool(strategy_params.get("hold_when_above", True)),
                execution_delay=int(strategy_params.get("execution_delay", 1)),
            )
            result = run_backtest(prices, strategy)
            positions = result[["date", "symbol", "position"]]
            orders = pd.DataFrame(columns=["date", "symbol", "trade_value", "price", "quantity", "cost"])
            nav = result[["date", "nav"]]
        elif strategy_name == "momentum":
            strategy = MomentumRotationStrategy(
                lookback=int(strategy_params.get("lookback", 20)),
                top_k=int(strategy_params.get("top_k", 1)),
                rebalance_frequency=int(strategy_params.get("rebalance_frequency", 20)),
                execution_delay=int(strategy_params.get("execution_delay", 1)),
            )
            weights = strategy.generate_target_weights(prices)
            portfolio = run_multi_asset_backtest(prices, weights, initial_nav=initial_nav)
            nav = portfolio["nav"]
            positions = portfolio["positions"]
            orders = portfolio["orders"]
        else:
            raise ValueError(f"Unsupported strategy: {strategy_name}")

        metrics = calculate_performance_metrics(nav["nav"])
        config = {
            "strategy": strategy_name,
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "initial_nav": initial_nav,
            "strategy_params": strategy_params,
        }
        save_backtest_result(output_dir, config, nav, positions, orders, metrics, run_id=run_id)
        update_run_state(run_id, "success", resolved_state_dir)
        append_run_log(run_id, "Backtest finished successfully.", resolved_log_dir)
        return run_id
    except Exception as exc:
        update_run_state(run_id, "failed", resolved_state_dir, message=str(exc))
        append_run_log(run_id, f"Backtest failed: {exc}", resolved_log_dir)
        raise


def _load_symbols(
    data_dir: str | Path,
    symbols: list[str],
    start_date: str | None,
    end_date: str | None,
) -> pd.DataFrame:
    frames = [load_price_data(data_dir, symbol=symbol, start_date=start_date, end_date=end_date) for symbol in symbols]
    prices = pd.concat(frames, ignore_index=True)
    if prices.empty:
        raise ValueError("No price rows found for selected symbols.")
    return prices
