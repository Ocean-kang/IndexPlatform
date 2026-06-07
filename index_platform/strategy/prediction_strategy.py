"""Strategy adapter for date-aligned prediction signals."""

from __future__ import annotations

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data
from index_platform.prediction.base import BasePredictor
from index_platform.strategy.base import Strategy


class PredictionStrategy(Strategy):
    """Convert prediction values into long/cash target positions."""

    name = "prediction"

    def __init__(
        self,
        predictor: BasePredictor | None = None,
        predictions: pd.Series | pd.DataFrame | None = None,
        threshold: float = 0.0,
        execution_delay: int = 1,
    ) -> None:
        if predictor is None and predictions is None:
            raise ValueError("Either predictor or predictions must be provided.")
        if execution_delay < 0:
            raise ValueError("execution_delay must not be negative.")
        self.predictor = predictor
        self.predictions = predictions
        self.threshold = threshold
        self.execution_delay = execution_delay

    def generate_signals(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate same-day long/cash signals from prediction values."""
        prices = normalize_daily_price_data(price_data).sort_values("date").reset_index(drop=True)
        prediction_values = self._resolve_predictions(prices)
        signals = (prediction_values > self.threshold).astype(float)
        signals.index = prices["date"]
        return signals.rename("signal")

    def generate_positions(self, price_data: pd.DataFrame) -> pd.Series:
        """Generate target positions with T signal applied after execution delay."""
        signals = self.generate_signals(price_data)
        positions = signals.shift(self.execution_delay).fillna(0.0).clip(lower=0.0, upper=1.0)
        return positions.astype(float).rename("position")

    def generate_target_weights(self, price_data: pd.DataFrame) -> pd.DataFrame:
        """Return a single-symbol target-weight matrix for portfolio backtests."""
        prices = normalize_daily_price_data(price_data).sort_values("date").reset_index(drop=True)
        symbols = prices["symbol"].dropna().unique()
        if len(symbols) != 1:
            raise ValueError("PredictionStrategy supports exactly one symbol in the first version.")
        positions = self.generate_positions(prices)
        return pd.DataFrame({symbols[0]: positions.to_numpy()}, index=positions.index)

    def _resolve_predictions(self, prices: pd.DataFrame) -> pd.Series:
        if self.predictor is not None:
            raw = self.predictor.predict(prices)
        else:
            raw = self.predictions
        series = _prediction_series(raw)
        series.index = pd.to_datetime(series.index).normalize()
        aligned = series.reindex(prices["date"])
        return aligned.fillna(float("-inf")).astype(float)


def _prediction_series(predictions: pd.Series | pd.DataFrame | None) -> pd.Series:
    if predictions is None:
        raise ValueError("predictions must not be None.")
    if isinstance(predictions, pd.Series):
        return predictions.copy()
    if "prediction" in predictions.columns:
        if "date" in predictions.columns:
            return pd.Series(predictions["prediction"].to_numpy(), index=pd.to_datetime(predictions["date"]))
        return predictions["prediction"].copy()
    raise ValueError("Prediction DataFrame must contain a 'prediction' column.")
