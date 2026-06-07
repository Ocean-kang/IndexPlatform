import pandas as pd

from index_platform.strategy.prediction_strategy import PredictionStrategy


def _prices(closes: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-02", periods=len(closes), freq="D"),
            "symbol": ["AAA"] * len(closes),
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000] * len(closes),
            "amount": [10000] * len(closes),
            "currency": ["CNY"] * len(closes),
            "source": ["toy"] * len(closes),
        }
    )


def test_prediction_values_convert_to_next_day_positions() -> None:
    prices = _prices([10, 11, 12, 13])
    predictions = pd.Series([0.1, -0.1, 0.2, 0.3], index=prices["date"])
    strategy = PredictionStrategy(predictions=predictions, threshold=0.0)

    positions = strategy.generate_positions(prices)

    assert positions.tolist() == [0.0, 1.0, 0.0, 1.0]


def test_prediction_threshold_rule_uses_long_or_cash_only() -> None:
    prices = _prices([10, 11, 12, 13])
    predictions = pd.DataFrame({"date": prices["date"], "prediction": [0.05, 0.20, 0.10, 0.30]})
    strategy = PredictionStrategy(predictions=predictions, threshold=0.10)

    signals = strategy.generate_signals(prices)
    weights = strategy.generate_target_weights(prices)

    assert signals.tolist() == [0.0, 1.0, 0.0, 1.0]
    assert weights["AAA"].max() <= 1.0
    assert weights["AAA"].min() >= 0.0


def test_prediction_strategy_does_not_use_future_predictions() -> None:
    prices = _prices([10, 11, 12, 13])
    base_predictions = pd.Series([0.1, -0.1, 0.2, -0.2], index=prices["date"])
    changed_future = pd.Series([0.1, -0.1, 0.2, 99.0], index=prices["date"])

    base = PredictionStrategy(predictions=base_predictions).generate_positions(prices)
    changed = PredictionStrategy(predictions=changed_future).generate_positions(prices)

    assert base.iloc[:4].tolist() == changed.iloc[:4].tolist()


def test_prediction_strategy_validates_inputs() -> None:
    try:
        PredictionStrategy()
    except ValueError as exc:
        assert "predictor or predictions" in str(exc)
    else:
        raise AssertionError("Expected missing predictions to raise ValueError")
