"""Report CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from index_platform.report import build_report_markdown


def show_report(
    metrics_file: Path | None = typer.Argument(None, help="Path to a metrics JSON file."),
    run_id: str | None = typer.Option(None, "--run-id", help="Saved backtest run_id."),
    runs_dir: Path = typer.Option(Path("outputs/backtests"), "--runs-dir", help="Backtest output directory."),
) -> None:
    """Show a saved backtest report, preferring run_id when provided."""
    if run_id is not None:
        typer.echo(build_report_markdown(runs_dir, run_id))
        return

    if metrics_file is None:
        raise typer.BadParameter("Provide --run-id or a metrics JSON file.")
    if not metrics_file.exists():
        raise typer.BadParameter(f"Metrics file not found: {metrics_file}")

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    for key, value in metrics.items():
        typer.echo(f"{key}: {value}")
