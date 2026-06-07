"""Simple daily backtest engine."""

from __future__ import annotations

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data
from index_platform.strategy.base import Strategy


def run_backtest(price_data: pd.DataFrame, strategy: Strategy) -> pd.DataFrame:
    """Run a single-index daily close-price backtest."""
    prices = normalize_daily_price_data(price_data).sort_values("date").reset_index(drop=True)
    symbols = prices["symbol"].dropna().unique()
    if len(symbols) != 1:
        raise ValueError("The first backtest engine supports exactly one symbol.")
    if prices.empty:
        raise ValueError("Price data must not be empty.")
    if (prices["close"] <= 0).any():
        raise ValueError("Close prices must be positive.")

    positions = strategy.generate_positions(prices).reset_index(drop=True).astype(float)
    if len(positions) != len(prices):
        raise ValueError("Strategy positions must match price data length.")
    if (positions < 0).any():
        raise ValueError("The first backtest engine only supports long-only positions.")

    returns = prices["close"].pct_change().fillna(0.0)
    strategy_returns = returns * positions.shift(1).fillna(positions.iloc[0])
    nav = (1.0 + strategy_returns).cumprod()
    nav.iloc[0] = 1.0

    return pd.DataFrame(
        {
            "date": prices["date"],
            "symbol": prices["symbol"],
            "close": prices["close"],
            "position": positions,
            "nav": nav,
        }
    )

