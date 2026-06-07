"""Filesystem storage for reproducible backtest runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd


def generate_run_id(prefix: str = "bt") -> str:
    """Generate a unique backtest run identifier."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{timestamp}_{uuid4().hex[:8]}"


def save_backtest_result(
    base_dir: str | Path,
    config: dict[str, object],
    nav: pd.DataFrame,
    positions: pd.DataFrame,
    orders: pd.DataFrame | None,
    metrics: dict[str, float],
    run_id: str | None = None,
) -> str:
    """Save a backtest run and return its run_id."""
    resolved_run_id = run_id or generate_run_id()
    run_dir = Path(base_dir) / resolved_run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    (run_dir / "config.yaml").write_text(_to_yaml(config), encoding="utf-8")
    nav.to_parquet(run_dir / "nav.parquet", index=False)
    positions.to_parquet(run_dir / "positions.parquet", index=False)
    _orders_or_empty(orders).to_parquet(run_dir / "orders.parquet", index=False)
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    return resolved_run_id


def load_backtest_result(base_dir: str | Path, run_id: str) -> dict[str, object]:
    """Load saved backtest tables and metrics for a run_id."""
    run_dir = Path(base_dir) / run_id
    if not run_dir.exists():
        raise FileNotFoundError(f"Backtest run not found: {run_id}")
    return {
        "run_id": run_id,
        "run_dir": run_dir,
        "config_text": (run_dir / "config.yaml").read_text(encoding="utf-8"),
        "nav": pd.read_parquet(run_dir / "nav.parquet"),
        "positions": pd.read_parquet(run_dir / "positions.parquet"),
        "orders": pd.read_parquet(run_dir / "orders.parquet"),
        "metrics": json.loads((run_dir / "metrics.json").read_text(encoding="utf-8")),
    }


def _orders_or_empty(orders: pd.DataFrame | None) -> pd.DataFrame:
    if orders is not None:
        return orders
    return pd.DataFrame(columns=["date", "symbol", "trade_value", "price", "quantity", "cost"])


def _to_yaml(value: object, indent: int = 0) -> str:
    lines = _yaml_lines(value, indent)
    return "\n".join(lines) + "\n"


def _yaml_lines(value: object, indent: int) -> list[str]:
    space = " " * indent
    if isinstance(value, dict):
        lines: list[str] = []
        for key, item in value.items():
            if isinstance(item, dict | list):
                lines.append(f"{space}{key}:")
                lines.extend(_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{space}{key}: {_yaml_scalar(item)}")
        return lines
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                lines.append(f"{space}-")
                lines.extend(_yaml_lines(item, indent + 2))
            else:
                lines.append(f"{space}- {_yaml_scalar(item)}")
        return lines
    return [f"{space}{_yaml_scalar(value)}"]


def _yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    text = str(value)
    if not text or any(char in text for char in [":", "#", "\n", "'", '"']):
        return json.dumps(text, ensure_ascii=False)
    return text
