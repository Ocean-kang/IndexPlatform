"""Backtest CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform.backtest import run_backtest
from index_platform.metrics import calculate_performance_metrics
from index_platform.storage import load_price_data
from index_platform.strategy import BuyAndHoldStrategy


def run_buy_hold_backtest(
    symbol: str = typer.Argument(..., help="Index symbol to backtest."),
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
    start_date: str | None = typer.Option(None, "--start-date", help="Inclusive start date."),
    end_date: str | None = typer.Option(None, "--end-date", help="Inclusive end date."),
) -> None:
    """Run the first buy-and-hold backtest."""
    prices = load_price_data(data_dir, symbol=symbol, start_date=start_date, end_date=end_date)
    result = run_backtest(prices, BuyAndHoldStrategy())
    metrics = calculate_performance_metrics(result["nav"])

    typer.echo(f"Strategy: buy_hold")
    typer.echo(f"Symbol: {symbol}")
    typer.echo(f"Final NAV: {result['nav'].iloc[-1]:.6f}")
    typer.echo(f"Total Return: {metrics['total_return']:.6f}")
    typer.echo(f"Max Drawdown: {metrics['max_drawdown']:.6f}")

