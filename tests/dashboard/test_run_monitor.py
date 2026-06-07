from pathlib import Path

from index_platform.dashboard.pages.run_monitor import get_run_monitor_rows
from index_platform.monitor import update_run_state


def test_run_monitor_reads_state_rows(tmp_path: Path) -> None:
    update_run_state("run_1", "success", tmp_path)

    rows = get_run_monitor_rows(tmp_path)

    assert rows[0]["run_id"] == "run_1"
    assert rows[0]["state"] == "success"
