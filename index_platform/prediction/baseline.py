"""Simple baseline predictors without training or heavy ML dependencies."""

from __future__ import annotations

import pandas as pd

from index_platform.prediction.base import BasePredictor
from index_platform.prediction.features import make_return_features


class MomentumDirectionPredictor(BasePredictor):
    """Predict future direction from the sign of trailing N-day return."""

    name = "momentum_direction"

    def __init__(self, window: int) -> None:
        if window <= 0:
            raise ValueError("window must be positive.")
        self.window = window

    def predict(self, price_data: pd.DataFrame) -> pd.Series:
        """Return 1 for positive trailing return, -1 for negative, 0 otherwise."""
        features = make_return_features(price_data, self.window)
        trailing_return = features[f"return_{self.window}d"]
        predictions = trailing_return.apply(_direction).astype(float)
        predictions.index = features["date"]
        return predictions.rename("prediction")


class RollingMeanReturnPredictor(BasePredictor):
    """Estimate future return with the trailing N-day average return."""

    name = "rolling_mean_return"

    def __init__(self, window: int) -> None:
        if window <= 0:
            raise ValueError("window must be positive.")
        self.window = window

    def predict(self, price_data: pd.DataFrame) -> pd.Series:
        """Return trailing average daily return as a date-aligned prediction."""
        features = make_return_features(price_data, self.window)
        predictions = features[f"mean_return_{self.window}d"].fillna(0.0).astype(float)
        predictions.index = features["date"]
        return predictions.rename("prediction")


def _direction(value: float) -> float:
    if pd.isna(value) or value == 0:
        return 0.0
    return 1.0 if value > 0 else -1.0
