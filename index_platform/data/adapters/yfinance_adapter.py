"""yfinance adapter for US index and ETF daily prices."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data
from index_platform.storage import save_price_data


class YFinanceAdapter:
    """Fetch and standardize daily prices from yfinance."""

    source = "yfinance"

    def __init__(self, yfinance_module: Any | None = None) -> None:
        self._yfinance = yfinance_module

    def fetch_daily(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        currency: str = "USD",
    ) -> pd.DataFrame:
        """Fetch daily prices and return the DailyPrice schema."""
        yfinance = self._load_yfinance()
        try:
            raw = yfinance.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
        except Exception as exc:  # pragma: no cover - exercised with mock errors
            raise RuntimeError(f"yfinance failed to fetch daily prices for {symbol}: {exc}") from exc
        return standardize_yfinance_daily(raw, symbol=symbol, currency=currency)

    def fetch_and_save(
        self,
        symbol: str,
        storage_dir: str | Path,
        start_date: str | None = None,
        end_date: str | None = None,
        currency: str = "USD",
    ) -> Path:
        """Fetch prices and save them to local Parquet storage."""
        prices = self.fetch_daily(symbol, start_date=start_date, end_date=end_date, currency=currency)
        return save_price_data(prices, storage_dir)

    def _load_yfinance(self) -> Any:
        if self._yfinance is not None:
            return self._yfinance
        try:
            import yfinance as yfinance_module  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError("yfinance is not installed. Install optional dependency 'yfinance' to use this adapter.") from exc
        return yfinance_module


def standardize_yfinance_daily(raw: pd.DataFrame, symbol: str, currency: str = "USD") -> pd.DataFrame:
    """Normalize yfinance download output to DailyPrice columns."""
    if raw.empty:
        raise ValueError(f"yfinance returned no daily price rows for {symbol}.")

    data = raw.copy()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.reset_index()
    data = data.rename(
        columns={
            "Date": "date",
            "Datetime": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
        }
    )
    data["symbol"] = symbol
    data["amount"] = 0.0
    data["currency"] = currency
    data["source"] = YFinanceAdapter.source
    return normalize_daily_price_data(data)
