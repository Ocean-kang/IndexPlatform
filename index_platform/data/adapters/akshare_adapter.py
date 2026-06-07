"""AKShare adapter for A-share index daily prices."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data
from index_platform.storage import save_price_data


class AkShareIndexAdapter:
    """Fetch and standardize A-share index daily prices from AKShare."""

    source = "akshare"

    def __init__(self, akshare_module: Any | None = None) -> None:
        self._akshare = akshare_module

    def fetch_daily(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        currency: str = "CNY",
    ) -> pd.DataFrame:
        """Fetch daily prices and return the DailyPrice schema."""
        akshare = self._load_akshare()
        try:
            raw = akshare.stock_zh_index_daily(symbol=symbol)
        except Exception as exc:  # pragma: no cover - exercised with mock errors
            raise RuntimeError(f"AKShare failed to fetch index daily prices for {symbol}: {exc}") from exc

        data = standardize_akshare_daily(raw, symbol=symbol, currency=currency)
        if start_date is not None:
            data = data[data["date"] >= pd.Timestamp(start_date).normalize()]
        if end_date is not None:
            data = data[data["date"] <= pd.Timestamp(end_date).normalize()]
        return data.reset_index(drop=True)

    def fetch_and_save(
        self,
        symbol: str,
        storage_dir: str | Path,
        start_date: str | None = None,
        end_date: str | None = None,
        currency: str = "CNY",
    ) -> Path:
        """Fetch prices and save them to local Parquet storage."""
        prices = self.fetch_daily(symbol, start_date=start_date, end_date=end_date, currency=currency)
        return save_price_data(prices, storage_dir)

    def _load_akshare(self) -> Any:
        if self._akshare is not None:
            return self._akshare
        try:
            import akshare as akshare_module  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError("AKShare is not installed. Install optional dependency 'akshare' to use this adapter.") from exc
        return akshare_module


def standardize_akshare_daily(raw: pd.DataFrame, symbol: str, currency: str = "CNY") -> pd.DataFrame:
    """Normalize common AKShare index output to DailyPrice columns."""
    rename_map = {
        "日期": "date",
        "date": "date",
        "开盘": "open",
        "open": "open",
        "最高": "high",
        "high": "high",
        "最低": "low",
        "low": "low",
        "收盘": "close",
        "close": "close",
        "成交量": "volume",
        "volume": "volume",
        "成交额": "amount",
        "amount": "amount",
    }
    data = raw.rename(columns={column: rename_map.get(str(column), str(column)) for column in raw.columns}).copy()
    data["symbol"] = symbol
    data["currency"] = currency
    data["source"] = AkShareIndexAdapter.source
    if "amount" not in data.columns:
        data["amount"] = 0.0
    if "volume" not in data.columns:
        data["volume"] = 0.0
    return normalize_daily_price_data(data)
