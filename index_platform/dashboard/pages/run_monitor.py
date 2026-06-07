"""Dashboard page for run monitoring."""

from __future__ import annotations

from pathlib import Path

from index_platform.monitor import list_run_states


def get_run_monitor_rows(state_dir: str | Path = "outputs/run_state") -> list[dict[str, str]]:
    """Return run state rows for display."""
    return list_run_states(state_dir)


def render_run_monitor_page(st_module, state_dir: str | Path = "outputs/run_state") -> None:
    """Render run monitor page."""
    st_module.header("Run Monitor")
    rows = get_run_monitor_rows(state_dir)
    if not rows:
        st_module.info(f"No run states found in {state_dir}")
        return
    st_module.dataframe(rows, use_container_width=True)
