"""Stage 2: de-duplication against tracked issues.

Takes the Candidates a judge (heuristic or LLM) already decided are genuine
and not suppressed, and answers one question only: is this a NEW issue, or
does it match something already tracked? Nothing here re-litigates whether a
candidate is real -- that judgment already happened upstream (see
judge_base.py). Keeping the two concerns separate means either can be
swapped, tested, or tuned independently.

Matching is TF-IDF + cosine similarity over each existing issue's
`summary + description` versus the candidate's `draft_title + snippet`,
restricted to matching issue type (a Bug candidate is only ever compared
against tracked Bugs, a Feature against tracked Features). This is plain
stdlib string/math work -- no embeddings, no network call, fully
deterministic and unit-testable. See TfidfIndex in text_utils.py for why a
from-scratch implementation is appropriate at this corpus size (dozens of
issues, not millions).

Growing-pool design
--------------------
`existing_issues.json` is a snapshot from before this batch started. Two
things it does NOT know about:

1. Issues filed earlier IN THIS SAME RUN. dev_labels.json's call-006/call-012
   pair is the concrete case: neither call's issue is in existing_issues.json
   at all -- call-006 is processed first and must become a new "search
   staleness" ticket, and call-012 (a later call, same run) reports the
   identical symptom and must corroborate against THAT ticket rather than
   opening a second one. The only way to catch this is to fold every
   FILE_NEW decision back into the matching pool immediately
   (`register_new`) so later candidates in the same pass can match against
   it, using a placeholder key (`PENDING:n`) until a human approves it and a
   real Jira key exists.
2. Issues filed in a PREVIOUS run. That is state_store.py's job: it persists
   the ledger of previously-filed tickets across process invocations and
   seeds this pool with them before a new batch starts, which is what makes
   re-running the pipeline over the same transcripts idempotent (see
   orchestrator.py).

Shipped issues are matched too (existing_issues.json intentionally includes
recently-shipped work): a match against a shipped issue resolves to
Action.NONE ("already shipped"), not a ticket of any kind.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import Action, Candidate, ExistingIssue, Transcript
from .text_utils import TfidfIndex

# Tuned empirically against dev_labels.json (see solution/eval). Candidate
# snippets are short, casual customer speech; existing-issue text is short,
# clean PM prose -- cosine similarity between the two styles runs lower than
# same-style document comparisons typically would, so the threshold is
# deliberately permissive rather than the ~0.5+ common for longer documents.
# Empirically: every dev_labels corroborate/shipped match scores >= 0.20;
# near-miss "distinct issue that merely shares a couple of words" pairs
# (e.g. call-010's Azure AD redirect loop vs the unrelated Okta early-expiry
# ticket PROJ-064, or call-006's rename-triggered staleness vs the unrelated
# new-member indexing delay PROJ-131) score 0.13-0.16. The threshold sits
# between those two clusters.
DEFAULT_SIMILARITY_THRESHOLD = 0.20

PENDING_KEY_PREFIX = "PENDING:"

_ISSUE_TYPES = ("Bug", "Feature")


@dataclass(frozen=True)
class MatchOutcome:
    """What dedup thinks should happen to one Candidate."""

    action: Action  # Action.FILE_NEW, Action.CORROBORATE, or Action.NONE (shipped)
    matched_key: Optional[str]
    similarity: float
    rationale: str


def load_existing_issues(path: Path) -> list[ExistingIssue]:
    """Parse `data/existing_issues.json` into ExistingIssue records."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    issues: list[ExistingIssue] = []
    for entry in raw:
        issues.append(
            ExistingIssue(
                key=entry["key"],
                type=entry["type"],
                status=entry["status"],
                summary=entry["summary"],
                description=entry["description"],
                created=entry["created"],
                reported_by_accounts=tuple(entry.get("reported_by_accounts", ())),
                shipped_in=entry.get("shipped_in"),
            )
        )
    return issues


def _issue_type_for(candidate: Candidate) -> str:
    return "Bug" if candidate.signal_type == "bug" else "Feature"


