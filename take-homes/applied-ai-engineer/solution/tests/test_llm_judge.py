"""Unit tests for llm_judge.py -- the optional model-backed IssueJudge.

No network calls: every test injects a fake `transport` callable so we can
assert on prompt construction and response parsing without ever reaching
`urllib`. Mirrors the `HeuristicJudge` test conventions in
test_heuristic_judge.py (`_transcript` builder) so the two judges' tests
read the same way.
"""
from __future__ import annotations

import json
import unittest
import urllib.error
from unittest.mock import patch

from solution.pipeline.llm_judge import LLMJudge, LLMJudgeError
from solution.pipeline.models import Speaker, Transcript, Turn

EXT, INT = Speaker.EXTERNAL, Speaker.INTERNAL


def _transcript(turns_spec: list[tuple[Speaker, str, str]], call_id: str = "call-001") -> Transcript:
    turns = tuple(
        Turn(index=i, speaker=speaker, name=name, text=text)
        for i, (speaker, name, text) in enumerate(turns_spec)
    )
    return Transcript(
        call_id=call_id, title="Test Call", account="Acme Corp", date="2026-01-01",
        call_type="Support", participants_raw="[EXTERNAL] Jamie \u00b7 [INTERNAL] Riley",
        turns=turns, path=f"transcripts/{call_id}.md",
    )


def _chat_response(content: object) -> dict:
    """Shape of a real OpenAI chat-completions response, enough of it for
    `_request_issues` to extract `choices[0].message.content`."""
    body = content if isinstance(content, str) else json.dumps(content)
    return {"choices": [{"message": {"content": body}}]}


class TestFindCandidatesNoExternalParticipant(unittest.TestCase):
    def test_internal_only_call_never_calls_transport(self) -> None:
        transport = unittest.mock.Mock()
        judge = LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=transport)
        transcript = _transcript([(INT, "Riley", "Sync on the roadmap.")])
        self.assertEqual(judge.find_candidates(transcript), [])
        transport.assert_not_called()


class TestFindCandidatesHappyPath(unittest.TestCase):
    def test_single_bug_span_becomes_one_candidate(self) -> None:
        transcript = _transcript(
            [
                (INT, "Riley", "What's going on?"),
                (EXT, "Jamie", "The export button crashes the app every time I click it."),
                (EXT, "Jamie", "It happens on every session report, no exceptions."),
            ],
            call_id="call-042",
        )
        model_reply = {
            "issues": [
                {
                    "start_turn": 1,
                    "end_turn": 2,
                    "signal_type": "bug",
                    "draft_title": "Fix crash exporting session report",
                    "rationale": "Customer reports a reproducible crash on every export.",
                    "confidence": 0.9,
                }
            ]
        }
        transport = unittest.mock.Mock(return_value=_chat_response(model_reply))
        judge = LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=transport)

        candidates = judge.find_candidates(transcript)

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.call_id, "call-042")
        self.assertEqual(candidate.account, "Acme Corp")
        self.assertEqual(candidate.turn_span, (1, 2))
        self.assertEqual(candidate.primary_turn_index, 1)
        self.assertEqual(candidate.signal_type, "bug")
        self.assertEqual(candidate.draft_title, "Fix crash exporting session report")
        # Snippet is re-quoted verbatim from the real turns, not the model's
        # own rationale/title text.
        self.assertIn("crashes the app every time I click it", candidate.snippet)
        self.assertIn("every session report", candidate.snippet)
        self.assertNotIn("Fix crash exporting", candidate.snippet)

    def test_no_genuine_issues_returns_empty_list(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "Just checking in, everything's fine.")])
        transport = unittest.mock.Mock(return_value=_chat_response({"issues": []}))
        judge = LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=transport)
        self.assertEqual(judge.find_candidates(transcript), [])

    def test_confidence_rescaled_into_raw_score_on_a_0_to_4_scale(self) -> None:
        """`_confidence_for`/the FILE_NEW_LOW downgrade in orchestrator.py
        read `candidate.raw_score` on the heuristic judge's implicit 0-4ish
        scale, not a 0-1 probability -- confidence must be rescaled so both
        judges' outputs are interpreted consistently downstream."""
        transcript = _transcript([(EXT, "Jamie", "Small thing: the label is misspelled.")])
        model_reply = {
            "issues": [
                {"start_turn": 0, "end_turn": 0, "signal_type": "bug", "confidence": 0.25}
            ]
        }
        transport = unittest.mock.Mock(return_value=_chat_response(model_reply))
        judge = LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=transport)

        candidate = judge.find_candidates(transcript)[0]
        self.assertAlmostEqual(candidate.raw_score, 1.0)
        self.assertEqual(candidate.flags, [])


