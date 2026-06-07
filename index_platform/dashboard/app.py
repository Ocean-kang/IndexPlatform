"""Streamlit dashboard entry point."""

from __future__ import annotations

from index_platform.dashboard.pages.backtest_result import render_backtest_result_page
from index_platform.dashboard.pages.data_status import render_data_status_page
from index_platform.dashboard.pages.index_view import render_index_view_page
from index_platform.dashboard.pages.run_monitor import render_run_monitor_page
from index_platform.dashboard.pages.strategy_lab import render_strategy_lab_page


def main() -> None:
    """Run the Streamlit dashboard."""
    import streamlit as st

    st.set_page_config(page_title="IndexPlatform", layout="wide")
    st.title("IndexPlatform")

    page = st.sidebar.radio(
        "Page",
        ["Data Status", "Index View", "Strategy Lab", "Backtest Result", "Run Monitor"],
    )
    if page == "Data Status":
        render_data_status_page(st)
    elif page == "Index View":
        render_index_view_page(st)
    elif page == "Strategy Lab":
        render_strategy_lab_page(st)
    elif page == "Backtest Result":
        render_backtest_result_page(st)
    else:
        render_run_monitor_page(st)


if __name__ == "__main__":
    main()