def _query_text(candidate: Candidate, transcript: Optional[Transcript] = None) -> str:
    """Text to match against tracked-issue summaries/descriptions.

    Prefers BOTH speakers' turns across the full span when a transcript is
    available, not just `candidate.snippet` (external-only, used for the
    Jira/Slack evidence quote). The internal speaker frequently paraphrases
    the customer's colloquial report back in cleaner, more technical
    language ("so it's a genuine redirect loop"), which tends to share far
    more vocabulary with existing_issues.json's clean PM-style prose than
    the raw customer phrasing alone -- this materially improves match
    recall. Falls back to the external-only snippet if no transcript is
    given (keeps the function usable in isolation, e.g. in unit tests).
    """
    if transcript is not None:
        lo, hi = candidate.turn_span
        span_text = "\n".join(t.text for t in transcript.turns[lo : hi + 1])
        return f"{candidate.draft_title}\n{span_text}"
    return f"{candidate.draft_title}\n{candidate.snippet}"


class Deduplicator:
    """Matches Candidates against a pool of known issues that grows as new
    ones are filed during a run. See module docstring for why the pool
    grows and how cross-run idempotency is layered on top by state_store.py.
    """

    def __init__(
        self,
        existing_issues: list[ExistingIssue],
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ):
        self._threshold = similarity_threshold
        self._issues: list[ExistingIssue] = list(existing_issues)
        self._pending_count = 0
        self._issues_by_type: dict[str, list[ExistingIssue]] = {}
        self._index_by_type: dict[str, TfidfIndex] = {}
        self._rebuild()

    def _rebuild(self) -> None:
        self._issues_by_type = {t: [] for t in _ISSUE_TYPES}
        for issue in self._issues:
            self._issues_by_type.setdefault(issue.type, []).append(issue)
        self._index_by_type = {
            t: TfidfIndex([i.corpus_text for i in issues])
            for t, issues in self._issues_by_type.items()
        }

    def evaluate(self, candidate: Candidate, transcript: Optional[Transcript] = None) -> MatchOutcome:
        """Decide FILE_NEW / CORROBORATE / NONE(shipped) for one candidate.
        Pass the source `transcript` when available for better match recall
        (see `_query_text`). Never mutates the pool -- call `register_new`
        afterward if the orchestrator actually proceeds with filing it."""
        issue_type = _issue_type_for(candidate)
        pool = self._issues_by_type.get(issue_type, [])
        index = self._index_by_type.get(issue_type)
        if not pool or index is None:
            return MatchOutcome(
                Action.FILE_NEW, None, 0.0,
                f"no tracked {issue_type} issues to compare against",
            )

        idx, sim = index.best_match(_query_text(candidate, transcript))
        if idx is None or sim < self._threshold:
            return MatchOutcome(
                Action.FILE_NEW, None, sim,
                f"no existing {issue_type} issue matched above threshold (best similarity={sim:.2f})",
            )

        matched = pool[idx]
        if matched.is_shipped:
            return MatchOutcome(
                Action.NONE, matched.key, sim,
                f"matches already-shipped {matched.key} ({matched.shipped_in}); "
                "enablement, not a new ticket",
            )
        return MatchOutcome(
            Action.CORROBORATE, matched.key, sim,
            f"matches tracked {matched.key} (similarity={sim:.2f})",
        )

    def register_new(self, key: str, candidate: Candidate) -> None:
        """Fold a just-filed (or about-to-be-filed) candidate back into the
        pool so later candidates -- same call or a later one this run --
        corroborate against it instead of creating a duplicate."""
        issue_type = _issue_type_for(candidate)
        self._issues.append(
            ExistingIssue(
                key=key,
                type=issue_type,
                status="Pending (this run)",
                summary=candidate.draft_title,
                description=candidate.snippet,
                created="",
                reported_by_accounts=(candidate.account,) if candidate.account else (),
            )
        )
        self._rebuild()

    def next_pending_key(self) -> str:
        """A placeholder key for a candidate about to be filed, used before a
        human has approved it and a real Jira key exists. The orchestrator
        is responsible for reconciling `PENDING:n` references to the real
        key once assigned (see orchestrator.py)."""
        self._pending_count += 1
        return f"{PENDING_KEY_PREFIX}{self._pending_count}"
