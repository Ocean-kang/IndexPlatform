"""Online daily price fetching orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Protocol

import pandas as pd

from index_platform.data.adapters.akshare_adapter import AkShareIndexAdapter
from index_platform.data.adapters.hk_adapter import HongKongIndexAdapter
from index_platform.data.adapters.yfinance_adapter import YFinanceAdapter
from index_platform.data.validators import normalize_daily_price_data
from index_platform.storage import load_price_data, save_price_data
from index_platform.universe import IndexInfo, filter_indices_by_market, load_indices


INSTALL_OPTIONAL_DATA_DEPS_MESSAGE = "Install data source dependencies with: python -m pip install akshare yfinance"

CN_SYMBOL_MAP = {
    "000300.SH": "sh000300",
    "000905.SH": "sh000905",
    "000852.SH": "sh000852",
    "000016.SH": "sh000016",
    "399006.SZ": "sz399006",
}

YFINANCE_SYMBOL_MAP = {
    "SPX.US": "^GSPC",
    "IXIC.US": "^IXIC",
    "NDX.US": "^NDX",
    "DJI.US": "^DJI",
    "HSI.HK": "^HSI",
    "HSCEI.HK": "^HSCE",
    "HSTECH.HK": "HSTECH.HK",
}


class DailyPriceAdapter(Protocol):
    """Small shared adapter surface used by the fetcher."""

    def fetch_daily(self, symbol: str, start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
        """Fetch daily prices for a data-source symbol."""


@dataclass(frozen=True)
class FetchFailure:
    """A failed symbol download."""

    symbol: str
    reason: str


@dataclass(frozen=True)
class FetchResult:
    """Summary of a fetch-and-save operation."""

    output_file: Path | None
    rows: int
    success_symbols: list[str]
    failures: list[FetchFailure]


def fetch_price_data(
    *,
    data_dir: str | Path,
    start_date: str | None = None,
    end_date: str | None = None,
    symbol: str | None = None,
    market: str | None = None,
    fetch_all: bool = False,
    registry: str | Path | None = None,
    adapter_factory: Callable[[str], DailyPriceAdapter] | None = None,
) -> FetchResult:
    """Fetch one or more registered indices and merge them into local Parquet storage."""
    targets = select_fetch_targets(symbol=symbol, market=market, fetch_all=fetch_all, registry=registry)
    make_adapter = adapter_factory or default_adapter_factory

    frames: list[pd.DataFrame] = []
    success_symbols: list[str] = []
    failures: list[FetchFailure] = []

    for index in targets:
        try:
            adapter = make_adapter(index.market.upper())
            data_source_symbol = to_data_source_symbol(index.symbol, index.market)
            prices = adapter.fetch_daily(data_source_symbol, start_date=start_date, end_date=end_date)
            prices = _restore_registry_symbol(prices, index)
            frames.append(prices)
            success_symbols.append(index.symbol)
        except Exception as exc:  # pragma: no cover - individual branches covered through tests
            failures.append(FetchFailure(symbol=index.symbol, reason=_format_fetch_error(exc)))

    if not frames:
        return FetchResult(output_file=None, rows=0, success_symbols=success_symbols, failures=failures)

    fetched = pd.concat(frames, ignore_index=True)
    merged = merge_with_existing_price_data(fetched, data_dir)
    output_file = save_price_data(merged, data_dir)
    return FetchResult(output_file=output_file, rows=len(fetched), success_symbols=success_symbols, failures=failures)


def select_fetch_targets(
    *,
    symbol: str | None = None,
    market: str | None = None,
    fetch_all: bool = False,
    registry: str | Path | None = None,
) -> list[IndexInfo]:
    """Select fetch targets from the index registry."""
    selected_modes = sum(value is not None for value in [symbol, market]) + int(fetch_all)
    if selected_modes != 1:
        raise ValueError("Choose exactly one of --symbol, --market, or --all.")

    if symbol is not None:
        target_symbol = symbol.upper()
        matches = [index for index in load_indices(registry) if index.symbol.upper() == target_symbol]
        if not matches:
            raise ValueError(f"Index symbol is not registered: {symbol}")
        return matches

    if market is not None:
        targets = filter_indices_by_market(market, registry)
        if not targets:
            raise ValueError(f"No registered indices found for market: {market}")
        return targets

    return load_indices(registry)


def default_adapter_factory(market: str) -> DailyPriceAdapter:
    """Create the preferred adapter for a market."""
    target_market = market.upper()
    if target_market == "CN":
        return AkShareIndexAdapter()
    if target_market == "US":
        return YFinanceAdapter()
    if target_market == "HK":
        return HongKongIndexAdapter()
    raise ValueError(f"Unsupported market for online fetch: {market}")


def to_data_source_symbol(symbol: str, market: str) -> str:
    """Map a registry symbol to the preferred data-source symbol."""
    target_market = market.upper()
    if target_market == "CN":
        return CN_SYMBOL_MAP.get(symbol, symbol)
    if target_market == "US":
        return YFINANCE_SYMBOL_MAP.get(symbol, symbol)
    if target_market == "HK":
        # HongKongIndexAdapter already maps the public HK registry symbols internally.
        return symbol
    return symbol


def merge_with_existing_price_data(fetched: pd.DataFrame, data_dir: str | Path) -> pd.DataFrame:
    """Merge fetched rows with existing storage, preferring fetched rows on duplicate dates."""
    normalized_fetched = normalize_daily_price_data(fetched)
    try:
        existing = load_price_data(data_dir)
    except FileNotFoundError:
        return normalized_fetched

    combined = pd.concat([existing, normalized_fetched], ignore_index=True)
    combined = combined.drop_duplicates(subset=["symbol", "date"], keep="last")
    return combined.sort_values(["symbol", "date"]).reset_index(drop=True)


def _restore_registry_symbol(prices: pd.DataFrame, index: IndexInfo) -> pd.DataFrame:
    data = prices.copy()
    data["symbol"] = index.symbol
    data["currency"] = index.currency
    return normalize_daily_price_data(data)


def _format_fetch_error(exc: Exception) -> str:
    message = str(exc)
    if isinstance(exc, ImportError) and ("akshare" in message.lower() or "yfinance" in message.lower()):
        return f"{message} {INSTALL_OPTIONAL_DATA_DEPS_MESSAGE}"
    return message
