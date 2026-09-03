"""Durable ledger giving the pipeline its cross-run idempotency guarantee.

The take-home requires: "Running it twice over the same transcripts must not
create duplicate tickets or notifications... A partial failure (one
transcript errors) doesn't corrupt the rest." This module is where both
guarantees actually live:

1. **No duplicate work across runs.** Every Candidate the pipeline ever
   queues for human review is recorded here under a stable key (see
   `candidate_key`). Before (re-)processing a call, the orchestrator checks
   whether that key already has a human decision or was already filed --
   if so, it skips straight past it instead of re-asking a human or calling
   the Jira/Slack stubs again. The stubs themselves do *not* de-duplicate
   (by design, per their docstrings), so this ledger is the only thing
   standing between a re-run and duplicate tickets/notifications.

2. **Partial-failure isolation.** `upsert()` performs a full atomic
   temp-file-then-`os.replace` rewrite after every meaningful state
   transition (queued -> reviewed -> filed), not just once at the end of a
   batch. If the process dies mid-run (call 83 of 140 raises), every call
   processed before it is durably recorded; re-running the batch resumes
   roughly where it left off instead of redoing (or losing) prior work.
   `os.replace` is atomic on both POSIX and Windows, so a crash mid-write
   never leaves a half-written, corrupt ledger on disk. On Windows the
   replace is wrapped with a short bounded retry (`_replace_with_retry`) to
   absorb the transient `PermissionError` that AV/indexer/cloud-sync
   processes occasionally cause by briefly holding the destination file
   open right after a write -- observed directly during a full 140-call
   run; without the retry this looked like a "partial failure" on a
   perfectly fine transcript, which is exactly the failure mode this
   module exists to prevent.

3. **Cross-run dedup pool seeding.** `filed_issues()` reconstructs
   `ExistingIssue` records for everything this pipeline has actually filed
   in any past run, so a fresh run's `Deduplicator` (see dedup.py) can be
   seeded with `data/existing_issues.json + store.filed_issues()`. That is
   what lets a call processed today correctly corroborate against a ticket
   a *different* call caused to be filed last week, even though neither is
   in the read-only existing_issues.json snapshot.

Deliberately generic: this module knows nothing about Jira/Slack payload
shapes or the review-queue file format. It is a small key -> dict store with
atomic persistence; orchestrator.py and review.py decide what fields to
`upsert` and when. Keeping it generic keeps it easy to unit test in
isolation and reusable if the review workflow's exact fields change later.
"""
from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Optional

from .models import Candidate, ExistingIssue

_STATE_VERSION = 1

DEFAULT_STATE_PATH = Path(__file__).resolve().parent.parent / "state" / "pipeline_state.json"

# os.replace() is atomic on both POSIX and Windows, but on Windows it can
# transiently raise PermissionError (WinError 5) if another process --
# antivirus real-time scanning, the search indexer, cloud-sync -- briefly
# holds an open handle on the destination right after it's (re)written.
# Observed empirically: ~1-3 times per 140-call run, on essentially random
# calls, always clearing within milliseconds. Nothing in this codebase holds
# a competing handle (the temp file's own handle is closed before replace is
# attempted), so this is not a real conflict -- a short bounded retry is the
# standard mitigation rather than letting a transient OS race surface as a
# pipeline failure that aborts an otherwise-fine call.
_REPLACE_RETRIES = 6
_REPLACE_RETRY_DELAY_S = 0.05


def _replace_with_retry(src: str, dst: Path) -> None:
    last_error: Optional[PermissionError] = None
    for attempt in range(_REPLACE_RETRIES):
        try:
            os.replace(src, dst)
            return
        except PermissionError as exc:
            last_error = exc
            if attempt < _REPLACE_RETRIES - 1:
                time.sleep(_REPLACE_RETRY_DELAY_S)
    assert last_error is not None
    raise last_error


def candidate_key(candidate: Candidate) -> str:
    """Stable idempotency key for a Candidate, used as the ledger's primary
    key and as `Decision.idempotency_key`.

    Anchored on the call id, the single turn the judge identified as the
    strongest signal (`primary_turn_index`), and the signal type -- not the
    full `turn_span`. The shipped HeuristicJudge is fully deterministic, so
    the span is stable run to run anyway, but anchoring on the primary turn
    keeps this key robust even against a future non-deterministic judge
    (e.g. an LLM judge) that might shift a window boundary by a turn without
    changing which real-world moment in the call it is anchored to.
    """
    return f"{candidate.call_id}#{candidate.primary_turn_index}#{candidate.signal_type}"


class StateStore:
    """Loads (or initializes) a single JSON ledger file and persists it with
    atomic whole-file rewrites on every `upsert`."""

    def __init__(self, path: Path | str = DEFAULT_STATE_PATH) -> None:
        self.path = Path(path)
        self._entries: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self._entries = raw.get("entries", {})

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": _STATE_VERSION, "entries": self._entries}
        fd, tmp_name = tempfile.mkstemp(
            dir=str(self.path.parent), prefix=".state_store_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2, sort_keys=True)
                fh.flush()
                os.fsync(fh.fileno())
            _replace_with_retry(tmp_name, self.path)
        except BaseException:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
            raise

    def get(self, key: str) -> Optional[dict[str, Any]]:
        entry = self._entries.get(key)
        return dict(entry) if entry is not None else None

    def upsert(self, key: str, **fields: Any) -> dict[str, Any]:
        """Merge `fields` into the entry for `key` (creating it if absent)
        and persist immediately. Returns the updated entry."""
        entry = self._entries.setdefault(key, {})
        entry.update(fields)
        self._save()
        return dict(entry)

    def all_entries(self) -> dict[str, dict[str, Any]]:
        """All ledger entries, keyed by `candidate_key`. Read-only snapshot
        for review.py (building the review queue) and observability."""
        return {k: dict(v) for k, v in self._entries.items()}

    def filed_issues(self) -> list[ExistingIssue]:
        """Reconstruct ExistingIssue records for every entry this pipeline
        has actually filed (status == "filed") in any past run -- see
        module docstring point 3."""
        out: list[ExistingIssue] = []
        for entry in self._entries.values():
            if entry.get("status") != "filed" or not entry.get("issue_key"):
                continue
            out.append(
                ExistingIssue(
                    key=entry["issue_key"],
                    type=entry.get("issue_type", "Bug"),
                    status="Open",
                    summary=entry.get("summary", ""),
                    description=entry.get("description", ""),
                    created=entry.get("filed_at", ""),
                    reported_by_accounts=tuple(entry.get("reported_by_accounts", ())),
                    shipped_in=None,
                )
            )
        return out
