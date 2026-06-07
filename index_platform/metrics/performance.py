"""Performance metrics calculated from NAV series."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def total_return(nav: pd.Series) -> float:
    """Calculate cumulative return from a NAV series."""
    clean_nav = _prepare_nav(nav)
    return float(clean_nav.iloc[-1] / clean_nav.iloc[0] - 1.0)


def annualized_return(nav: pd.Series, trading_days: int = 252) -> float:
    """Calculate annualized return from a NAV series."""
    clean_nav = _prepare_nav(nav)
    periods = len(clean_nav) - 1
    if periods <= 0:
        return 0.0
    return float((clean_nav.iloc[-1] / clean_nav.iloc[0]) ** (trading_days / periods) - 1.0)


def annualized_volatility(nav: pd.Series, trading_days: int = 252) -> float:
    """Calculate annualized volatility from daily NAV returns."""
    returns = _daily_returns(nav)
    if returns.empty:
        return 0.0
    return float(returns.std(ddof=0) * math.sqrt(trading_days))


def max_drawdown(nav: pd.Series) -> float:
    """Calculate max drawdown as a negative return from prior peak."""
    clean_nav = _prepare_nav(nav)
    drawdown = clean_nav / clean_nav.cummax() - 1.0
    return float(drawdown.min())


def sharpe_ratio(nav: pd.Series, risk_free_rate: float = 0.0, trading_days: int = 252) -> float:
    """Calculate annualized Sharpe ratio."""
    returns = _daily_returns(nav)
    if returns.empty:
        return 0.0

    daily_risk_free = risk_free_rate / trading_days
    excess_returns = returns - daily_risk_free
    volatility = excess_returns.std(ddof=0)
    if volatility == 0 or np.isnan(volatility):
        return 0.0
    return float(excess_returns.mean() / volatility * math.sqrt(trading_days))


def calmar_ratio(nav: pd.Series, trading_days: int = 252) -> float:
    """Calculate Calmar ratio from annualized return and max drawdown."""
    annual_return = annualized_return(nav, trading_days=trading_days)
    drawdown = abs(max_drawdown(nav))
    if drawdown == 0:
        return 0.0
    return float(annual_return / drawdown)


def calculate_performance_metrics(
    nav: pd.Series,
    risk_free_rate: float = 0.0,
    trading_days: int = 252,
) -> dict[str, float]:
    """Calculate all first-phase performance metrics."""
    return {
        "total_return": total_return(nav),
        "annualized_return": annualized_return(nav, trading_days=trading_days),
        "annualized_volatility": annualized_volatility(nav, trading_days=trading_days),
        "max_drawdown": max_drawdown(nav),
        "sharpe_ratio": sharpe_ratio(nav, risk_free_rate=risk_free_rate, trading_days=trading_days),
        "calmar_ratio": calmar_ratio(nav, trading_days=trading_days),
    }


def _prepare_nav(nav: pd.Series) -> pd.Series:
    clean_nav = pd.Series(nav).dropna().astype(float).reset_index(drop=True)
    if clean_nav.empty:
        raise ValueError("NAV series must not be empty.")
    if (clean_nav <= 0).any():
        raise ValueError("NAV values must be positive.")
    return clean_nav


def _daily_returns(nav: pd.Series) -> pd.Series:
    clean_nav = _prepare_nav(nav)
    return clean_nav.pct_change().dropna()

