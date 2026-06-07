import pandas as pd

from index_platform.backtest.engine import run_multi_asset_backtest


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


def test_multi_asset_backtest_rebalances_to_target_weights() -> None:
    prices = _multi_prices({"AAA": [100, 110], "BBB": [100, 100]})
    weights = pd.DataFrame({"AAA": [0.6], "BBB": [0.4]}, index=[pd.Timestamp("2024-01-02")])

    result = run_multi_asset_backtest(prices, weights)
    day0_positions = result["positions"][result["positions"]["date"] == pd.Timestamp("2024-01-02")]

    assert day0_positions.set_index("symbol")["weight"].round(6).to_dict() == {"AAA": 0.6, "BBB": 0.4}
    assert result["nav"]["nav"].round(6).tolist() == [1.0, 1.06]


def test_multi_asset_weights_drift_on_non_rebalance_days() -> None:
    prices = _multi_prices({"AAA": [100, 200], "BBB": [100, 100]})
    weights = pd.DataFrame({"AAA": [0.5], "BBB": [0.5]}, index=[pd.Timestamp("2024-01-02")])

    result = run_multi_asset_backtest(prices, weights)
    day1_positions = result["positions"][result["positions"]["date"] == pd.Timestamp("2024-01-03")]

    drifted = day1_positions.set_index("symbol")["weight"].round(6).to_dict()
    assert drifted == {"AAA": 0.666667, "BBB": 0.333333}


def test_multi_asset_rebalance_can_leave_cash() -> None:
    prices = _multi_prices({"AAA": [100, 100], "BBB": [100, 100]})
    weights = pd.DataFrame({"AAA": [0.3], "BBB": [0.2]}, index=[pd.Timestamp("2024-01-02")])

    result = run_multi_asset_backtest(prices, weights)
    day0_positions = result["positions"][result["positions"]["date"] == pd.Timestamp("2024-01-02")]

    assert round(day0_positions["weight"].sum(), 6) == 0.5
    assert result["nav"]["nav"].tolist() == [1.0, 1.0]


def test_multi_asset_rejects_leverage_and_short_weights() -> None:
    prices = _multi_prices({"AAA": [100], "BBB": [100]})
    leveraged = pd.DataFrame({"AAA": [0.7], "BBB": [0.4]}, index=[pd.Timestamp("2024-01-02")])
    short = pd.DataFrame({"AAA": [1.0], "BBB": [-0.1]}, index=[pd.Timestamp("2024-01-02")])

    for weights in (leveraged, short):
        try:
            run_multi_asset_backtest(prices, weights)
        except ValueError as exc:
            assert "weights" in str(exc)
        else:
            raise AssertionError("Expected invalid target weights to raise ValueError")
