"""Backtest CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform.backtest import run_backtest
from index_platform.backtest.runner import run_strategy_backtest
from index_platform.config import load_backtest_config
from index_platform.metrics import calculate_performance_metrics
from index_platform.research.parameter_sweep import load_sweep_config, run_parameter_sweep
from index_platform.storage import load_price_data
from index_platform.strategy import BuyAndHoldStrategy


def run_buy_hold_backtest(
    symbol: str | None = typer.Argument(None, help="Index symbol to backtest."),
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
    start_date: str | None = typer.Option(None, "--start-date", help="Inclusive start date."),
    end_date: str | None = typer.Option(None, "--end-date", help="Inclusive end date."),
    config: Path | None = typer.Option(None, "--config", help="YAML backtest config file."),
    output_dir: Path = typer.Option(Path("outputs/backtests"), "--output-dir", help="Saved backtest output directory."),
) -> None:
    """Run the first buy-and-hold backtest."""
    if config is not None:
        loaded = load_backtest_config(config)
        run_id = run_strategy_backtest(
            loaded.strategy_name,
            loaded.symbols,
            data_dir=data_dir,
            output_dir=output_dir,
            start_date=loaded.start_date,
            end_date=loaded.end_date,
            initial_nav=loaded.initial_nav,
            strategy_params=loaded.strategy_params,
        )
        typer.echo(f"Run ID: {run_id}")
        return
    if symbol is None:
        raise typer.BadParameter("symbol is required unless --config is provided.")
    prices = load_price_data(data_dir, symbol=symbol, start_date=start_date, end_date=end_date)
    result = run_backtest(prices, BuyAndHoldStrategy())
    metrics = calculate_performance_metrics(result["nav"])

    typer.echo(f"Strategy: buy_hold")
    typer.echo(f"Symbol: {symbol}")
    typer.echo(f"Final NAV: {result['nav'].iloc[-1]:.6f}")
    typer.echo(f"Total Return: {metrics['total_return']:.6f}")
    typer.echo(f"Max Drawdown: {metrics['max_drawdown']:.6f}")


def run_sweep(
    config: Path = typer.Option(..., "--config", help="YAML sweep config file."),
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
    output_dir: Path = typer.Option(Path("outputs/backtests"), "--output-dir", help="Saved backtest output directory."),
) -> None:
    """Run a parameter sweep from YAML config."""
    loaded, parameter_grid = load_sweep_config(config)
    summary = run_parameter_sweep(loaded, parameter_grid, data_dir=data_dir, output_dir=output_dir)
    typer.echo(summary.to_csv(index=False).strip())
