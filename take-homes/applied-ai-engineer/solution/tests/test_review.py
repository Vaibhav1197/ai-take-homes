"""Unit tests for review.py -- the human-review queue artifacts."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from solution.pipeline.review import (
    load_review_decisions,
    queued_entries,
    sync_review_decisions,
    write_review_queue_markdown,
    record_decision,
    proposal_digest,
)


class TestQueuedEntries(unittest.TestCase):
    def test_filters_to_queued_status_only(self) -> None:
        all_entries = {
            "k1": {"status": "queued"},
            "k2": {"status": "filed"},
            "k3": {"status": "rejected"},
            "k4": {"status": "queued"},
        }
        result = queued_entries(all_entries)
        self.assertEqual(set(result.keys()), {"k1", "k4"})


class TestWriteReviewQueueMarkdown(unittest.TestCase):
    def test_nested_export_links_resolve_to_actual_source(self) -> None:
        root = Path(self._tmpdir.name)
        transcripts = root / "transcripts with spaces"
        transcripts.mkdir()
        source = transcripts / "call-001.md"
        source.write_text("source", encoding="utf-8")
        output = root / "artifacts" / "nested" / "queue.md"
        write_review_queue_markdown({"key": {"call_id": "call-001"}}, output, transcripts_dir=transcripts)
        self.assertIn("../../transcripts%20with%20spaces/call-001.md", output.read_text(encoding="utf-8"))

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.path = Path(self._tmpdir.name) / "review_queue.md"

    def test_empty_queue_says_so(self) -> None:
        write_review_queue_markdown({}, self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("Nothing awaiting review", text)

    def test_entry_content_rendered(self) -> None:
        entries = {
            "call-003#30#feature": {
                "status": "queued", "call_id": "call-003", "account": "Atlas Financial",
                "action": "file-new", "matched_key": None, "issue_type": "Feature",
                "priority": "P2", "confidence": 0.8, "summary": "SAML role mapping",
                "rationale": "no existing Feature issue matched", "description": "We need role assignment...",
            }
        }
        write_review_queue_markdown(entries, self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("SAML role mapping", text)
        self.assertIn("call-003#30#feature", text)
        self.assertIn("Atlas Financial", text)
        self.assertIn("file-new", text)
        self.assertIn("Feature", text)
        self.assertIn("0.80", text)

    def test_priority_ordering_p1_before_p3(self) -> None:
        entries = {
            "low": {"priority": "P3", "summary": "Low prio", "status": "queued"},
            "high": {"priority": "P1", "summary": "High prio", "status": "queued"},
        }
        write_review_queue_markdown(entries, self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertLess(text.index("High prio"), text.index("Low prio"))

    def test_matched_key_shown_when_present(self) -> None:
        entries = {
            "k1": {"priority": "P2", "summary": "Dup bug", "action": "corroborate",
                   "matched_key": "PROJ-087", "status": "queued"},
        }
        write_review_queue_markdown(entries, self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("matches `PROJ-087`", text)


class TestSyncReviewDecisions(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.path = Path(self._tmpdir.name) / "review_decisions.json"

    def test_creates_pending_scaffolding_for_new_keys(self) -> None:
        entries = {"k1": {"call_id": "call-001", "action": "file-new", "summary": "s", "priority": "P2"}}
        result = sync_review_decisions(entries, self.path)
        self.assertEqual(result["k1"]["decision"], "pending")
        self.assertEqual(result["k1"]["call_id"], "call-001")

    def test_never_overwrites_an_existing_decision(self) -> None:
        self.path.write_text(
            json.dumps({"k1": {"decision": "approved", "note": "looks real", "summary": "old summary"}}),
            encoding="utf-8",
        )
        entries = {"k1": {"call_id": "call-001", "action": "file-new", "summary": "new summary", "priority": "P2"}}
        result = sync_review_decisions(entries, self.path)
        self.assertEqual(result["k1"]["decision"], "approved")
        self.assertEqual(result["k1"]["note"], "looks real")
        self.assertEqual(result["k1"]["summary"], "old summary")  # untouched once decided

    def test_refreshes_context_fields_while_still_pending(self) -> None:
        self.path.write_text(
            json.dumps({"k1": {"decision": "pending", "note": "", "summary": "stale summary"}}),
            encoding="utf-8",
        )
        entries = {"k1": {"call_id": "call-001", "action": "file-new", "summary": "fresh summary", "priority": "P1"}}
        result = sync_review_decisions(entries, self.path)
        self.assertEqual(result["k1"]["decision"], "pending")
        self.assertEqual(result["k1"]["summary"], "fresh summary")

    def test_writes_result_to_disk(self) -> None:
        entries = {"k1": {"call_id": "call-001", "action": "file-new", "summary": "s", "priority": "P2"}}
        sync_review_decisions(entries, self.path)
        reloaded = load_review_decisions(self.path)
        self.assertIn("k1", reloaded)

    def test_keys_no_longer_queued_are_left_alone_not_deleted(self) -> None:
        """A key that was queued last run but isn't in `entries` this run
        (e.g. already applied and now status="filed") must not vanish from
        the decisions file -- it's a historical record, not a working set."""
        self.path.write_text(
            json.dumps({"old_key": {"decision": "approved", "note": ""}}), encoding="utf-8"
        )
        result = sync_review_decisions({}, self.path)
        self.assertIn("old_key", result)


class TestLoadReviewDecisions(unittest.TestCase):
    def test_records_identity_timing_and_exact_proposal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.json"
            entry = {"status": "queued", "summary": "Fix export", "priority": "P2"}
            record = record_decision(path, "key", entry, decision="approved", reviewer="Test reviewer",
                                     note="Verified source", elapsed_seconds=12.3456)
            self.assertEqual(record["elapsed_seconds"], 12.346)
            self.assertEqual(record["proposal_sha256"], proposal_digest(entry))
            self.assertEqual(load_review_decisions(path)["key"], record)
            with self.assertRaises(ValueError):
                record_decision(path, "key", entry, decision="rejected", reviewer="Other",
                                note="Changed mind", elapsed_seconds=1)

    def test_invalid_reviews_do_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.json"
            for fields in ({"reviewer": " "}, {"decision": "pending"},
                           {"decision": "rejected", "note": ""},
                           {"elapsed_seconds": float("nan")}):
                options = {"decision": "approved", "reviewer": "Tester", "note": "", "elapsed_seconds": 1}
                options.update(fields)
                with self.subTest(fields=fields), self.assertRaises(ValueError):
                    record_decision(path, "key", {"status": "queued"}, **options)
            self.assertFalse(path.exists())

    def test_missing_file_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "does_not_exist.json"
            self.assertEqual(load_review_decisions(path), {})


if __name__ == "__main__":
    unittest.main()
