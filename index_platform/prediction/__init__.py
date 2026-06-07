"""Lightweight prediction interfaces and baseline predictors."""

from index_platform.prediction.base import BasePredictor
from index_platform.prediction.baseline import MomentumDirectionPredictor, RollingMeanReturnPredictor
from index_platform.prediction.features import make_return_features

__all__ = [
    "BasePredictor",
    "MomentumDirectionPredictor",
    "RollingMeanReturnPredictor",
    "make_return_features",
]
