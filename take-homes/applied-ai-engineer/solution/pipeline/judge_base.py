"""The pluggable "which intelligence answers this question" boundary.

The orchestrator only ever talks to this interface. Swapping the shipped
deterministic engine (HeuristicJudge) for a real model call (LLMJudge) is a
one-line change in config.py -- no other stage needs to know which is active.
See WRITEUP.md "AI placement" for why the default judge is heuristic, not a
live LLM call.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import Candidate, Transcript


@runtime_checkable
class IssueJudge(Protocol):
    """Turns one transcript into zero or more Candidates.

    Implementations decide "is this genuine, and is it a bug or a feature
    request" -- nothing about deduplication against existing issues, which is
    a separate, deliberately judge-independent stage (see dedup.py).
    """

    def find_candidates(self, transcript: Transcript) -> list[Candidate]:
        """Return every transcript span worth a human's attention, in call
        order. Include suppressed spans too (candidate.suppressed=True) --
        they're kept for observability/audit but the orchestrator must never
        let a suppressed candidate reach Jira/Slack."""
        ...
