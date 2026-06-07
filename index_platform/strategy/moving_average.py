"""Moving-average timing strategy."""

from __future__ import annotations

import pandas as pd

from index_platform.strategy.base import Strategy


class MovingAverageStrategy(Strategy):
    """Single-symbol timing strategy based on close price and moving average.

    Rule: the signal is generated after day T close and becomes the target
    position on T+1 by default, avoiding look-ahead bias.
    """

    name = "moving_average"

    def __init__(self, window: int, hold_when_above: bool = True, execution_delay: int = 1) -> None:
        if window <= 0:
            raise ValueError("window must be positive.")
        if execution_delay < 0:
            raise ValueError("execution_delay must not be negative.")
        self.window = window
        self.hold_when_above = hold_when_above
        self.execution_delay = execution_delay

    def generate_signals(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate close-of-day hold/cash signals before execution delay."""
        closes = pd.to_numeric(price_data["close"], errors="raise")
        moving_average = closes.rolling(self.window, min_periods=self.window).mean()
        above = closes > moving_average
        signal = above if self.hold_when_above else ~above
        return signal.fillna(False).astype(float).rename("signal")

    def generate_positions(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate target positions with T close signal applied on T+1."""
        signals = self.generate_signals(price_data)
        positions = signals.shift(self.execution_delay).fillna(0.0)
        return positions.astype(float).rename("position")
