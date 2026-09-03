"""Integration tests for orchestrator.py -- run_review()/run_apply() wiring,
idempotency, partial-failure isolation, and same-call duplicate collapsing.

Uses a fake IssueJudge (so tests are independent of heuristic keyword
tuning) and fake jira_stub/slack_stub collaborators (so tests never touch
the real stubs/outbox/*.jsonl files, which are actual deliverable output).
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from solution.pipeline import orchestrator
from solution.pipeline.config import Config
from solution.pipeline.models import Candidate, Transcript
from solution.pipeline.review import load_review_decisions
from solution.pipeline.state_store import StateStore, candidate_key

_TRANSCRIPT_TEMPLATE = """# Call \u2014 {account} \u00d7 BetterBark \u00b7 Support
Date: 2026-06-01 \u00b7 Call ID: {call_id}
Participants: [EXTERNAL] Jamie Lee ({account}) \u00b7 [INTERNAL] Riley Chen, Support

[EXTERNAL] Jamie: Just checking in, all good here.
[INTERNAL] Riley: Great to hear!
[EXTERNAL] Jamie: One more thing, nothing major.
[INTERNAL] Riley: Noted, thanks.
"""


class _FakeJudge:
    """Deterministic fake IssueJudge returning pre-built candidates per call
    id, bypassing real keyword heuristics entirely."""

    def __init__(self, candidates_by_call: dict[str, list[Candidate]]) -> None:
        self._by_call = candidates_by_call

    def find_candidates(self, transcript: Transcript) -> list[Candidate]:
        return self._by_call.get(transcript.call_id, [])


class _FakeJira:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self._next = 9001

    def create_issue(self, payload: dict) -> dict:
        self.calls.append(payload)
        record = {"key": f"PROJ-{self._next}", **payload}
        self._next += 1
        return record


class _FakeSlack:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post_message(self, payload: dict) -> dict:
        self.calls.append(payload)
        return {"ts": "fake-ts", **payload}


def _write_transcript(directory: Path, call_id: str, account: str = "Acme Corp") -> None:
    text = _TRANSCRIPT_TEMPLATE.format(call_id=call_id, account=account)
    (directory / f"{call_id}.md").write_text(text, encoding="utf-8")


def _write_broken_transcript(directory: Path, call_id: str) -> None:
    (directory / f"{call_id}.md").write_text("not a valid transcript at all\n", encoding="utf-8")


def _make_candidate(
    call_id: str, account: str, primary_turn_index: int = 0, signal_type: str = "bug",
    snippet: str = "The scheduled export button returns a blank CSV file every time.",
    suppressed: bool = False,
) -> Candidate:
    return Candidate(
        call_id=call_id, account=account, primary_turn_index=primary_turn_index,
        turn_span=(primary_turn_index, primary_turn_index), snippet=snippet,
        signal_type=signal_type, draft_title=snippet.rstrip("."), raw_score=3.0,
        suppressed=suppressed,
    )


class OrchestratorTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.transcripts_dir = root / "transcripts"
        self.transcripts_dir.mkdir()
        self.existing_issues_path = root / "existing_issues.json"
        self.existing_issues_path.write_text("[]", encoding="utf-8")

        self.cfg = Config(
            transcripts_dir=self.transcripts_dir,
            existing_issues_path=self.existing_issues_path,
            dev_labels_path=root / "dev_labels.json",
            state_path=root / "state" / "pipeline_state.json",
            review_queue_path=root / "state" / "review_queue.md",
            review_decisions_path=root / "state" / "review_decisions.json",
            log_path=root / "state" / "events.jsonl",
            similarity_threshold=0.20,
            judge="heuristic",
            openai_model="gpt-4o-mini",
        )
        self.fake_jira = _FakeJira()
        self.fake_slack = _FakeSlack()

    def _run_review_with(self, candidates_by_call: dict[str, list[Candidate]]) -> orchestrator.ReviewRunSummary:
        fake_judge = _FakeJudge(candidates_by_call)
        with patch.object(orchestrator, "_make_judge", return_value=fake_judge):
            return orchestrator.run_review(self.cfg)

    def _run_apply(self) -> orchestrator.ApplyRunSummary:
        with patch.object(orchestrator, "jira_stub", self.fake_jira), \
             patch.object(orchestrator, "slack_stub", self.fake_slack):
            return orchestrator.run_apply(self.cfg)

    def _approve(self, key: str) -> None:
        decisions = load_review_decisions(self.cfg.review_decisions_path)
        decisions[key]["decision"] = "approved"
        self.cfg.review_decisions_path.write_text(__import__("json").dumps(decisions), encoding="utf-8")

    def _reject(self, key: str) -> None:
        decisions = load_review_decisions(self.cfg.review_decisions_path)
        decisions[key]["decision"] = "rejected"
        self.cfg.review_decisions_path.write_text(__import__("json").dumps(decisions), encoding="utf-8")


class TestRunReview(OrchestratorTestBase):
    def test_file_new_candidate_gets_queued(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        summary = self._run_review_with({"call-001": [candidate]})

        self.assertEqual(summary.queued_for_review, 1)
        store = StateStore(self.cfg.state_path)
        entry = store.get(candidate_key(candidate))
        self.assertIsNotNone(entry)
        assert entry is not None
        self.assertEqual(entry["status"], "queued")
        self.assertEqual(entry["action"], "file-new")

    def test_suppressed_candidate_never_queued(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp", suppressed=True)
        summary = self._run_review_with({"call-001": [candidate]})

        self.assertEqual(summary.queued_for_review, 0)
        self.assertEqual(summary.candidates_suppressed, 1)

    def test_review_queue_markdown_and_decisions_json_written(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})

        self.assertTrue(self.cfg.review_queue_path.exists())
        self.assertIn("call-001", self.cfg.review_queue_path.read_text(encoding="utf-8"))
        decisions = load_review_decisions(self.cfg.review_decisions_path)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(next(iter(decisions.values()))["decision"], "pending")

    def test_second_call_corroborates_against_first(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        _write_transcript(self.transcripts_dir, "call-002")
        same_snippet = "The scheduled export button returns a blank CSV file every time, reproducibly."
        cand1 = _make_candidate("call-001", "Acme Corp", snippet=same_snippet)
        cand2 = _make_candidate("call-002", "Globex Inc", snippet=same_snippet)
        self._run_review_with({"call-001": [cand1], "call-002": [cand2]})

        store = StateStore(self.cfg.state_path)
        entry2 = store.get(candidate_key(cand2))
        assert entry2 is not None
        self.assertEqual(entry2["action"], "corroborate")
        self.assertTrue(str(entry2["matched_key"]).startswith("PENDING:"))

    def test_same_call_duplicate_targets_collapse(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        same_snippet = "The scheduled export button returns a blank CSV file every time, reproducibly."
        cand1 = _make_candidate("call-001", "Acme Corp", primary_turn_index=0, snippet=same_snippet)
        cand2 = _make_candidate("call-001", "Acme Corp", primary_turn_index=2, snippet=same_snippet)
        summary = self._run_review_with({"call-001": [cand1, cand2]})

        self.assertEqual(summary.queued_for_review, 1)
        self.assertEqual(summary.collapsed_duplicates, 1)
        store = StateStore(self.cfg.state_path)
        entry2 = store.get(candidate_key(cand2))
        assert entry2 is not None
        self.assertEqual(entry2["status"], "collapsed_duplicate")

    def test_rerunning_review_does_not_duplicate_queue_entries(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})
        summary2 = self._run_review_with({"call-001": [candidate]})

        self.assertEqual(summary2.queued_for_review, 0)  # already queued, not re-added
        decisions = load_review_decisions(self.cfg.review_decisions_path)
        self.assertEqual(len(decisions), 1)

    def test_partial_failure_bad_transcript_does_not_abort_batch(self) -> None:
        _write_broken_transcript(self.transcripts_dir, "call-001")
        _write_transcript(self.transcripts_dir, "call-002")
        candidate = _make_candidate("call-002", "Acme Corp")
        summary = self._run_review_with({"call-002": [candidate]})

        self.assertEqual(summary.calls_failed, 1)
        self.assertEqual(summary.calls_processed, 1)
        self.assertEqual(summary.queued_for_review, 1)


class TestRunApply(OrchestratorTestBase):
    def test_approved_file_new_creates_ticket_and_notifies(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})
        key = candidate_key(candidate)
        self._approve(key)

        summary = self._run_apply()

        self.assertEqual(summary.filed, 1)
        self.assertEqual(len(self.fake_jira.calls), 1)
        self.assertEqual(len(self.fake_slack.calls), 1)
        store = StateStore(self.cfg.state_path)
        entry = store.get(key)
        assert entry is not None
        self.assertEqual(entry["status"], "filed")
        self.assertTrue(str(entry["issue_key"]).startswith("PROJ-"))

    def test_rejected_item_is_not_filed(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})
        key = candidate_key(candidate)
        self._reject(key)

        summary = self._run_apply()

        self.assertEqual(summary.rejected, 1)
        self.assertEqual(len(self.fake_jira.calls), 0)
        self.assertEqual(len(self.fake_slack.calls), 0)

    def test_pending_item_left_untouched(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})
        # No approve/reject call -- still "pending".

        summary = self._run_apply()

        self.assertEqual(summary.filed, 0)
        self.assertEqual(summary.rejected, 0)
        store = StateStore(self.cfg.state_path)
        entry = store.get(candidate_key(candidate))
        assert entry is not None
        self.assertEqual(entry["status"], "queued")

    def test_second_apply_does_not_refile(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        candidate = _make_candidate("call-001", "Acme Corp")
        self._run_review_with({"call-001": [candidate]})
        self._approve(candidate_key(candidate))
        self._run_apply()

        summary2 = self._run_apply()

        self.assertEqual(summary2.filed, 0)
        self.assertEqual(len(self.fake_jira.calls), 1)  # still just the one from pass 1

    def test_corroborate_resolves_pending_key_from_same_apply_batch(self) -> None:
        _write_transcript(self.transcripts_dir, "call-001")
        _write_transcript(self.transcripts_dir, "call-002")
        same_snippet = "The scheduled export button returns a blank CSV file every time, reproducibly."
        cand1 = _make_candidate("call-001", "Acme Corp", snippet=same_snippet)
        cand2 = _make_candidate("call-002", "Globex Inc", snippet=same_snippet)
        self._run_review_with({"call-001": [cand1], "call-002": [cand2]})
        self._approve(candidate_key(cand1))
        self._approve(candidate_key(cand2))

        summary = self._run_apply()

        self.assertEqual(summary.filed, 1)
        self.assertEqual(summary.corroborated, 1)
        real_key = self.fake_jira.calls[0].get("source", {}).get("call_id")  # sanity: a payload was built
        self.assertIsNotNone(real_key)
        slack_texts = [c["text"] for c in self.fake_slack.calls]
        self.assertTrue(any("PROJ-9001" in t for t in slack_texts))
        self.assertFalse(any("PENDING:" in t for t in slack_texts))


if __name__ == "__main__":
    unittest.main()
