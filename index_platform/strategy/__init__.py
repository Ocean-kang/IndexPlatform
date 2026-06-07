"""Strategy package."""

from index_platform.strategy.base import Strategy
from index_platform.strategy.buy_hold import BuyAndHoldStrategy
from index_platform.strategy.momentum import MomentumRotationStrategy
from index_platform.strategy.moving_average import MovingAverageStrategy

__all__ = [
    "BuyAndHoldStrategy",
    "MomentumRotationStrategy",
    "MovingAverageStrategy",
    "Strategy",
]
