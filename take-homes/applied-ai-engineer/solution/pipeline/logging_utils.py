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
import uuid
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
        self.run_id = uuid.uuid4().hex
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: str, **fields: Any) -> dict[str, Any]:
        """Write one structured event. Returns the record actually written
        (useful in tests / for callers that want to echo it elsewhere)."""
        record: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "run_id": self.run_id,
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


def assess_health(events: list[dict[str, Any]], *, now: datetime | None = None,
                  max_age_seconds: float = 3600, expected_calls: int = 140,
                  baseline_candidates_per_call: float | None = None,
                  max_low_fraction: float = 0.25) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    alerts: list[dict[str, Any]] = []

    def alert(code: str, detail: Any) -> None:
        alerts.append({"code": code, "detail": detail})

    starts = [event for event in events if event.get("event") == "run_review_started"]
    latest = starts[-1] if starts else None
    completed = None
    if latest is None:
        alert("NO_REVIEW_RUN", "No start event; verify scheduler and log path.")
    else:
        run_events = [event for event in events if event.get("run_id") == latest.get("run_id")]
        completed = next((event for event in reversed(run_events) if event.get("event") == "run_review_completed"), None)
        last_event = run_events[-1]
        age = (now - datetime.fromisoformat(last_event["ts"])).total_seconds()
        if age > max_age_seconds:
            alert("STALE_REVIEW" if completed else "STALLED_REVIEW", {"age_seconds": age, "last_event": last_event["event"]})
        if latest.get("calls_discovered") != expected_calls:
            alert("INPUT_COVERAGE", {"expected": expected_calls, "discovered": latest.get("calls_discovered")})
        if completed:
            if completed.get("calls_failed", 0):
                alert("CALL_FAILURES", completed["calls_failed"])
            if completed.get("calls_processed", 0) + completed.get("calls_failed", 0) != expected_calls:
                alert("INCOMPLETE_BATCH", completed)
            processed = completed.get("calls_processed", 0)
            rate = completed.get("candidates_found", 0) / processed if processed else 0
            if processed and rate == 0:
                alert("ZERO_CANDIDATES", "Inspect judge/configuration; use candidate rate, not new queue count, on reruns.")
            if baseline_candidates_per_call and not 0.5 * baseline_candidates_per_call <= rate <= 2 * baseline_candidates_per_call:
                alert("CANDIDATE_RATE_DRIFT", {"actual": rate, "baseline": baseline_candidates_per_call})
            actions = completed.get("queue_by_action", {})
            total = sum(actions.values())
            if total and actions.get("file-new-low", 0) / total > max_low_fraction:
                alert("LOW_CONFIDENCE_BACKLOG", {"actions": actions, "max_fraction": max_low_fraction})
    apply_ends = [event for event in events if event.get("event") == "run_apply_completed"]
    if apply_ends and apply_ends[-1].get("failed", 0):
        alert("APPLY_FAILURES", apply_ends[-1]["failed"])
    return {"healthy": not alerts, "alerts": alerts,
            "review_state": "completed" if completed else "running" if latest else "missing",
            "latest_review_run_id": latest.get("run_id") if latest else None,
            "latest_summary": completed,
            "limits": {"expected_calls": expected_calls, "max_age_seconds": max_age_seconds,
                       "max_low_fraction": max_low_fraction, "baseline_candidates_per_call": baseline_candidates_per_call}}
