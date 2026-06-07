"""Backtest YAML configuration schema and loader."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_BACKTEST_FIELDS = {"strategy_name", "symbols"}


@dataclass(frozen=True)
class BacktestConfig:
    """Minimal reproducible backtest configuration."""

    strategy_name: str
    symbols: list[str]
    start_date: str | None = None
    end_date: str | None = None
    initial_nav: float = 1.0
    benchmark: str | None = None
    rebalance_frequency: str | int | None = None
    transaction_cost: dict[str, float] = field(default_factory=dict)
    execution_rule: str = "next_close"
    strategy_params: dict[str, object] = field(default_factory=dict)


def load_backtest_config(path: str | Path) -> BacktestConfig:
    """Load a backtest config from a small YAML file."""
    raw = _load_simple_yaml(Path(path))
    missing = REQUIRED_BACKTEST_FIELDS - raw.keys()
    if missing:
        raise ValueError(f"Backtest config is missing required fields: {', '.join(sorted(missing))}")

    symbols = raw["symbols"]
    if isinstance(symbols, str):
        symbols = [symbols]
    if not isinstance(symbols, list) or not symbols:
        raise ValueError("symbols must be a non-empty list.")

    initial_nav = raw.get("initial_nav", raw.get("initial_capital", 1.0))
    return BacktestConfig(
        strategy_name=str(raw["strategy_name"]),
        symbols=[str(symbol) for symbol in symbols],
        start_date=_optional_str(raw.get("start_date")),
        end_date=_optional_str(raw.get("end_date")),
        initial_nav=float(initial_nav),
        benchmark=_optional_str(raw.get("benchmark")),
        rebalance_frequency=raw.get("rebalance_frequency"),
        transaction_cost=_as_float_dict(raw.get("transaction_cost", {})),
        execution_rule=str(raw.get("execution_rule", "next_close")),
        strategy_params=dict(raw.get("strategy_params", {})),
    )


def _load_simple_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Backtest config file not found: {path}")
    root: dict[str, object] = {}
    current_dict: dict[str, object] | None = None
    current_key: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            key, value = _parse_key_value(line)
            if value == "":
                current_dict = {}
                root[key] = current_dict
                current_key = key
            else:
                root[key] = _parse_scalar_or_list(value)
                current_dict = None
                current_key = None
            continue
        if current_dict is None or current_key is None:
            raise ValueError(f"Invalid indented config line: {raw_line}")
        key, value = _parse_key_value(line)
        current_dict[key] = _parse_scalar_or_list(value)

    return root


def _parse_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Invalid config line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar_or_list(value: str) -> object:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(item.strip()) for item in inner.split(",")]
    return _parse_scalar(value)


def _parse_scalar(value: str) -> object:
    text = value.strip().strip('"').strip("'")
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if text.lower() in {"null", "none"}:
        return None
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _as_float_dict(value: object) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("transaction_cost must be a mapping.")
    return {str(key): float(item) for key, item in value.items()}
