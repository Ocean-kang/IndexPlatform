import pandas as pd

from index_platform.backtest.engine import run_backtest
from index_platform.strategy.buy_hold import BuyAndHoldStrategy


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


def test_buy_hold_backtest_nav_uses_close_price_returns() -> None:
    result = run_backtest(_prices([100, 110, 99]), BuyAndHoldStrategy())

    assert result["nav"].round(6).tolist() == [1.0, 1.1, 0.99]


def test_buy_hold_backtest_initial_nav_is_one() -> None:
    result = run_backtest(_prices([100, 120]), BuyAndHoldStrategy())

    assert result.loc[0, "nav"] == 1.0


def test_backtest_rejects_multiple_symbols() -> None:
    prices = _prices([100, 101])
    prices.loc[1, "symbol"] = "SPX.US"

    try:
        run_backtest(prices, BuyAndHoldStrategy())
    except ValueError as exc:
        assert "exactly one symbol" in str(exc)
    else:
        raise AssertionError("Expected multiple symbols to raise ValueError")

