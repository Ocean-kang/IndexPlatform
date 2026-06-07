"""Simple market trading calendar."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


SUPPORTED_MARKETS = {"CN", "HK", "US"}


@dataclass(frozen=True)
class TradingCalendar:
    """Weekend-aware trading calendar for first-stage research."""

    market: str
    holidays: frozenset[pd.Timestamp] = frozenset()

    def __post_init__(self) -> None:
        normalized_market = self.market.upper()
        if normalized_market not in SUPPORTED_MARKETS:
            raise ValueError(f"Unsupported market: {self.market}")
        object.__setattr__(self, "market", normalized_market)
        object.__setattr__(
            self,
            "holidays",
            frozenset(pd.Timestamp(day).normalize() for day in self.holidays),
        )

    def is_trading_day(self, day: str | pd.Timestamp) -> bool:
        """Return whether a date is a trading day."""
        date = pd.Timestamp(day).normalize()
        return date.weekday() < 5 and date not in self.holidays

    def next_trading_day(self, day: str | pd.Timestamp) -> pd.Timestamp:
        """Return the first trading day after the given date."""
        current = pd.Timestamp(day).normalize() + pd.Timedelta(days=1)
        while not self.is_trading_day(current):
            current += pd.Timedelta(days=1)
        return current

    def trading_days(self, start_date: str | pd.Timestamp, end_date: str | pd.Timestamp) -> pd.DatetimeIndex:
        """Return trading days in an inclusive date range."""
        days = pd.date_range(pd.Timestamp(start_date).normalize(), pd.Timestamp(end_date).normalize(), freq="D")
        return pd.DatetimeIndex([day for day in days if self.is_trading_day(day)])

    def rebalance_days(
        self,
        start_date: str | pd.Timestamp,
        end_date: str | pd.Timestamp,
        frequency: str,
    ) -> pd.DatetimeIndex:
        """Return week-end or month-end rebalance days."""
        days = self.trading_days(start_date, end_date)
        if days.empty:
            return days

        frequency = frequency.lower()
        groups: list[pd.DatetimeIndex]
        if frequency in {"weekly", "week", "w"}:
            groups = [group for _, group in pd.Series(days, index=days).groupby(days.to_period("W-FRI"))]
        elif frequency in {"monthly", "month", "m"}:
            groups = [group for _, group in pd.Series(days, index=days).groupby(days.to_period("M"))]
        else:
            raise ValueError(f"Unsupported rebalance frequency: {frequency}")
        return pd.DatetimeIndex([group.iloc[-1] for group in groups])
