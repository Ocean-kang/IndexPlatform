import pandas as pd

from index_platform.metrics.performance import (
    annualized_return,
    annualized_volatility,
    calculate_performance_metrics,
    calmar_ratio,
    max_drawdown,
    sharpe_ratio,
    total_return,
)


def test_performance_metrics_for_toy_nav() -> None:
    nav = pd.Series([1.0, 1.1, 0.99, 1.2])

    metrics = calculate_performance_metrics(nav, trading_days=3)

    assert round(metrics["total_return"], 6) == 0.2
    assert round(metrics["annualized_return"], 6) == 0.2
    assert round(metrics["max_drawdown"], 6) == -0.1
    assert round(metrics["calmar_ratio"], 6) == 2.0
    assert metrics["annualized_volatility"] > 0
    assert metrics["sharpe_ratio"] != 0


def test_max_drawdown_uses_prior_peak() -> None:
    nav = pd.Series([1.0, 1.5, 1.2, 1.6])

    assert round(max_drawdown(nav), 6) == -0.2


def test_single_point_nav_has_explicit_zero_metrics() -> None:
    nav = pd.Series([1.0])

    assert total_return(nav) == 0.0
    assert annualized_return(nav) == 0.0
    assert annualized_volatility(nav) == 0.0
    assert max_drawdown(nav) == 0.0
    assert sharpe_ratio(nav) == 0.0
    assert calmar_ratio(nav) == 0.0


def test_empty_nav_raises_clear_error() -> None:
    try:
        calculate_performance_metrics(pd.Series(dtype=float))
    except ValueError as exc:
        assert "NAV series must not be empty" in str(exc)
    else:
        raise AssertionError("Expected empty NAV to raise ValueError")


def test_non_positive_nav_raises_clear_error() -> None:
    try:
        total_return(pd.Series([1.0, 0.0]))
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("Expected non-positive NAV to raise ValueError")

