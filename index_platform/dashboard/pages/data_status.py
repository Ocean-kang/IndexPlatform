"""Dashboard page for local price data status."""

from __future__ import annotations

from pathlib import Path

from index_platform.data.quality import check_daily_price_quality, summarize_data_status
from index_platform.storage import load_price_data


def get_data_status(data_dir: str | Path = "data/parquet") -> dict[str, object]:
    """Return reusable local data status fields for display."""
    try:
        prices = load_price_data(data_dir)
    except FileNotFoundError:
        return {"exists": False, "summary": None, "issues": [], "prices": None}

    return {
        "exists": True,
        "summary": summarize_data_status(prices),
        "issues": check_daily_price_quality(prices),
        "prices": prices,
    }


def render_data_status_page(st_module, data_dir: str | Path = "data/parquet") -> None:
    """Render the data status dashboard page."""
    st_module.header("Data Status")
    status = get_data_status(data_dir)
    if not status["exists"]:
        st_module.info(f"No local price data found in {data_dir}")
        return

    prices = status["prices"]
    summary = status["summary"]
    issues = status["issues"]
    st_module.metric("Rows", len(prices))
    st_module.dataframe(summary, use_container_width=True)
    if issues:
        st_module.dataframe([issue.__dict__ for issue in issues], use_container_width=True)
    else:
        st_module.success("No quality issues found.")
