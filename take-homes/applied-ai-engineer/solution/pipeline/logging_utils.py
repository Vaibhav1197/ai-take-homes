"""Structured JSONL event log for observability.

The README's ask: "if this ran unattended and silently started mis-filing
(or silently stopped), someone could tell from the output." One JSON object
per line, one line per event, append-only -- greppable, diffable, and
trivial to load into anything (`jq`, pandas, a log viewer) without a schema
migration every time a new event type is added, because there is no fixed
schema beyond `ts`/`event`; every event's other fields are just whatever the
caller passes in.

Deliberately a thin wrapper: this module has no opinion on *which* events
matter (that's orchestrator.py's job, e.g. emitting "call_failed" so a
partial failure is visible instead of silently swallowed). It only
guarantees each `emit()` call is a single atomic append -- concurrent writers
within one process won't interleave partial lines.
"""
from __future__ import annotations

import json
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class EventLogger:
    """Append-only JSONL writer. One instance per pipeline run is typical,
    but instances are independent (no shared global state) so tests can
    freely create throwaway loggers against a temp path."""

    def __init__(self, path: Optional[Path] = None, echo_to_stderr: bool = False) -> None:
        self.path = Path(path) if path else None
        self.echo_to_stderr = echo_to_stderr or self.path is None
        self._lock = threading.Lock()
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **fields: Any) -> dict[str, Any]:
        """Write one structured event. Returns the record actually written
        (useful in tests / for callers that want to echo it elsewhere)."""
        record: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **fields,
        }
        line = json.dumps(record, sort_keys=True, default=str)
        with self._lock:
            if self.path:
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(line + "\n")
            if self.echo_to_stderr:
                print(line, file=sys.stderr)
        return record

    def read_all(self) -> list[dict[str, Any]]:
        """All events recorded so far (requires a file-backed logger).
        Intended for tests and for the eval harness's observability checks,
        not for hot-path use."""
        if not self.path or not self.path.exists():
            return []
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events
