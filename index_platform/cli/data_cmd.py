"""Data CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform.data import read_price_csv
from index_platform.data.fetcher import fetch_price_data
from index_platform.data.quality import check_daily_price_quality, summarize_data_status
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
    summary = summarize_data_status(prices)
    issues = check_daily_price_quality(prices)

    typer.echo(f"Rows: {len(prices)}")
    typer.echo(f"Symbols: {symbols}")
    typer.echo(f"Date range: {start_date} to {end_date}")
    typer.echo("Per-symbol status:")
    for row in summary.itertuples(index=False):
        typer.echo(
            f"- {row.symbol}: rows={row.rows}, date_range={row.start_date} to {row.end_date}, "
            f"quality_issues={row.quality_issues}"
        )
    if issues:
        typer.echo("Quality issues:")
        for issue in issues:
            typer.echo(f"- {issue.rule}: {issue.message} rows={issue.rows}")
    else:
        typer.echo("Quality issues: none")


def fetch_online_price_data(
    symbol: str | None = typer.Option(None, "--symbol", help="Registered index symbol to fetch."),
    market: str | None = typer.Option(None, "--market", help="Fetch all registered indices in this market."),
    fetch_all: bool = typer.Option(False, "--all", help="Fetch all registered indices."),
    start_date: str | None = typer.Option(None, "--start-date", help="Start date, for example 2010-01-01."),
    end_date: str | None = typer.Option(None, "--end-date", help="End date, for example 2026-06-07."),
    data_dir: Path = typer.Option(Path("data/parquet"), "--data-dir", help="Local Parquet data directory."),
    registry: Path | None = typer.Option(None, "--registry", help="Path to indices.yaml."),
) -> None:
    """Fetch registered index daily prices from online data sources."""
    try:
        result = fetch_price_data(
            data_dir=data_dir,
            start_date=start_date,
            end_date=end_date,
            symbol=symbol,
            market=market,
            fetch_all=fetch_all,
            registry=registry,
        )
    except ValueError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo(f"Success: {len(result.success_symbols)}")
    typer.echo(f"Failed: {len(result.failures)}")
    if result.output_file is not None:
        typer.echo(f"Fetched rows: {result.rows}")
        typer.echo(f"Saved to: {result.output_file}")
    else:
        typer.echo("No data was saved.")

    if result.failures:
        typer.echo("Failures:")
        for failure in result.failures:
            typer.echo(f"- {failure.symbol}: {failure.reason}")

    if not result.success_symbols:
        raise typer.Exit(code=1)
