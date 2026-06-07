import pandas as pd

from index_platform.strategy.buy_hold import BuyAndHoldStrategy


def test_buy_hold_generates_constant_long_position() -> None:
    prices = pd.DataFrame({"close": [100, 101, 102]})
    strategy = BuyAndHoldStrategy()

    positions = strategy.generate_positions(prices)

    assert strategy.name == "buy_hold"
    assert positions.tolist() == [1.0, 1.0, 1.0]
    assert positions.index.equals(prices.index)

