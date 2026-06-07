"""Strategy package."""

from index_platform.strategy.base import Strategy
from index_platform.strategy.buy_hold import BuyAndHoldStrategy
from index_platform.strategy.momentum import MomentumRotationStrategy
from index_platform.strategy.moving_average import MovingAverageStrategy
from index_platform.strategy.prediction_strategy import PredictionStrategy

__all__ = [
    "BuyAndHoldStrategy",
    "MomentumRotationStrategy",
    "MovingAverageStrategy",
    "PredictionStrategy",
    "Strategy",
]