class TestPromptConstruction(unittest.TestCase):
    def test_payload_includes_model_zero_temperature_and_rendered_turns(self) -> None:
        transcript = _transcript(
            [(EXT, "Jamie", "The dashboard export is broken.")], call_id="call-007"
        )
        captured: dict = {}

        def fake_transport(api_key: str, payload: dict) -> dict:
            captured["api_key"] = api_key
            captured["payload"] = payload
            return _chat_response({"issues": []})

        judge = LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=fake_transport)
        judge.find_candidates(transcript)

        self.assertEqual(captured["api_key"], "sk-test")
        self.assertEqual(captured["payload"]["model"], "gpt-4o-mini")
        self.assertEqual(captured["payload"]["temperature"], 0)
        user_message = captured["payload"]["messages"][1]["content"]
        self.assertIn("[0] [EXTERNAL] Jamie: The dashboard export is broken.", user_message)

    def test_api_key_falls_back_to_environment(self) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-from-env"}, clear=True):
            judge = LLMJudge(model="gpt-4o-mini")
        self.assertEqual(judge.api_key, "sk-from-env")


class TestRobustnessAgainstBadModelOutput(unittest.TestCase):
    def _judge(self, transport) -> LLMJudge:
        return LLMJudge(model="gpt-4o-mini", api_key="sk-test", transport=transport)

    def test_out_of_range_turn_span_is_dropped_not_raised(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        model_reply = {"issues": [{"start_turn": 0, "end_turn": 99, "signal_type": "bug"}]}
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response(model_reply)))
        self.assertEqual(judge.find_candidates(transcript), [])

    def test_span_with_no_external_turn_is_dropped(self) -> None:
        transcript = _transcript(
            [(INT, "Riley", "Let's discuss internally."), (EXT, "Jamie", "Sounds good.")]
        )
        model_reply = {"issues": [{"start_turn": 0, "end_turn": 0, "signal_type": "bug"}]}
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response(model_reply)))
        self.assertEqual(judge.find_candidates(transcript), [])

    def test_malformed_item_missing_required_field_is_dropped(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        model_reply = {"issues": [{"start_turn": 0, "signal_type": "bug"}]}  # no end_turn
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response(model_reply)))
        self.assertEqual(judge.find_candidates(transcript), [])

    def test_unparseable_json_content_raises_llm_judge_error(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response("not valid json {{")))
        with self.assertRaises(LLMJudgeError):
            judge.find_candidates(transcript)

    def test_missing_issues_key_raises_llm_judge_error(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response({"oops": []})))
        with self.assertRaises(LLMJudgeError):
            judge.find_candidates(transcript)

    def test_non_list_issues_value_raises_llm_judge_error(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        judge = self._judge(unittest.mock.Mock(return_value=_chat_response({"issues": "bug"})))
        with self.assertRaises(LLMJudgeError):
            judge.find_candidates(transcript)

    def test_malformed_response_shape_raises_llm_judge_error(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])
        judge = self._judge(unittest.mock.Mock(return_value={"no": "choices"}))
        with self.assertRaises(LLMJudgeError):
            judge.find_candidates(transcript)

    def test_transport_network_error_raises_llm_judge_error(self) -> None:
        transcript = _transcript([(EXT, "Jamie", "The export is broken.")])

        def raising_transport(api_key: str, payload: dict) -> dict:
            raise urllib.error.URLError("connection refused")

        judge = self._judge(raising_transport)
        with self.assertRaises(LLMJudgeError):
            judge.find_candidates(transcript)


if __name__ == "__main__":
    unittest.main()
