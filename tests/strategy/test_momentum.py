import pandas as pd

from index_platform.strategy.momentum import MomentumRotationStrategy


def _multi_prices(close_by_symbol: dict[str, list[float]]) -> pd.DataFrame:
    rows = []
    dates = pd.date_range("2024-01-02", periods=len(next(iter(close_by_symbol.values()))), freq="D")
    for symbol, closes in close_by_symbol.items():
        for date, close in zip(dates, closes):
            rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "open": close,
                    "high": close,
                    "low": close,
                    "close": close,
                    "volume": 1000,
                    "amount": 100000,
                    "currency": "CNY",
                    "source": "toy",
                }
            )
    return pd.DataFrame(rows)


def test_momentum_calculates_past_returns() -> None:
    strategy = MomentumRotationStrategy(lookback=2, top_k=1, rebalance_frequency=1)

    momentum = strategy.calculate_momentum(_multi_prices({"AAA": [100, 110, 121], "BBB": [100, 90, 81]}))

    assert round(momentum.loc[pd.Timestamp("2024-01-04"), "AAA"], 6) == 0.21
    assert round(momentum.loc[pd.Timestamp("2024-01-04"), "BBB"], 6) == -0.19


def test_momentum_selects_top_k_and_equal_weights_next_day() -> None:
    strategy = MomentumRotationStrategy(lookback=2, top_k=2, rebalance_frequency=1)
    prices = _multi_prices(
        {
            "AAA": [100, 110, 121, 130],
            "BBB": [100, 100, 102, 104],
            "CCC": [100, 90, 81, 80],
        }
    )

    weights = strategy.generate_target_weights(prices)

    effective_date = pd.Timestamp("2024-01-05")
    assert weights.loc[effective_date, "AAA"] == 0.5
    assert weights.loc[effective_date, "BBB"] == 0.5
    assert weights.loc[effective_date, "CCC"] == 0.0
    assert weights.loc[effective_date].sum() <= 1.0


def test_momentum_rebalances_by_frequency_and_carries_weights() -> None:
    strategy = MomentumRotationStrategy(lookback=1, top_k=1, rebalance_frequency=2)
    prices = _multi_prices({"AAA": [100, 120, 110, 100], "BBB": [100, 101, 130, 150]})

    weights = strategy.generate_target_weights(prices)

    assert weights.loc[pd.Timestamp("2024-01-04"), "AAA"] == 1.0
    assert weights.loc[pd.Timestamp("2024-01-05"), "AAA"] == 1.0


def test_momentum_does_not_use_future_prices_for_earlier_weights() -> None:
    strategy = MomentumRotationStrategy(lookback=2, top_k=1, rebalance_frequency=1)
    base = strategy.generate_target_weights(_multi_prices({"AAA": [100, 110, 121, 130], "BBB": [100, 90, 81, 80]}))
    changed_future = strategy.generate_target_weights(
        _multi_prices({"AAA": [100, 110, 121, 10], "BBB": [100, 90, 81, 800]})
    )

    assert base.iloc[:3].equals(changed_future.iloc[:3])


def test_momentum_validates_parameters() -> None:
    try:
        MomentumRotationStrategy(lookback=0, top_k=1, rebalance_frequency=1)
    except ValueError as exc:
        assert "lookback" in str(exc)
    else:
        raise AssertionError("Expected invalid lookback to raise ValueError")
