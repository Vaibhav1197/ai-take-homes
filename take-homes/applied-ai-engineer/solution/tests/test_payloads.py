"""Unit tests for payloads.py -- Jira ticket + Slack notification payload shaping."""
from __future__ import annotations

import unittest

from solution.pipeline.models import Action, Candidate, Decision, IssueType, Speaker, Transcript, Turn
from solution.pipeline.payloads import build_jira_payload, build_slack_payload


def _make_transcript() -> Transcript:
    turns = (
        Turn(index=0, speaker=Speaker.EXTERNAL, name="Renee", text="Exports drop rows randomly."),
        Turn(index=1, speaker=Speaker.INTERNAL, name="Tom\u00e1s Vela", text="That sounds like a real bug."),
    )
    return Transcript(
        call_id="call-003",
        title="Atlas Financial \u00d7 BetterBark",
        account="Atlas Financial",
        date="2026-06-17",
        call_type="Onboarding",
        participants_raw="[EXTERNAL] Renee Park \u00b7 [INTERNAL] Tom\u00e1s Vela, Implementation",
        turns=turns,
        path="transcripts/call-003.md",
    )


def _make_candidate(**overrides) -> Candidate:
    defaults = dict(
        call_id="call-003",
        account="Atlas Financial",
        primary_turn_index=0,
        turn_span=(0, 1),
        snippet="Exports drop rows randomly.",
        signal_type="bug",
        draft_title="Exports drop rows randomly",
    )
    defaults.update(overrides)
    return Candidate(**defaults)


def _make_decision(action: Action, issue_type=IssueType.BUG, matched_issue_key=None, priority="P2", **cand_overrides) -> Decision:
    candidate = _make_candidate(**cand_overrides)
    return Decision(
        candidate=candidate,
        action=action,
        issue_type=issue_type,
        title=candidate.draft_title,
        priority=priority,
        rationale="no existing Bug issue matched above threshold",
        confidence=0.9,
        matched_issue_key=matched_issue_key,
        idempotency_key="call-003#0#bug",
    )


class TestBuildJiraPayload(unittest.TestCase):
    def test_file_new_has_all_required_fields(self) -> None:
        decision = _make_decision(Action.FILE_NEW)
        transcript = _make_transcript()
        payload = build_jira_payload(decision, transcript)
        for field in ("project", "type", "summary", "description"):
            self.assertIn(field, payload)
            self.assertTrue(payload[field], f"{field!r} must be non-empty")

    def test_project_is_proj(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW), _make_transcript())
        self.assertEqual(payload["project"], "PROJ")

    def test_type_matches_decision_issue_type(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW, issue_type=IssueType.FEATURE), _make_transcript())
        self.assertEqual(payload["type"], "Feature")

    def test_priority_passed_through(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW, priority="P1"), _make_transcript())
        self.assertEqual(payload["priority"], "P1")

    def test_description_includes_snippet_and_transcript_reference(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW), _make_transcript())
        self.assertIn("Exports drop rows randomly.", payload["description"])
        self.assertIn("transcripts/call-003.md", payload["description"])

    def test_source_includes_call_id_and_snippet(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW), _make_transcript())
        self.assertEqual(payload["source"]["call_id"], "call-003")
        self.assertEqual(payload["source"]["snippet"], "Exports drop rows randomly.")

    def test_file_new_low_adds_confidence_note(self) -> None:
        payload = build_jira_payload(_make_decision(Action.FILE_NEW_LOW), _make_transcript())
        self.assertIn("low-confidence", payload["description"])

    def test_raises_for_corroborate_action(self) -> None:
        decision = _make_decision(Action.CORROBORATE, matched_issue_key="PROJ-087")
        with self.assertRaises(ValueError):
            build_jira_payload(decision, _make_transcript())

    def test_raises_for_none_action(self) -> None:
        decision = _make_decision(Action.NONE, issue_type=None)
        with self.assertRaises(ValueError):
            build_jira_payload(decision, _make_transcript())

    def test_raises_when_issue_type_missing(self) -> None:
        decision = _make_decision(Action.FILE_NEW, issue_type=None)
        with self.assertRaises(ValueError):
            build_jira_payload(decision, _make_transcript())


class TestBuildSlackPayload(unittest.TestCase):
    def test_required_fields_present(self) -> None:
        payload = build_slack_payload(_make_decision(Action.FILE_NEW), _make_transcript(), issue_key="PROJ-1042")
        self.assertIn("channel", payload)
        self.assertIn("text", payload)
        self.assertTrue(payload["channel"])
        self.assertTrue(payload["text"])

    def test_channel_derived_from_internal_owner_ascii_slug(self) -> None:
        payload = build_slack_payload(_make_decision(Action.FILE_NEW), _make_transcript(), issue_key="PROJ-1042")
        self.assertEqual(payload["channel"], "@tomas.vela")

    def test_file_new_text_includes_issue_key_and_priority(self) -> None:
        payload = build_slack_payload(
            _make_decision(Action.FILE_NEW, priority="P1"), _make_transcript(), issue_key="PROJ-1042"
        )
        self.assertIn("PROJ-1042", payload["text"])
        self.assertIn("P1", payload["text"])
        self.assertIn(":rotating_light:", payload["text"])  # P1 is urgent

    def test_low_priority_uses_memo_emoji(self) -> None:
        payload = build_slack_payload(
            _make_decision(Action.FILE_NEW, priority="P4"), _make_transcript(), issue_key="PROJ-1042"
        )
        self.assertIn(":memo:", payload["text"])

    def test_file_new_low_flags_low_confidence(self) -> None:
        payload = build_slack_payload(
            _make_decision(Action.FILE_NEW_LOW), _make_transcript(), issue_key="PROJ-1042"
        )
        self.assertIn("please verify", payload["text"])

    def test_corroborate_text_references_matched_key_and_no_new_ticket(self) -> None:
        decision = _make_decision(Action.CORROBORATE, matched_issue_key="PROJ-087")
        payload = build_slack_payload(decision, _make_transcript(), issue_key="PROJ-087")
        self.assertIn("PROJ-087", payload["text"])
        self.assertIn("No new ticket filed", payload["text"])

    def test_raises_for_none_action(self) -> None:
        decision = _make_decision(Action.NONE, issue_type=None)
        with self.assertRaises(ValueError):
            build_slack_payload(decision, _make_transcript(), issue_key="")

    def test_source_metadata_present(self) -> None:
        payload = build_slack_payload(_make_decision(Action.FILE_NEW), _make_transcript(), issue_key="PROJ-1042")
        self.assertEqual(payload["source"]["call_id"], "call-003")
        self.assertEqual(payload["source"]["issue_key"], "PROJ-1042")


if __name__ == "__main__":
    unittest.main()
