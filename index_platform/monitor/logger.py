"""Simple file logger for runs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


def append_run_log(run_id: str, message: str, log_dir: str | Path = "outputs/logs") -> Path:
    """Append one timestamped line to a run log."""
    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{run_id}.log"
    timestamp = datetime.now(timezone.utc).isoformat()
    with target.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} {message}\n")
    return target
