"""Build text reports from saved backtest runs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from index_platform.storage.backtest_store import load_backtest_result


METRIC_LABELS = {
    "total_return": "Total Return",
    "annualized_return": "Annualized Return",
    "annualized_volatility": "Annualized Volatility",
    "max_drawdown": "Max Drawdown",
    "sharpe_ratio": "Sharpe Ratio",
    "calmar_ratio": "Calmar Ratio",
}


def build_report(base_dir: str | Path, run_id: str) -> dict[str, object]:
    """Read a saved run and return normalized report fields."""
    result = load_backtest_result(base_dir, run_id)
    nav = result["nav"]
    orders = result["orders"]
    metrics = result["metrics"]

    if not isinstance(nav, pd.DataFrame) or nav.empty:
        raise ValueError("Saved NAV must not be empty.")
    if "date" in nav.columns:
        dates = pd.to_datetime(nav["date"])
        start_date = dates.min().date().isoformat()
        end_date = dates.max().date().isoformat()
    else:
        start_date = ""
        end_date = ""

    return {
        "run_id": run_id,
        "strategy": _extract_config_value(str(result["config_text"]), "strategy") or "unknown",
        "start_date": start_date,
        "end_date": end_date,
        "initial_nav": float(nav["nav"].iloc[0]),
        "final_nav": float(nav["nav"].iloc[-1]),
        "trade_count": int(len(orders)) if isinstance(orders, pd.DataFrame) else 0,
        "metrics": metrics,
    }


def build_report_markdown(base_dir: str | Path, run_id: str) -> str:
    """Build a Markdown report for a saved backtest run."""
    report = build_report(base_dir, run_id)
    metrics = report["metrics"]
    lines = [
        f"# Backtest Report: {report['run_id']}",
        "",
        f"- Strategy: {report['strategy']}",
        f"- Period: {report['start_date']} to {report['end_date']}",
        f"- Initial NAV: {report['initial_nav']:.6f}",
        f"- Final NAV: {report['final_nav']:.6f}",
        f"- Trade Count: {report['trade_count']}",
        "",
        "## Metrics",
    ]
    for key, label in METRIC_LABELS.items():
        value = metrics.get(key) if isinstance(metrics, dict) else None
        if isinstance(value, int | float):
            lines.append(f"- {label}: {value:.6f}")
        else:
            lines.append(f"- {label}: {value}")
    return "\n".join(lines) + "\n"


def _extract_config_value(config_text: str, key: str) -> str | None:
    prefix = f"{key}:"
    for line in config_text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip().strip('"')
    return None
