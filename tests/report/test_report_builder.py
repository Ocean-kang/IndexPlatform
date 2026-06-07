from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from index_platform.cli.main import app
from index_platform.report.builder import build_report, build_report_markdown
from index_platform.storage.backtest_store import save_backtest_result


runner = CliRunner()


def _save_run(tmp_path: Path) -> str:
    return save_backtest_result(
        tmp_path,
        config={"strategy": "momentum", "symbols": ["AAA", "BBB"]},
        nav=pd.DataFrame({"date": pd.date_range("2024-01-02", periods=2), "nav": [1.0, 1.2]}),
        positions=pd.DataFrame(
            {
                "date": [pd.Timestamp("2024-01-02")],
                "symbol": ["AAA"],
                "market_value": [1.0],
                "weight": [1.0],
            }
        ),
        orders=pd.DataFrame(
            {
                "date": [pd.Timestamp("2024-01-02")],
                "symbol": ["AAA"],
                "trade_value": [1.0],
                "price": [100.0],
                "quantity": [0.01],
                "cost": [0.0],
            }
        ),
        metrics={
            "total_return": 0.2,
            "annualized_return": 1.0,
            "annualized_volatility": 0.3,
            "max_drawdown": -0.1,
            "sharpe_ratio": 2.0,
            "calmar_ratio": 10.0,
        },
        run_id="report_run",
    )


def test_build_report_reads_saved_result_by_run_id(tmp_path: Path) -> None:
    run_id = _save_run(tmp_path)

    report = build_report(tmp_path, run_id)

    assert report["strategy"] == "momentum"
    assert report["start_date"] == "2024-01-02"
    assert report["end_date"] == "2024-01-03"
    assert report["final_nav"] == 1.2
    assert report["trade_count"] == 1
    assert report["metrics"]["total_return"] == 0.2


def test_build_report_markdown_contains_core_metrics(tmp_path: Path) -> None:
    run_id = _save_run(tmp_path)

    markdown = build_report_markdown(tmp_path, run_id)

    assert "# Backtest Report: report_run" in markdown
    assert "Strategy: momentum" in markdown
    assert "Total Return: 0.200000" in markdown
    assert "Final NAV: 1.200000" in markdown


def test_report_show_cli_supports_run_id(tmp_path: Path) -> None:
    _save_run(tmp_path)

    result = runner.invoke(app, ["report", "show", "--run-id", "report_run", "--runs-dir", str(tmp_path)])

    assert result.exit_code == 0
    assert "Backtest Report: report_run" in result.output
    assert "Sharpe Ratio: 2.000000" in result.output
