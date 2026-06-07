"""Index registry loading and filtering."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "configs" / "indices.yaml"
REQUIRED_FIELDS = {"symbol", "name", "market", "currency", "source"}


@dataclass(frozen=True)
class IndexInfo:
    """Metadata for a supported index."""

    symbol: str
    name: str
    market: str
    currency: str
    source: str


def load_indices(path: str | Path | None = None) -> list[IndexInfo]:
    """Load all indices from the registry file."""
    registry_path = Path(path) if path is not None else DEFAULT_REGISTRY_PATH
    raw_indices = _load_simple_indices_yaml(registry_path)
    return [_build_index_info(item) for item in raw_indices]


def filter_indices_by_market(market: str, path: str | Path | None = None) -> list[IndexInfo]:
    """Load indices and return only entries for the requested market."""
    target_market = market.upper()
    return [index for index in load_indices(path) if index.market.upper() == target_market]


def _build_index_info(raw: dict[str, str]) -> IndexInfo:
    missing_fields = REQUIRED_FIELDS - raw.keys()
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"Index registry item is missing required fields: {missing}")

    return IndexInfo(
        symbol=raw["symbol"],
        name=raw["name"],
        market=raw["market"],
        currency=raw["currency"],
        source=raw["source"],
    )


def _load_simple_indices_yaml(path: Path) -> list[dict[str, str]]:
    """Parse the simple YAML shape used by configs/indices.yaml."""
    if not path.exists():
        raise FileNotFoundError(f"Index registry file not found: {path}")

    indices: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    in_indices_section = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line == "indices:":
            in_indices_section = True
            continue

        if not in_indices_section:
            continue

        if line.startswith("- "):
            if current is not None:
                indices.append(current)
            current = {}
            item_line = line[2:].strip()
            if item_line:
                key, value = _parse_key_value(item_line)
                current[key] = value
            continue

        if current is None:
            raise ValueError(f"Invalid index registry line before item: {raw_line}")

        key, value = _parse_key_value(line)
        current[key] = value

    if current is not None:
        indices.append(current)

    return indices


def _parse_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise ValueError(f"Invalid index registry line: {line}")

    key, value = line.split(":", 1)
    return key.strip(), value.strip()
