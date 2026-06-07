"""Momentum rotation strategy."""

from __future__ import annotations

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data


class MomentumRotationStrategy:
    """Rank symbols by past returns and hold the top K equally."""

    name = "momentum"

    def __init__(
        self,
        lookback: int,
        top_k: int,
        rebalance_frequency: int,
        execution_delay: int = 1,
    ) -> None:
        if lookback <= 0:
            raise ValueError("lookback must be positive.")
        if top_k <= 0:
            raise ValueError("top_k must be positive.")
        if rebalance_frequency <= 0:
            raise ValueError("rebalance_frequency must be positive.")
        if execution_delay < 0:
            raise ValueError("execution_delay must not be negative.")
        self.lookback = lookback
        self.top_k = top_k
        self.rebalance_frequency = rebalance_frequency
        self.execution_delay = execution_delay

    def calculate_momentum(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate past N-day close-to-close returns by symbol."""
        closes = _pivot_close(price_data)
        return closes.pct_change(self.lookback)

    def generate_target_weights(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Generate target weights, with T close scores applied on T+1."""
        scores = self.calculate_momentum(price_data)
        raw_weights = pd.DataFrame(float("nan"), index=scores.index, columns=scores.columns, dtype="float64")

        for row_number, date in enumerate(scores.index):
            if row_number < self.lookback or (row_number - self.lookback) % self.rebalance_frequency != 0:
                continue
            raw_weights.loc[date] = 0.0
            valid_scores = scores.loc[date].dropna().sort_values(ascending=False)
            selected = valid_scores.head(self.top_k).index
            if len(selected) == 0:
                continue
            raw_weights.loc[date, selected] = 1.0 / len(selected)

        weights = raw_weights.shift(self.execution_delay).ffill().fillna(0.0)
        row_sums = weights.sum(axis=1)
        if (row_sums > 1.0 + 1e-12).any():
            raise ValueError("Generated weights must not sum above 1.")
        return weights


def _pivot_close(price_data: pd.DataFrame) -> pd.DataFrame:
    prices = normalize_daily_price_data(price_data)
    if prices.empty:
        raise ValueError("Price data must not be empty.")
    closes = prices.pivot(index="date", columns="symbol", values="close").sort_index()
    if (closes <= 0).any().any():
        raise ValueError("Close prices must be positive.")
    return closes
