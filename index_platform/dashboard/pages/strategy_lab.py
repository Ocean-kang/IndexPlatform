"""Dashboard page for running simple strategy experiments."""

from __future__ import annotations

from pathlib import Path

from index_platform.backtest.runner import run_strategy_backtest
from index_platform.universe import load_indices


SUPPORTED_STRATEGIES = ["buy_hold", "moving_average", "momentum"]


def run_dashboard_backtest(
    strategy_name: str,
    symbols: list[str],
    data_dir: str | Path = "data/parquet",
    output_dir: str | Path = "outputs/backtests",
    start_date: str | None = None,
    end_date: str | None = None,
    strategy_params: dict[str, object] | None = None,
) -> str:
    """Run a dashboard-triggered backtest through the shared runner."""
    return run_strategy_backtest(
        strategy_name=strategy_name,
        symbols=symbols,
        data_dir=data_dir,
        output_dir=output_dir,
        start_date=start_date,
        end_date=end_date,
        strategy_params=strategy_params,
    )


def render_strategy_lab_page(st_module, data_dir: str | Path = "data/parquet") -> None:
    """Render the strategy lab page."""
    st_module.header("Strategy Lab")
    strategy_name = st_module.selectbox("Strategy", SUPPORTED_STRATEGIES)
    all_symbols = [index.symbol for index in load_indices()]
    default_symbols = all_symbols[:1] if strategy_name != "momentum" else all_symbols[:2]
    symbols = st_module.multiselect("Symbols", all_symbols, default=default_symbols)
    start_date = st_module.text_input("Start date", "")
    end_date = st_module.text_input("End date", "")

    params: dict[str, object] = {}
    if strategy_name == "moving_average":
        params["window"] = st_module.number_input("Window", min_value=1, value=20, step=1)
        params["execution_delay"] = st_module.number_input("Execution delay", min_value=0, value=1, step=1)
    elif strategy_name == "momentum":
        params["lookback"] = st_module.number_input("Lookback", min_value=1, value=20, step=1)
        params["top_k"] = st_module.number_input("Top K", min_value=1, value=1, step=1)
        params["rebalance_frequency"] = st_module.number_input("Rebalance frequency", min_value=1, value=20, step=1)
        params["execution_delay"] = st_module.number_input("Execution delay", min_value=0, value=1, step=1)

    if st_module.button("Run") and symbols:
        run_id = run_dashboard_backtest(
            strategy_name,
            symbols,
            data_dir=data_dir,
            start_date=start_date or None,
            end_date=end_date or None,
            strategy_params=params,
        )
        st_module.success(f"Run saved: {run_id}")
