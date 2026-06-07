import pandas as pd

from index_platform.strategy.moving_average import MovingAverageStrategy


def _prices(close_values: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-02", periods=len(close_values), freq="D"),
            "symbol": ["000300.SH"] * len(close_values),
            "open": close_values,
            "high": close_values,
            "low": close_values,
            "close": close_values,
            "volume": [1000] * len(close_values),
            "amount": [100000] * len(close_values),
            "currency": ["CNY"] * len(close_values),
            "source": ["toy"] * len(close_values),
        }
    )


def test_moving_average_generates_hold_and_cash_signals() -> None:
    strategy = MovingAverageStrategy(window=3)

    signals = strategy.generate_signals(_prices([10, 10, 12, 9, 13]))

    assert signals.tolist() == [0.0, 0.0, 1.0, 0.0, 1.0]


def test_moving_average_positions_apply_next_day() -> None:
    strategy = MovingAverageStrategy(window=3)

    positions = strategy.generate_positions(_prices([10, 10, 12, 9, 13]))

    assert positions.tolist() == [0.0, 0.0, 0.0, 1.0, 0.0]


def test_moving_average_does_not_use_future_prices_for_earlier_positions() -> None:
    strategy = MovingAverageStrategy(window=3)
    base = strategy.generate_positions(_prices([10, 10, 12, 9, 13]))
    changed_future = strategy.generate_positions(_prices([10, 10, 12, 9, 99]))

    assert base.iloc[:4].tolist() == changed_future.iloc[:4].tolist()


def test_moving_average_validates_window() -> None:
    try:
        MovingAverageStrategy(window=0)
    except ValueError as exc:
        assert "window" in str(exc)
    else:
        raise AssertionError("Expected invalid window to raise ValueError")
