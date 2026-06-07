"""Command-line entry point for IndexPlatform."""

from __future__ import annotations

from pathlib import Path

import typer

from index_platform import __version__
from index_platform.cli import backtest_cmd, data_cmd, monitor_cmd, report_cmd
from index_platform.universe import filter_indices_by_market, load_indices

app = typer.Typer(help="IndexPlatform research and backtesting CLI.", no_args_is_help=True)
data_app = typer.Typer(help="Local price data commands.")
backtest_app = typer.Typer(help="Backtest commands.")
report_app = typer.Typer(help="Report commands.")
monitor_app = typer.Typer(help="Run monitor commands.")


@app.callback()
def root(
    version: bool = typer.Option(False, "--version", help="Show CLI version."),
) -> None:
    """IndexPlatform research and backtesting CLI."""
    if version:
        typer.echo(f"idx {__version__}")
        raise typer.Exit()


@app.command("list-indices")
def list_indices(
    market: str | None = typer.Option(None, "--market", "-m", help="Filter by market."),
    registry: Path | None = typer.Option(None, "--registry", help="Path to indices.yaml."),
) -> None:
    """List registered indices."""
    indices = filter_indices_by_market(market, registry) if market else load_indices(registry)
    for index in indices:
        typer.echo(f"{index.symbol}\t{index.market}\t{index.currency}\t{index.name}")


data_app.command("import")(data_cmd.import_price_data)
data_app.command("status")(data_cmd.show_data_status)
backtest_app.command("run")(backtest_cmd.run_buy_hold_backtest)
backtest_app.command("sweep")(backtest_cmd.run_sweep)
report_app.command("show")(report_cmd.show_report)
monitor_app.command("status")(monitor_cmd.show_run_states)

app.add_typer(data_app, name="data")
app.add_typer(backtest_app, name="backtest")
app.add_typer(report_app, name="report")
app.add_typer(monitor_app, name="monitor")


def build_parser() -> typer.Typer:
    """Return the Typer app for tests and integrations."""
    return app


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    command = typer.main.get_command(app)
    try:
        command.main(args=argv, prog_name="idx", standalone_mode=False)
    except typer.Exit as exc:
        return int(exc.exit_code)
    except Exception as exc:
        if exc.__class__.__name__ == "NoArgsIsHelpError":
            return 0
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
