"""Feature helpers for lightweight prediction baselines."""

from __future__ import annotations

import pandas as pd

from index_platform.data.validators import normalize_daily_price_data


def make_return_features(price_df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Create trailing return features using only current and past closes."""
    if window <= 0:
        raise ValueError("window must be positive.")
    prices = normalize_daily_price_data(price_df).sort_values("date").reset_index(drop=True)
    symbols = prices["symbol"].dropna().unique()
    if len(symbols) != 1:
        raise ValueError("make_return_features supports exactly one symbol in the first version.")
    if (prices["close"] <= 0).any():
        raise ValueError("Close prices must be positive.")

    closes = prices["close"].astype(float)
    daily_return = closes.pct_change()
    features = pd.DataFrame(
        {
            "date": prices["date"],
            "symbol": prices["symbol"],
            "close": closes,
            "daily_return": daily_return,
            f"return_{window}d": closes.pct_change(window),
            f"mean_return_{window}d": daily_return.rolling(window, min_periods=window).mean(),
        }
    )
    return features
