"""Buy-and-hold strategy."""

from __future__ import annotations

import pandas as pd

from index_platform.strategy.base import Strategy


class BuyAndHoldStrategy(Strategy):
    """Hold one long unit of exposure for the whole backtest."""

    name = "buy_hold"

    def generate_positions(self, price_data: pd.DataFrame) -> pd.Series:
        """Return a constant long-only target position."""
        return pd.Series(1.0, index=price_data.index, name="position")

