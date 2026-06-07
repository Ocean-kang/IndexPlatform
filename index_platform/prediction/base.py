"""Base prediction interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BasePredictor(ABC):
    """Interface for simple predictors that return date-aligned values."""

    name: str

    @abstractmethod
    def predict(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate predictions from historical daily price data."""
