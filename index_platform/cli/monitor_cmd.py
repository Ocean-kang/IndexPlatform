"""Monitor CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform.monitor import list_run_states


def show_run_states(
    state_dir: Path = typer.Option(Path("outputs/run_state"), "--state-dir", help="Run state directory."),
) -> None:
    """Show saved run states."""
    states = list_run_states(state_dir)
    if not states:
        typer.echo(f"No run states found in {state_dir}")
        return
    for item in states:
        typer.echo(f"{item['run_id']}\t{item['state']}\t{item.get('updated_at', '')}\t{item.get('message', '')}")
