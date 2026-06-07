"""Hong Kong index adapter built on yfinance-compatible daily data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from index_platform.data.adapters.yfinance_adapter import standardize_yfinance_daily
from index_platform.storage import save_price_data


class HongKongIndexAdapter:
    """Fetch and standardize Hong Kong index prices with HKD currency."""

    source = "yfinance"

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yfinance = yfinance_module

    def fetch_daily(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """Fetch Hong Kong daily prices and return DailyPrice rows in HKD."""
        yfinance = self._load_yfinance()
        yf_symbol = _to_yfinance_hk_symbol(symbol)
        try:
            raw = yfinance.download(yf_symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
        except Exception as exc:  # pragma: no cover - exercised with mock errors
            raise RuntimeError(f"yfinance failed to fetch Hong Kong daily prices for {symbol}: {exc}") from exc
        prices = standardize_yfinance_daily(raw, symbol=symbol, currency="HKD")
        prices["source"] = "hk_yfinance"
        return prices

    def fetch_and_save(
        self,
        symbol: str,
        storage_dir: str | Path,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Path:
        """Fetch prices and save them to local Parquet storage."""
        prices = self.fetch_daily(symbol, start_date=start_date, end_date=end_date)
        return save_price_data(prices, storage_dir)

    def _load_yfinance(self) -> Any:
        if self._yfinance is not None:
            return self._yfinance
        try:
            import yfinance as yfinance_module  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError("yfinance is not installed. Install optional dependency 'yfinance' to use HK adapter.") from exc
        return yfinance_module


def _to_yfinance_hk_symbol(symbol: str) -> str:
    mapping = {
        "HSI.HK": "^HSI",
        "HSCEI.HK": "^HSCE",
        "HSTECH.HK": "HSTECH.HK",
    }
    return mapping.get(symbol, symbol)
