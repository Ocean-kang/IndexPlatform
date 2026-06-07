import json
from pathlib import Path

from typer.testing import CliRunner

from index_platform.cli.main import app, build_parser, main


runner = CliRunner()


def _write_price_csv(path: Path) -> None:
    path.write_text(
        """date,symbol,open,high,low,close,volume,amount,currency,source
2024-01-02,000300.SH,100,100,100,100,1000,100000,CNY,toy
2024-01-03,000300.SH,110,110,110,110,1000,110000,CNY,toy
""",
        encoding="utf-8",
    )


def test_cli_help_is_available() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "IndexPlatform research and backtesting CLI." in result.output
    assert build_parser() is app


def test_cli_main_returns_success() -> None:
    assert main([]) == 0


def test_list_indices_command() -> None:
    result = runner.invoke(app, ["list-indices", "--market", "US"])

    assert result.exit_code == 0
    assert "SPX.US" in result.output
    assert "000300.SH" not in result.output


def test_data_import_and_status_commands(tmp_path: Path) -> None:
    csv_file = tmp_path / "prices.csv"
    data_dir = tmp_path / "parquet"
    _write_price_csv(csv_file)

    import_result = runner.invoke(app, ["data", "import", str(csv_file), "--data-dir", str(data_dir)])
    status_result = runner.invoke(app, ["data", "status", "--data-dir", str(data_dir)])

    assert import_result.exit_code == 0
    assert "Imported 2 rows" in import_result.output
    assert status_result.exit_code == 0
    assert "Rows: 2" in status_result.output
    assert "000300.SH" in status_result.output


def test_data_fetch_help_is_available() -> None:
    result = runner.invoke(app, ["data", "fetch", "--help"])

    assert result.exit_code == 0
    assert "--symbol" in result.output
    assert "--market" in result.output
    assert "--all" in result.output


def test_backtest_run_command(tmp_path: Path) -> None:
    csv_file = tmp_path / "prices.csv"
    data_dir = tmp_path / "parquet"
    _write_price_csv(csv_file)
    runner.invoke(app, ["data", "import", str(csv_file), "--data-dir", str(data_dir)])

    result = runner.invoke(app, ["backtest", "run", "000300.SH", "--data-dir", str(data_dir)])

    assert result.exit_code == 0
    assert "Strategy: buy_hold" in result.output
    assert "Final NAV: 1.100000" in result.output


def test_report_show_command(tmp_path: Path) -> None:
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text(json.dumps({"total_return": 0.1}), encoding="utf-8")

    result = runner.invoke(app, ["report", "show", str(metrics_file)])

    assert result.exit_code == 0
    assert "total_return: 0.1" in result.output


def test_monitor_status_command(tmp_path: Path) -> None:
    state_dir = tmp_path / "run_state"
    state_dir.mkdir()
    (state_dir / "run_1.json").write_text(
        '{"run_id": "run_1", "state": "success", "updated_at": "2024-01-01T00:00:00Z", "message": ""}',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["monitor", "status", "--state-dir", str(state_dir)])

    assert result.exit_code == 0
    assert "run_1" in result.output
    assert "success" in result.output
