from pathlib import Path

import pytest

from index_platform.monitor import append_run_log, list_run_states, load_run_state, update_run_state


def test_update_load_and_list_run_state(tmp_path: Path) -> None:
    update_run_state("run_1", "running", tmp_path, message="started")

    state = load_run_state("run_1", tmp_path)
    states = list_run_states(tmp_path)

    assert state["state"] == "running"
    assert state["message"] == "started"
    assert states[0]["run_id"] == "run_1"


def test_invalid_run_state_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Invalid run state"):
        update_run_state("run_1", "unknown", tmp_path)


def test_append_run_log(tmp_path: Path) -> None:
    path = append_run_log("run_1", "hello", tmp_path)

    assert "hello" in path.read_text(encoding="utf-8")
