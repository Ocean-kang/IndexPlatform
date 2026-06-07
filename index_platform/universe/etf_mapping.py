"""Index-to-ETF mapping registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_ETF_MAPPING_PATH = Path("configs/etf_mapping.yaml")
REQUIRED_ETF_FIELDS = {
    "index_symbol",
    "etf_symbol",
    "etf_name",
    "market",
    "currency",
    "expense_ratio",
    "source",
}


@dataclass(frozen=True)
class ETFMapping:
    """Metadata for one index-to-ETF mapping."""

    index_symbol: str
    etf_symbol: str
    etf_name: str
    market: str
    currency: str
    expense_ratio: float
    source: str


def load_etf_mappings(path: str | Path | None = None) -> list[ETFMapping]:
    """Load ETF mappings from a small YAML list file."""
    mapping_path = Path(path) if path is not None else DEFAULT_ETF_MAPPING_PATH
    rows = _load_yaml_list(mapping_path)
    mappings: list[ETFMapping] = []
    for row in rows:
        missing = REQUIRED_ETF_FIELDS - row.keys()
        if missing:
            raise ValueError(f"ETF mapping is missing required fields: {', '.join(sorted(missing))}")
        mappings.append(
            ETFMapping(
                index_symbol=str(row["index_symbol"]),
                etf_symbol=str(row["etf_symbol"]),
                etf_name=str(row["etf_name"]),
                market=str(row["market"]),
                currency=str(row["currency"]),
                expense_ratio=float(row["expense_ratio"]),
                source=str(row["source"]),
            )
        )
    return mappings


def find_etfs_by_index(index_symbol: str, path: str | Path | None = None) -> list[ETFMapping]:
    """Return ETF mappings for an index symbol."""
    return [mapping for mapping in load_etf_mappings(path) if mapping.index_symbol == index_symbol]


def filter_etfs_by_market(market: str, path: str | Path | None = None) -> list[ETFMapping]:
    """Return ETF mappings listed in the requested market."""
    return [mapping for mapping in load_etf_mappings(path) if mapping.market == market]


def _load_yaml_list(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        raise FileNotFoundError(f"ETF mapping file not found: {path}")
    rows: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = raw_line.strip()
        if line.startswith("- "):
            current = {}
            rows.append(current)
            line = line[2:].strip()
            if not line:
                continue
        if current is None:
            raise ValueError(f"Invalid ETF mapping line: {raw_line}")
        key, value = _parse_key_value(line)
        current[key] = _parse_scalar(value)
    return rows


def _parse_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Invalid ETF mapping line: {line}")
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _parse_scalar(value: str) -> object:
    text = value.strip().strip('"').strip("'")
    try:
        if "." in text:
            return float(text)
        return int(text)
    except ValueError:
        return text
