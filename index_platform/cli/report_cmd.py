"""Report CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer


def show_report(
    metrics_file: Path = typer.Argument(..., help="Path to a metrics JSON file."),
) -> None:
    """Show metrics from a saved JSON report file."""
    if not metrics_file.exists():
        raise typer.BadParameter(f"Metrics file not found: {metrics_file}")

    metrics = json.loads(metrics_file.read_text(encoding="utf-8"))
    for key, value in metrics.items():
        typer.echo(f"{key}: {value}")

