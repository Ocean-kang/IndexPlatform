import pandas as pd

from index_platform.backtest.costs import TransactionCostModel
from index_platform.backtest.engine import run_multi_asset_backtest


def _prices() -> pd.DataFrame:
    rows = []
    for date in pd.date_range("2024-01-02", periods=2, freq="D"):
        rows.append(
            {
                "date": date,
                "symbol": "AAA",
                "open": 100,
                "high": 100,
                "low": 100,
                "close": 100,
                "volume": 1000,
                "amount": 100000,
                "currency": "CNY",
                "source": "toy",
            }
        )
    return pd.DataFrame(rows)


def test_transaction_cost_model_calculates_commission_and_slippage() -> None:
    model = TransactionCostModel(commission_rate=0.001, slippage_rate=0.002, min_commission=1.0)

    assert model.calculate(10_000) == 30.0
    assert model.calculate(-10_000) == 30.0


def test_transaction_cost_model_applies_min_commission() -> None:
    model = TransactionCostModel(commission_rate=0.001, slippage_rate=0.0, min_commission=1.0)

    assert model.calculate(100) == 1.0
    assert model.calculate(0) == 0.0


def test_costs_reduce_backtest_nav() -> None:
    weights = pd.DataFrame({"AAA": [1.0]}, index=[pd.Timestamp("2024-01-02")])
    free = run_multi_asset_backtest(_prices(), weights)
    costly = run_multi_asset_backtest(
        _prices(),
        weights,
        cost_model=TransactionCostModel(commission_rate=0.01, slippage_rate=0.0),
    )

    assert free["nav"]["nav"].tolist() == [1.0, 1.0]
    assert costly["nav"]["nav"].tolist() == [0.99, 0.99]
    assert costly["orders"].loc[0, "cost"] == 0.01


def test_transaction_cost_model_validates_parameters() -> None:
    try:
        TransactionCostModel(commission_rate=-0.1)
    except ValueError as exc:
        assert "commission_rate" in str(exc)
    else:
        raise AssertionError("Expected negative commission rate to raise ValueError")
