"""Unit tests for dedup.py -- TF-IDF matching against tracked issues, issue
type isolation, shipped-issue handling, and the growing pending-key pool.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from solution.pipeline.dedup import (
    DEFAULT_SIMILARITY_THRESHOLD,
    Deduplicator,
    load_existing_issues,
)
from solution.pipeline.models import Action, Candidate, ExistingIssue


def _make_issue(
    key: str, type_: str = "Bug", status: str = "Open",
    summary: str = "Search results are stale after a member rename",
    description: str = "Renaming a member does not refresh the search index for up to 24 hours.",
    shipped_in: str | None = None,
) -> ExistingIssue:
    return ExistingIssue(
        key=key, type=type_, status=status, summary=summary, description=description,
        created="2024-01-01T00:00:00+00:00", reported_by_accounts=(), shipped_in=shipped_in,
    )


def _make_candidate(
    signal_type: str = "bug",
    draft_title: str = "Search results are stale after a member rename",
    snippet: str = "The search index doesn't update after we rename a member for up to a day.",
) -> Candidate:
    return Candidate(
        call_id="call-001", account="Acme Corp", primary_turn_index=5, turn_span=(3, 7),
        snippet=snippet, signal_type=signal_type, draft_title=draft_title,
    )


class TestLoadExistingIssues(unittest.TestCase):
    def test_parses_required_and_optional_fields(self) -> None:
        raw = [
            {
                "key": "PROJ-1001", "type": "Bug", "status": "Open",
                "summary": "s", "description": "d", "created": "2024-01-01",
                "reported_by_accounts": ["Acme Corp"],
            },
            {
                "key": "PROJ-1002", "type": "Feature", "status": "Shipped",
                "summary": "s2", "description": "d2", "created": "2024-02-01",
                "shipped_in": "v2.3",
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing_issues.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            issues = load_existing_issues(path)

        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].reported_by_accounts, ("Acme Corp",))
        self.assertIsNone(issues[0].shipped_in)
        self.assertEqual(issues[1].shipped_in, "v2.3")
        self.assertTrue(issues[1].is_shipped)


class TestDeduplicatorEvaluate(unittest.TestCase):
    def test_empty_pool_files_new(self) -> None:
        dedup = Deduplicator([])
        outcome = dedup.evaluate(_make_candidate())
        self.assertEqual(outcome.action, Action.FILE_NEW)
        self.assertIsNone(outcome.matched_key)
        self.assertEqual(outcome.similarity, 0.0)

    def test_similar_candidate_corroborates_against_matching_issue(self) -> None:
        dedup = Deduplicator([_make_issue("PROJ-2001")])
        outcome = dedup.evaluate(_make_candidate())
        self.assertEqual(outcome.action, Action.CORROBORATE)
        self.assertEqual(outcome.matched_key, "PROJ-2001")
        self.assertGreaterEqual(outcome.similarity, DEFAULT_SIMILARITY_THRESHOLD)

    def test_dissimilar_candidate_files_new(self) -> None:
        dedup = Deduplicator([_make_issue("PROJ-2001")])
        candidate = _make_candidate(
            draft_title="API access to engagement metrics",
            snippet="We want an API endpoint to pull engagement metrics into our warehouse.",
        )
        outcome = dedup.evaluate(candidate)
        self.assertEqual(outcome.action, Action.FILE_NEW)
        self.assertIsNone(outcome.matched_key)
        self.assertLess(outcome.similarity, DEFAULT_SIMILARITY_THRESHOLD)

    def test_shipped_issue_match_resolves_to_none_action(self) -> None:
        dedup = Deduplicator([_make_issue("PROJ-2001", status="Shipped", shipped_in="v2.3")])
        outcome = dedup.evaluate(_make_candidate())
        self.assertEqual(outcome.action, Action.NONE)
        self.assertEqual(outcome.matched_key, "PROJ-2001")
        self.assertIn("PROJ-2001", outcome.rationale)

    def test_bug_candidate_never_matches_feature_pool(self) -> None:
        """Same text, but tracked only as a Feature -- issue-type isolation
        must prevent a false corroboration across types."""
        dedup = Deduplicator([_make_issue("PROJ-2001", type_="Feature")])
        outcome = dedup.evaluate(_make_candidate(signal_type="bug"))
        self.assertEqual(outcome.action, Action.FILE_NEW)
        self.assertIsNone(outcome.matched_key)

    def test_feature_candidate_never_matches_bug_pool(self) -> None:
        dedup = Deduplicator([_make_issue("PROJ-2001", type_="Bug")])
        outcome = dedup.evaluate(_make_candidate(signal_type="feature"))
        self.assertEqual(outcome.action, Action.FILE_NEW)
        self.assertIsNone(outcome.matched_key)

    def test_evaluate_does_not_mutate_pool(self) -> None:
        dedup = Deduplicator([_make_issue("PROJ-2001")])
        dedup.evaluate(_make_candidate())
        dedup.evaluate(_make_candidate())  # calling twice must not change the outcome
        outcome = dedup.evaluate(_make_candidate())
        self.assertEqual(outcome.matched_key, "PROJ-2001")


class TestGrowingPool(unittest.TestCase):
    def test_registered_candidate_is_matchable_by_a_later_one(self) -> None:
        dedup = Deduplicator([])
        first = _make_candidate()
        outcome1 = dedup.evaluate(first)
        self.assertEqual(outcome1.action, Action.FILE_NEW)

        pending_key = dedup.next_pending_key()
        dedup.register_new(pending_key, first)

        second = _make_candidate(snippet="Yeah, our search index is stale for a day after renames too.")
        outcome2 = dedup.evaluate(second)
        self.assertEqual(outcome2.action, Action.CORROBORATE)
        self.assertEqual(outcome2.matched_key, pending_key)

    def test_pending_keys_increment_sequentially(self) -> None:
        dedup = Deduplicator([])
        self.assertEqual(dedup.next_pending_key(), "PENDING:1")
        self.assertEqual(dedup.next_pending_key(), "PENDING:2")
        self.assertEqual(dedup.next_pending_key(), "PENDING:3")

    def test_register_new_respects_candidate_issue_type(self) -> None:
        dedup = Deduplicator([])
        feature_candidate = _make_candidate(signal_type="feature")
        dedup.register_new("PENDING:1", feature_candidate)
        # A bug candidate with similar text must NOT match the just-registered feature pending entry.
        bug_outcome = dedup.evaluate(_make_candidate(signal_type="bug"))
        self.assertEqual(bug_outcome.action, Action.FILE_NEW)


if __name__ == "__main__":
    unittest.main()
