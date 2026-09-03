"""Optional `IssueJudge` implementation that asks a real model instead of
running the rule engine. See WRITEUP.md "AI placement" for why this is not
the default.

Only imported when `PIPELINE_JUDGE=llm` (see `orchestrator._make_judge`),
and `config.load_config()` already refuses to select "llm" without
`OPENAI_API_KEY` set. Uses only the standard library (`urllib`) to stay
consistent with the rest of this solution's zero-third-party-dependency
stance -- no `openai` package required.

Design choices that keep this judge honest and comparable to HeuristicJudge:
  * The prompt requires turn-index citations, not paraphrase: the model
    must point at which turns it's reacting to, and `_build_candidate`
    (below) re-quotes those turns verbatim from the transcript object --
    the model's own restatement of what was said is never trusted as the
    snippet that reaches Jira/Slack. The raw transcript stays the source
    of truth regardless of which judge is active.
  * Priority is *not* asked of the model. It's derived the same
    deterministic way as the heuristic judge, via the shared
    `estimate_priority()` -- keeping "never inflate priority from a
    customer's own dramatic framing" a judge-independent guarantee that
    doesn't have to be re-prompted-for and separately verified per judge.
  * Network I/O goes through a small `transport` seam (defaults to a real
    urllib call) so unit tests can inject a fake and assert on prompt
    construction / response parsing without ever making a live call --
    same "no network in unit tests" discipline as the rest of this suite.
  * A malformed or unreachable model response raises `LLMJudgeError`
    rather than crashing the run: `orchestrator.run_review`'s existing
    per-transcript `except Exception` boundary catches it, logs
    `call_failed` with the call_id, and moves on -- one bad model call
    can't corrupt the rest of the batch, the same partial-failure
    contract a bad transcript parse already gets.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable, Optional

from .heuristic_judge import _build_snippet, estimate_priority
from .models import Candidate, Speaker, Transcript, Turn

_API_URL = "https://api.openai.com/v1/chat/completions"
_REQUEST_TIMEOUT_SECONDS = 60

_SYSTEM_PROMPT = """You are helping triage customer-call transcripts for a product team.

Read the transcript and identify spans where the EXTERNAL speaker (the \
customer) raises a genuine, actionable software bug or feature request -- \
not small talk, not internal-only chatter, not a vague complaint with no \
product substance.

Respond with a single JSON object: {"issues": [...]}. Each element of \
"issues" must have exactly these fields:
  - "start_turn": integer, first turn index (inclusive) of the span raising this one issue
  - "end_turn": integer, last turn index (inclusive) of that span
  - "signal_type": "bug" or "feature"
  - "draft_title": a short (<=100 char) imperative title you write, e.g. "Fix crash exporting PDF with no sessions"
  - "rationale": one sentence on why this is genuine and actionable, not noise
  - "confidence": float from 0.0 to 1.0

Rules:
  - Only use turn indices that actually appear in the transcript below.
  - If the customer explicitly retracts a report, says it's already fixed, \
or is only relaying hearsay ("I heard someone else had an issue"), leave it out.
  - Two turns far apart discussing the same issue are ONE object spanning both, not two.
  - "issues" is an empty array if nothing genuine and actionable was raised.
  - Output ONLY the JSON object, no prose before or after."""


def _render_transcript(transcript: Transcript) -> str:
    return "\n".join(f"[{t.index}] [{t.speaker.value}] {t.name}: {t.text}" for t in transcript.turns)


Transport = Callable[[str, dict], dict]


def _default_transport(api_key: str, payload: dict) -> dict:
    """Real network call, stdlib-only. Never exercised by unit tests --
    `LLMJudge(transport=...)` swaps this out for a fake."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        _API_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


class LLMJudgeError(RuntimeError):
    """The model call failed, or the response wasn't usable (bad JSON,
    missing fields, out-of-range turn indices). Caught by
    `orchestrator.run_review`'s per-call boundary -- see module docstring."""


class LLMJudge:
    """`IssueJudge` backed by a real chat-completions call. Same interface
    and same `Candidate` shape as `HeuristicJudge` -- `orchestrator.py`
    cannot tell the two apart."""

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        transport: Optional[Transport] = None,
    ) -> None:
        self.model = model
        self.api_key = api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")
        self._transport = transport or _default_transport

    def find_candidates(self, transcript: Transcript) -> list[Candidate]:
        if not transcript.has_external_participant:
            return []

        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _render_transcript(transcript)},
            ],
        }
        items = self._request_issues(transcript.call_id, payload)

        turns_by_index = {t.index: t for t in transcript.turns}
        candidates: list[Candidate] = []
        for item in items:
            candidate = self._build_candidate(transcript, turns_by_index, item)
            if candidate is not None:
                candidates.append(candidate)
        return candidates

    def _request_issues(self, call_id: str, payload: dict) -> list[dict]:
        try:
            response = self._transport(self.api_key, payload)
            raw_content = response["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)
            issues = parsed["issues"]
        except (
            urllib.error.URLError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as exc:
            raise LLMJudgeError(f"LLM judge call failed for {call_id}: {exc}") from exc
        if not isinstance(issues, list):
            raise LLMJudgeError(f"LLM judge returned non-list 'issues' for {call_id}")
        return issues

    def _build_candidate(
        self, transcript: Transcript, turns_by_index: dict[int, Turn], item: dict
    ) -> Optional[Candidate]:
        """Never trust the model past this point without re-deriving from
        real turns -- an out-of-range span, or a span with no EXTERNAL
        turn in it, is dropped rather than passed through."""
        try:
            lo, hi = int(item["start_turn"]), int(item["end_turn"])
            signal_type = str(item["signal_type"])
            confidence = float(item.get("confidence", 0.5))
        except (KeyError, TypeError, ValueError):
            return None
        if lo > hi or lo not in turns_by_index or hi not in turns_by_index:
            return None

        window = [turns_by_index[i] for i in range(lo, hi + 1) if i in turns_by_index]
        ext_turns = [t for t in window if t.speaker is Speaker.EXTERNAL]
        if not ext_turns:
            return None  # a genuine issue must include the customer's own words

        full_text_l = " ".join(t.text for t in window).lower()
        # No flags: the LLM path has no equivalent of the heuristic engine's
        # objective corroborating-signal flags, so `estimate_priority` (and
        # the FILE_NEW_LOW downgrade in orchestrator._build_decision, which
        # keys off raw_score/flags) fall back to the confidence signal alone.
        priority, needs_human_priority_call = estimate_priority(full_text_l, flags=[])

        return Candidate(
            call_id=transcript.call_id,
            account=transcript.account,
            primary_turn_index=ext_turns[0].index,
            turn_span=(lo, hi),
            snippet=_build_snippet(ext_turns),
            signal_type=signal_type if signal_type in ("bug", "feature") else "bug",
            keyword_hits=[],
            raw_score=max(0.0, min(1.0, confidence)) * 4.0,
            flags=[],
            provisional_priority=priority,
            draft_title=str(item.get("draft_title", "") or "")[:200],
            suppressed=False,
            suppression_reason="",
            needs_human_priority_call=needs_human_priority_call,
        )
