"""Base strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Interface for strategies that produce target daily positions."""

    name: str

    @abstractmethod
    def generate_positions(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate target exposure for each row in the price data."""

