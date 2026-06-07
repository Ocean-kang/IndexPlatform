"""Simple daily backtest engine."""

from __future__ import annotations

import pandas as pd

from index_platform.backtest.costs import TransactionCostModel
from index_platform.data.validators import normalize_daily_price_data
from index_platform.strategy.base import Strategy


def run_backtest(price_data: pd.DataFrame, strategy: Strategy) -> pd.DataFrame:
    """Run a single-index daily close-price backtest."""
    prices = normalize_daily_price_data(price_data).sort_values("date").reset_index(drop=True)
    symbols = prices["symbol"].dropna().unique()
    if len(symbols) != 1:
        raise ValueError("The first backtest engine supports exactly one symbol.")
    if prices.empty:
        raise ValueError("Price data must not be empty.")
    if (prices["close"] <= 0).any():
        raise ValueError("Close prices must be positive.")

    positions = strategy.generate_positions(prices).reset_index(drop=True).astype(float)
    if len(positions) != len(prices):
        raise ValueError("Strategy positions must match price data length.")
    if (positions < 0).any():
        raise ValueError("The first backtest engine only supports long-only positions.")

    returns = prices["close"].pct_change().fillna(0.0)
    strategy_returns = returns * positions.shift(1).fillna(positions.iloc[0])
    nav = (1.0 + strategy_returns).cumprod()
    nav.iloc[0] = 1.0

    return pd.DataFrame(
        {
            "date": prices["date"],
            "symbol": prices["symbol"],
            "close": prices["close"],
            "position": positions,
            "nav": nav,
        }
    )


def run_multi_asset_backtest(
    price_data: pd.DataFrame,
    target_weights: pd.DataFrame,
    initial_nav: float = 1.0,
    cost_model: TransactionCostModel | None = None,
) -> dict[str, pd.DataFrame]:
    """Run a long-only multi-asset portfolio backtest.

    ``target_weights`` is indexed by rebalance date and has one column per
    symbol. Dates missing from the matrix are treated as non-rebalance days, so
    existing positions drift with close prices.
    """
    if initial_nav <= 0:
        raise ValueError("initial_nav must be positive.")

    closes = _close_price_matrix(price_data)
    weights = _prepare_target_weights(target_weights, closes)

    cash = float(initial_nav)
    cost_model = cost_model or TransactionCostModel()
    shares = pd.Series(0.0, index=closes.columns)
    nav_rows: list[dict[str, object]] = []
    position_rows: list[dict[str, object]] = []
    order_rows: list[dict[str, object]] = []

    for date, current_prices in closes.iterrows():
        portfolio_value = cash + float((shares * current_prices).sum())
        target_row = weights.loc[date]

        if target_row.notna().any():
            target = target_row.fillna(0.0).astype(float)
            _validate_weight_row(target)

            current_values = shares * current_prices
            target_values = portfolio_value * target
            trade_values = target_values - current_values
            costs = trade_values.apply(cost_model.calculate)
            shares = shares + trade_values / current_prices
            cash -= float(trade_values.sum() + costs.sum())

            for symbol, trade_value in trade_values.items():
                if abs(float(trade_value)) <= 1e-12:
                    continue
                order_rows.append(
                    {
                        "date": date,
                        "symbol": symbol,
                        "trade_value": float(trade_value),
                        "price": float(current_prices[symbol]),
                        "quantity": float(trade_value / current_prices[symbol]),
                        "cost": float(costs[symbol]),
                    }
                )

        portfolio_value = cash + float((shares * current_prices).sum())
        nav_rows.append({"date": date, "nav": portfolio_value / initial_nav})

        values = shares * current_prices
        for symbol, value in values.items():
            position_rows.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "market_value": float(value),
                    "weight": float(value / portfolio_value) if portfolio_value else 0.0,
                }
            )

    return {
        "nav": pd.DataFrame(nav_rows),
        "positions": pd.DataFrame(position_rows),
        "orders": pd.DataFrame(
            order_rows,
            columns=["date", "symbol", "trade_value", "price", "quantity", "cost"],
        ),
    }


def _close_price_matrix(price_data: pd.DataFrame) -> pd.DataFrame:
    prices = normalize_daily_price_data(price_data)
    if prices.empty:
        raise ValueError("Price data must not be empty.")
    closes = prices.pivot(index="date", columns="symbol", values="close").sort_index()
    if closes.isna().any().any():
        raise ValueError("Price data must contain a close price for every symbol/date.")
    if (closes <= 0).any().any():
        raise ValueError("Close prices must be positive.")
    return closes


def _prepare_target_weights(target_weights: pd.DataFrame, closes: pd.DataFrame) -> pd.DataFrame:
    if target_weights.empty:
        raise ValueError("target_weights must not be empty.")

    weights = target_weights.copy()
    weights.index = pd.to_datetime(weights.index).normalize()
    unknown_symbols = set(weights.columns) - set(closes.columns)
    if unknown_symbols:
        raise ValueError(f"Target weights contain unknown symbols: {', '.join(sorted(unknown_symbols))}")

    weights = weights.reindex(columns=closes.columns)
    for _, row in weights.iterrows():
        if row.notna().any():
            _validate_weight_row(row.fillna(0.0).astype(float))
    return weights.reindex(closes.index)


def _validate_weight_row(weights: pd.Series) -> None:
    if (weights < 0).any():
        raise ValueError("Target weights must be non-negative.")
    if float(weights.sum()) > 1.0 + 1e-12:
        raise ValueError("Target weights must sum to no more than 1.")
