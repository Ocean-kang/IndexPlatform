"""Dashboard page for browsing registered indices and local prices."""

from __future__ import annotations

from pathlib import Path

from index_platform.storage import load_price_data
from index_platform.universe import load_indices


def get_index_options(registry: str | Path | None = None) -> list[str]:
    """Return registered index symbols for selectors."""
    return [index.symbol for index in load_indices(registry)]


def get_index_price_data(symbol: str, data_dir: str | Path = "data/parquet"):
    """Load one index price table for display."""
    return load_price_data(data_dir, symbol=symbol)


def render_index_view_page(st_module, data_dir: str | Path = "data/parquet") -> None:
    """Render the index price viewer page."""
    st_module.header("Index View")
    symbols = get_index_options()
    symbol = st_module.selectbox("Symbol", symbols)
    if not symbol:
        return
    try:
        prices = get_index_price_data(symbol, data_dir)
    except FileNotFoundError:
        st_module.info(f"No local price data found in {data_dir}")
        return

    if prices.empty:
        st_module.info(f"No price rows found for {symbol}")
        return
    chart_data = prices.set_index("date")["close"]
    st_module.line_chart(chart_data)
    st_module.dataframe(prices, use_container_width=True)
