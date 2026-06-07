"""Data CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform.data import read_price_csv
from index_platform.storage import load_price_data, save_price_data


def import_price_data(
    csv_file: Path = typer.Argument(..., help="Path to a daily price CSV file."),
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
) -> None:
    """Import a local daily price CSV into Parquet storage."""
    prices = read_price_csv(csv_file)
    output_file = save_price_data(prices, data_dir)
    typer.echo(f"Imported {len(prices)} rows into {output_file}")


def show_data_status(
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
) -> None:
    """Show basic local price data status."""
    try:
        prices = load_price_data(data_dir)
    except FileNotFoundError:
        typer.echo(f"No local price data found in {data_dir}")
        return

    symbols = ", ".join(sorted(prices["symbol"].unique()))
    start_date = prices["date"].min().date()
    end_date = prices["date"].max().date()
    typer.echo(f"Rows: {len(prices)}")
    typer.echo(f"Symbols: {symbols}")
    typer.echo(f"Date range: {start_date} to {end_date}")

