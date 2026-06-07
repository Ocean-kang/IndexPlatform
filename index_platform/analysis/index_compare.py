"""Index comparison analysis helpers."""

from __future__ import annotations

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data
from index_platform.metrics import calculate_performance_metrics


def normalize_prices(price_data: pd.DataFrame, base: float = 1.0) -> pd.DataFrame:
    """Return close prices normalized to a common starting value by symbol."""
    closes = _close_matrix(price_data)
    return closes.divide(closes.iloc[0]).multiply(base)


def yearly_returns(price_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate calendar-year close-to-close returns by symbol."""
    closes = _close_matrix(price_data)
    yearly_last = closes.resample("YE").last()
    yearly_first = closes.resample("YE").first()
    returns = yearly_last.divide(yearly_first).subtract(1.0)
    returns.index = returns.index.year
    return returns


def risk_metrics(price_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate basic risk metrics for each index."""
    normalized = normalize_prices(price_data)
    rows = {
        symbol: calculate_performance_metrics(normalized[symbol].dropna())
        for symbol in normalized.columns
    }
    return pd.DataFrame.from_dict(rows, orient="index")


def correlation_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily return correlation matrix by symbol."""
    closes = _close_matrix(price_data)
    return closes.pct_change().dropna(how="all").corr()


def compare_indices(price_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build reusable comparison outputs for dashboard and CLI callers."""
    return {
        "normalized": normalize_prices(price_data),
        "yearly_returns": yearly_returns(price_data),
        "risk_metrics": risk_metrics(price_data),
        "correlation": correlation_matrix(price_data),
    }


def _close_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
    prices = normalize_daily_price_data(price_data)
    if prices.empty:
        raise ValueError("Price data must not be empty.")
    closes = prices.pivot(index="date", columns="symbol", values="close").sort_index()
    if closes.empty:
        raise ValueError("Price data must contain close prices.")
    return closes
