"""File-based run state tracking."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


VALID_STATES = {"pending", "running", "success", "failed"}


def update_run_state(
    run_id: str,
    state: str,
    base_dir: str | Path = "outputs/run_state",
    message: str | None = None,
) -> Path:
    """Write the current state for a run."""
    if state not in VALID_STATES:
        raise ValueError(f"Invalid run state: {state}")
    target_dir = Path(base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "state": state,
        "message": message or "",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    target = target_dir / f"{run_id}.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def load_run_state(run_id: str, base_dir: str | Path = "outputs/run_state") -> dict[str, str]:
    """Load one run state file."""
    source = Path(base_dir) / f"{run_id}.json"
    if not source.exists():
        raise FileNotFoundError(f"Run state not found: {run_id}")
    return json.loads(source.read_text(encoding="utf-8"))


def list_run_states(base_dir: str | Path = "outputs/run_state") -> list[dict[str, str]]:
    """List run states sorted by update time."""
    root = Path(base_dir)
    if not root.exists():
        return []
    states = [json.loads(path.read_text(encoding="utf-8")) for path in root.glob("*.json")]
    return sorted(states, key=lambda item: item.get("updated_at", ""), reverse=True)
