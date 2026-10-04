"""Unit tests for logging_utils.py -- structured JSONL event logging."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from solution.pipeline.logging_utils import EventLogger, assess_health


class TestEventLogger(unittest.TestCase):
    def test_stale_completed_run_still_alerts(self) -> None:
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        events = [{"event": "run_review_started", "run_id": "run", "ts": old, "calls_discovered": 140},
                  {"event": "run_review_completed", "run_id": "run", "ts": old, "calls_processed": 140,
                   "calls_failed": 0, "candidates_found": 217}]
        self.assertIn("STALE_REVIEW", {alert["code"] for alert in assess_health(events)["alerts"]})

    def test_missing_and_stalled_runs_alert(self) -> None:
        self.assertEqual(assess_health([])["alerts"][0]["code"], "NO_REVIEW_RUN")
        old = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        events = [{"event": "run_review_started", "run_id": "run", "ts": old, "calls_discovered": 140}]
        self.assertIn("STALLED_REVIEW", {alert["code"] for alert in assess_health(events)["alerts"]})

    def test_bad_completed_run_exposes_counts(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        events = [{"event": "run_review_started", "run_id": "run", "ts": now, "calls_discovered": 139},
                  {"event": "run_review_completed", "run_id": "run", "ts": now, "calls_processed": 138,
                   "calls_failed": 1, "candidates_found": 0, "queue_by_action": {"file-new-low": 9, "file-new": 1}}]
        codes = {alert["code"] for alert in assess_health(events, baseline_candidates_per_call=1)["alerts"]}
        self.assertTrue({"INPUT_COVERAGE", "INCOMPLETE_BATCH", "CALL_FAILURES", "ZERO_CANDIDATES",
                         "CANDIDATE_RATE_DRIFT", "LOW_CONFIDENCE_BACKLOG"}.issubset(codes))

    def test_no_new_queue_on_rerun_is_not_a_silent_stop(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        events = [{"event": "run_review_started", "run_id": "run", "ts": now, "calls_discovered": 140},
                  {"event": "run_review_completed", "run_id": "run", "ts": now, "calls_processed": 140,
                   "calls_failed": 0, "candidates_found": 200, "queued_for_review": 0}]
        self.assertTrue(assess_health(events)["healthy"])

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.path = Path(self._tmpdir.name) / "events.jsonl"

    def test_emit_writes_one_json_line(self) -> None:
        logger = EventLogger(self.path)
        logger.emit("call_started", call_id="call-001")
        lines = self.path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["event"], "call_started")
        self.assertEqual(record["call_id"], "call-001")
        self.assertIn("ts", record)

    def test_multiple_emits_append(self) -> None:
        logger = EventLogger(self.path)
        logger.emit("call_started", call_id="call-001")
        logger.emit("call_completed", call_id="call-001", n_candidates=2)
        lines = self.path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)

    def test_read_all_round_trips_emitted_events(self) -> None:
        logger = EventLogger(self.path)
        logger.emit("run_started", n_calls=140)
        logger.emit("call_failed", call_id="call-047", error="parse error")
        events = logger.read_all()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["event"], "run_started")
        self.assertEqual(events[1]["call_id"], "call-047")

    def test_read_all_on_nonexistent_file_returns_empty(self) -> None:
        logger = EventLogger(self.path)  # never emits, file never created
        self.assertEqual(logger.read_all(), [])

    def test_emit_returns_the_written_record(self) -> None:
        logger = EventLogger(self.path)
        record = logger.emit("ticket_filed", issue_key="PROJ-1042")
        self.assertEqual(record["event"], "ticket_filed")
        self.assertEqual(record["issue_key"], "PROJ-1042")

    def test_non_json_native_field_is_stringified_not_fatal(self) -> None:
        logger = EventLogger(self.path)
        logger.emit("weird", value=object())  # must not raise
        events = logger.read_all()
        self.assertEqual(len(events), 1)

    def test_no_path_echoes_to_stderr_without_raising(self) -> None:
        logger = EventLogger(path=None)
        record = logger.emit("run_started", n_calls=1)  # must not raise
        self.assertEqual(record["event"], "run_started")


if __name__ == "__main__":
    unittest.main()
