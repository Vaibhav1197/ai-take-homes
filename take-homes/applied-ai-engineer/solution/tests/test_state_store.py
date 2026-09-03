"""Unit tests for state_store.py -- the pipeline's cross-run idempotency ledger."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from solution.pipeline.models import Candidate
from solution.pipeline.state_store import StateStore, candidate_key


def _make_candidate(call_id: str = "call-001", primary_turn_index: int = 5, signal_type: str = "bug") -> Candidate:
    return Candidate(
        call_id=call_id,
        account="Acme Corp",
        primary_turn_index=primary_turn_index,
        turn_span=(3, 7),
        snippet="The export button is broken.",
        signal_type=signal_type,
    )


class TestCandidateKey(unittest.TestCase):
    def test_key_is_stable_for_identical_candidates(self) -> None:
        a = _make_candidate()
        b = _make_candidate()
        self.assertEqual(candidate_key(a), candidate_key(b))

    def test_key_differs_by_call_id(self) -> None:
        a = _make_candidate(call_id="call-001")
        b = _make_candidate(call_id="call-002")
        self.assertNotEqual(candidate_key(a), candidate_key(b))

    def test_key_differs_by_signal_type(self) -> None:
        a = _make_candidate(signal_type="bug")
        b = _make_candidate(signal_type="feature")
        self.assertNotEqual(candidate_key(a), candidate_key(b))

    def test_key_stable_across_turn_span_drift(self) -> None:
        """Same anchor turn, different span bounds (e.g. a non-deterministic
        judge widening its window slightly run to run) must still produce
        the same key -- that's the whole point of anchoring on
        primary_turn_index rather than the full span."""
        a = Candidate(
            call_id="call-001", account="Acme", primary_turn_index=10,
            turn_span=(8, 12), snippet="x", signal_type="bug",
        )
        b = Candidate(
            call_id="call-001", account="Acme", primary_turn_index=10,
            turn_span=(9, 14), snippet="y", signal_type="bug",
        )
        self.assertEqual(candidate_key(a), candidate_key(b))


class TestStateStore(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.path = Path(self._tmpdir.name) / "ledger.json"

    def test_get_missing_key_returns_none(self) -> None:
        store = StateStore(self.path)
        self.assertIsNone(store.get("nope"))

    def test_upsert_creates_and_persists_entry(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="queued", summary="thing")
        self.assertTrue(self.path.exists())

        # A fresh StateStore instance pointed at the same path must see it --
        # proves persistence (not just in-memory state).
        reloaded = StateStore(self.path)
        entry = reloaded.get("k1")
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry["status"], "queued")
        self.assertEqual(entry["summary"], "thing")

    def test_upsert_merges_rather_than_overwrites(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="queued", summary="thing")
        store.upsert("k1", status="approved")
        entry = store.get("k1")
        assert entry is not None
        self.assertEqual(entry["status"], "approved")
        self.assertEqual(entry["summary"], "thing")  # untouched by the second upsert

    def test_upsert_returns_the_updated_entry(self) -> None:
        store = StateStore(self.path)
        result = store.upsert("k1", status="queued")
        self.assertEqual(result, {"status": "queued"})

    def test_all_entries_is_a_read_only_snapshot(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="queued")
        snapshot = store.all_entries()
        snapshot["k1"]["status"] = "mutated"
        snapshot["k2"] = {"status": "should not appear"}
        # Mutating the returned snapshot must not affect the store's own state.
        self.assertEqual(store.get("k1"), {"status": "queued"})
        self.assertIsNone(store.get("k2"))

    def test_filed_issues_reconstructs_only_filed_entries(self) -> None:
        store = StateStore(self.path)
        store.upsert(
            "k1", status="filed", issue_key="PROJ-2001", issue_type="Bug",
            summary="Search stale after rename", description="details here",
            filed_at="2024-06-01T00:00:00+00:00", reported_by_accounts=["Harborline Media"],
        )
        store.upsert("k2", status="queued", summary="not filed yet")
        store.upsert("k3", status="rejected", summary="human said no")

        issues = store.filed_issues()
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].key, "PROJ-2001")
        self.assertEqual(issues[0].type, "Bug")
        self.assertEqual(issues[0].summary, "Search stale after rename")
        self.assertEqual(issues[0].reported_by_accounts, ("Harborline Media",))
        self.assertFalse(issues[0].is_shipped)

    def test_filed_entry_missing_issue_key_is_excluded(self) -> None:
        """Defensive: an entry marked filed without an issue_key (shouldn't
        happen, but must not crash or fabricate a bogus ExistingIssue)."""
        store = StateStore(self.path)
        store.upsert("k1", status="filed")
        self.assertEqual(store.filed_issues(), [])

    def test_survives_process_restart_with_multiple_entries(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="filed", issue_key="PROJ-1", issue_type="Bug", summary="a")
        store.upsert("k2", status="queued", summary="b")

        reloaded = StateStore(self.path)
        self.assertEqual(len(reloaded.all_entries()), 2)
        self.assertEqual(reloaded.get("k1")["status"], "filed")  # type: ignore[index]
        self.assertEqual(reloaded.get("k2")["status"], "queued")  # type: ignore[index]

    def test_ledger_file_is_valid_json_with_version(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="queued")
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertIn("version", raw)
        self.assertIn("entries", raw)
        self.assertIn("k1", raw["entries"])

    def test_no_leftover_temp_files_after_upsert(self) -> None:
        store = StateStore(self.path)
        store.upsert("k1", status="queued")
        store.upsert("k2", status="approved")
        siblings = list(self.path.parent.iterdir())
        self.assertEqual(siblings, [self.path])


if __name__ == "__main__":
    unittest.main()
