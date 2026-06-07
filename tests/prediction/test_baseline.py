import pandas as pd

import index_platform.prediction as prediction
from index_platform.prediction import MomentumDirectionPredictor, RollingMeanReturnPredictor, make_return_features


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


def test_prediction_module_can_import() -> None:
    assert prediction.MomentumDirectionPredictor is MomentumDirectionPredictor


def test_return_features_and_baselines_generate_date_aligned_predictions() -> None:
    prices = _prices([10, 11, 12, 11, 13])

    features = make_return_features(prices, window=2)
    direction = MomentumDirectionPredictor(window=2).predict(prices)
    mean_return = RollingMeanReturnPredictor(window=2).predict(prices)

    assert features["date"].tolist() == prices["date"].tolist()
    assert direction.index.tolist() == prices["date"].tolist()
    assert mean_return.index.tolist() == prices["date"].tolist()
    assert direction.tolist() == [0.0, 0.0, 1.0, 0.0, 1.0]
    assert mean_return.iloc[-1] != 0.0


def test_baseline_does_not_use_future_data_for_earlier_predictions() -> None:
    predictor = RollingMeanReturnPredictor(window=2)
    base = predictor.predict(_prices([10, 11, 12, 11, 13]))
    changed_future = predictor.predict(_prices([10, 11, 12, 11, 99]))

    assert base.iloc[:4].tolist() == changed_future.iloc[:4].tolist()


def test_predictor_validates_window() -> None:
    try:
        MomentumDirectionPredictor(window=0)
    except ValueError as exc:
        assert "window" in str(exc)
    else:
        raise AssertionError("Expected invalid window to raise ValueError")
