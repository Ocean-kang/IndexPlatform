"""Schema definitions for daily index price data."""

from __future__ import annotations

DAILY_PRICE_REQUIRED_FIELDS = [
    "date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "currency",
    "source",
]

DAILY_PRICE_NUMERIC_FIELDS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
]

