import pandas as pd
import pytest

from index_platform.calendar import TradingCalendar


def test_is_trading_day_uses_weekdays_and_holidays() -> None:
    calendar = TradingCalendar("CN", holidays=frozenset({pd.Timestamp("2024-01-01")}))

    assert calendar.is_trading_day("2024-01-02") is True
    assert calendar.is_trading_day("2024-01-06") is False
    assert calendar.is_trading_day("2024-01-01") is False


def test_next_trading_day_skips_weekend() -> None:
    calendar = TradingCalendar("US")

    assert calendar.next_trading_day("2024-01-05") == pd.Timestamp("2024-01-08")


def test_rebalance_days_support_weekly_and_monthly() -> None:
    calendar = TradingCalendar("HK")

    weekly = calendar.rebalance_days("2024-01-01", "2024-01-12", "weekly")
    monthly = calendar.rebalance_days("2024-01-01", "2024-02-05", "monthly")

    assert list(weekly) == [pd.Timestamp("2024-01-05"), pd.Timestamp("2024-01-12")]
    assert list(monthly) == [pd.Timestamp("2024-01-31"), pd.Timestamp("2024-02-05")]


def test_unsupported_market_and_frequency_raise() -> None:
    with pytest.raises(ValueError, match="Unsupported market"):
        TradingCalendar("EU")

    with pytest.raises(ValueError, match="Unsupported rebalance frequency"):
        TradingCalendar("CN").rebalance_days("2024-01-01", "2024-01-05", "daily")
