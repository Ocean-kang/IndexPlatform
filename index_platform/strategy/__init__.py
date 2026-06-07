"""Strategy package."""

from index_platform.strategy.base import Strategy
from index_platform.strategy.buy_hold import BuyAndHoldStrategy

__all__ = [
    "BuyAndHoldStrategy",
    "Strategy",
]
