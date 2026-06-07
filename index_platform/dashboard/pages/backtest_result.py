"""Dashboard page for saved backtest results."""

from __future__ import annotations

from pathlib import Path

from index_platform.storage.backtest_store import load_backtest_result


def list_backtest_runs(base_dir: str | Path = "outputs/backtests") -> list[str]:
    """List saved backtest run identifiers."""
    root = Path(base_dir)
    if not root.exists():
        return []
    return sorted(path.name for path in root.iterdir() if path.is_dir())


def get_backtest_result(base_dir: str | Path, run_id: str) -> dict[str, object]:
    """Load one saved backtest run for display."""
    return load_backtest_result(base_dir, run_id)


def render_backtest_result_page(st_module, base_dir: str | Path = "outputs/backtests") -> None:
    """Render saved backtest results."""
    st_module.header("Backtest Result")
    run_ids = list_backtest_runs(base_dir)
    if not run_ids:
        st_module.info(f"No backtest runs found in {base_dir}")
        return

    run_id = st_module.selectbox("Run ID", run_ids)
    result = get_backtest_result(base_dir, run_id)
    st_module.subheader(run_id)
    st_module.json(result["metrics"])
    nav = result["nav"]
    if "date" in nav.columns and "nav" in nav.columns:
        st_module.line_chart(nav.set_index("date")["nav"])
    st_module.dataframe(nav, use_container_width=True)
