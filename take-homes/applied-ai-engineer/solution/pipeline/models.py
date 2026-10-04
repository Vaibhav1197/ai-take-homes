"""Shared data structures for the pipeline.

Kept dependency-free (stdlib only) and deliberately dumb: no behavior lives on
these types beyond trivial derived properties. That keeps every stage
(ingest, judge, dedup, payloads) testable in isolation against plain data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Speaker(str, Enum):
    EXTERNAL = "EXTERNAL"
    INTERNAL = "INTERNAL"


@dataclass(frozen=True)
class Turn:
    """One spoken line in a transcript. `text` is verbatim from the source file."""

    index: int
    speaker: Speaker
    name: str
    text: str


@dataclass(frozen=True)
class Transcript:
    call_id: str
    title: str
    account: Optional[str]  # None for internal-only calls (no customer present)
    date: str
    call_type: str
    participants_raw: str
    turns: tuple[Turn, ...]
    path: str

    @property
    def has_external_participant(self) -> bool:
        return any(t.speaker is Speaker.EXTERNAL for t in self.turns)

    def external_turns(self) -> list[Turn]:
        return [t for t in self.turns if t.speaker is Speaker.EXTERNAL]


class Action(str, Enum):
    FILE_NEW = "file-new"
    FILE_NEW_LOW = "file-new-low"
    CORROBORATE = "corroborate"
    NONE = "none"


class IssueType(str, Enum):
    BUG = "Bug"
    FEATURE = "Feature"


@dataclass(frozen=True)
class ExistingIssue:
    key: str
    type: str
    status: str
    summary: str
    description: str
    created: str
    reported_by_accounts: tuple[str, ...] = ()
    shipped_in: Optional[str] = None

    @property
    def is_shipped(self) -> bool:
        return self.status.lower() == "shipped"

    @property
    def corpus_text(self) -> str:
        return f"{self.summary}\n{self.description}"


@dataclass
class Candidate:
    """A transcript span the judge believes is worth a human's attention."""

    call_id: str
    account: Optional[str]
    primary_turn_index: int
    turn_span: tuple[int, int]
    snippet: str
    signal_type: str  # "bug" | "feature"
    keyword_hits: list[str] = field(default_factory=list)
    raw_score: float = 0.0
    flags: list[str] = field(default_factory=list)
    provisional_priority: str = "P3"
    draft_title: str = ""
    suppressed: bool = False
    suppression_reason: str = ""
    needs_human_priority_call: bool = False


@dataclass
class Decision:
    """Final judged + de-duplicated outcome for a Candidate."""

    candidate: Candidate
    action: Action
    issue_type: Optional[IssueType]
    title: str
    priority: str
    rationale: str
    confidence: float
    matched_issue_key: Optional[str] = None
    idempotency_key: str = ""
    needs_human_priority_call: bool = False

    @property
    def call_id(self) -> str:
        return self.candidate.call_id

    def to_log_dict(self) -> dict[str, Any]:
        return {
            "call_id": self.call_id,
            "turn_span": list(self.candidate.turn_span),
            "action": self.action.value,
            "issue_type": self.issue_type.value if self.issue_type else None,
            "priority": self.priority,
            "confidence": round(self.confidence, 3),
            "matched_issue_key": self.matched_issue_key,
            "rationale": self.rationale,
            "flags": list(self.candidate.flags),
            "idempotency_key": self.idempotency_key,
        }
