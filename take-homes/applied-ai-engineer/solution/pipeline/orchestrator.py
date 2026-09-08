"""Stage 5: orchestration.

Wires ingest -> judge -> dedup -> state_store -> review into the two
commands the README's human-gate requirement implies:

- `run_review()`: parse every transcript, find candidates, de-duplicate them
  against tracked + previously-filed + currently-pending issues, and queue
  every genuine (file-new/corroborate) outcome for human review. Never
  calls the Jira/Slack stubs -- "nothing files automatically."
- `run_apply()`: read a human's `review_decisions.json` and, for every
  `"approved"` item, actually call the Jira/Slack stubs (in dependency
  order: new tickets before corroborations that might reference one), then
  record the outcome in state_store so it can never be re-applied.

Reliability guarantees implemented here:
- **Partial failure isolation**: each transcript, and each apply-decision,
  is wrapped in its own try/except. One bad transcript or one failed stub
  call is logged and skipped; it never aborts the batch.
- **Idempotency**: `state_store` is consulted before any work is redone.
  A candidate already filed, rejected, marked not-actionable, or collapsed
  as a same-call duplicate in a past run is skipped outright on every
  subsequent run -- re-running the whole pipeline over the same transcripts
  is a safe no-op for anything already resolved.
- **Same-call duplicate collapse**: multiple candidates from the SAME call
  that resolve to the SAME target (an existing ticket, a pending one from
  earlier in this call, or each other) are collapsed into one queued item --
  see `_process_call_for_review`'s `seen_targets_this_call`. Otherwise a
  call that mentions one bug three times would spam three notifications
  for it (observed directly in calls 008/010/011/013 during dedup tuning).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from stubs import jira_stub, slack_stub

from .config import Config, load_config
from .dedup import PENDING_KEY_PREFIX, Deduplicator, load_existing_issues
from .ingest import TranscriptParseError, iter_transcript_paths, parse_transcript
from .judge_base import IssueJudge
from .heuristic_judge import HeuristicJudge
from .logging_utils import EventLogger
from .models import Action, Candidate, Decision, IssueType, Transcript
from .payloads import build_jira_payload, build_slack_payload
from .review import load_review_decisions, queued_entries, sync_review_decisions, write_review_queue_markdown
from .state_store import StateStore, candidate_key

_TERMINAL_STATUSES = frozenset({"filed", "corroborated", "rejected", "not_actionable", "collapsed_duplicate"})
_FILE_NEW_ACTIONS = frozenset({Action.FILE_NEW.value, Action.FILE_NEW_LOW.value})


@dataclass
class ReviewRunSummary:
    calls_processed: int = 0
    calls_failed: int = 0
    candidates_found: int = 0
    candidates_suppressed: int = 0
    not_actionable: int = 0
    collapsed_duplicates: int = 0
    skipped_already_processed: int = 0
    queued_for_review: int = 0


@dataclass
class ApplyRunSummary:
    filed: int = 0
    corroborated: int = 0
    rejected: int = 0
    failed: int = 0


def _make_judge(cfg: Config) -> IssueJudge:
    if cfg.judge == "llm":
        from .llm_judge import LLMJudge  # local import: optional dependency path

        return LLMJudge(model=cfg.openai_model)
    return HeuristicJudge()


def _transcript_path(cfg: Config, call_id: str) -> Path:
    return cfg.transcripts_dir / f"{call_id}.md"


def _confidence_for(candidate: Candidate, outcome) -> float:
    if outcome.matched_key is not None:
        return round(outcome.similarity, 3)
    return round(min(1.0, candidate.raw_score / 4.0), 3)


def _build_decision(candidate: Candidate, outcome, key: str) -> Decision:
    """Combine a judge's Candidate with dedup's MatchOutcome into the final
    Decision record. The one piece of business logic that lives here rather
    than in dedup.py: downgrading FILE_NEW to FILE_NEW_LOW when keyword
    support is thin (a single hit, no corroborating flags) -- still queued
    for a human, just flagged as needing extra scrutiny rather than
    presented as a confident find (keeps the fast path fast; see review.py).
    """
    issue_type = IssueType.BUG if candidate.signal_type == "bug" else IssueType.FEATURE
    action = outcome.action
    if action is Action.FILE_NEW and candidate.raw_score <= 1.0 and not candidate.flags:
        action = Action.FILE_NEW_LOW
    return Decision(
        candidate=candidate,
        action=action,
        issue_type=issue_type if action is not Action.NONE else None,
        title=candidate.draft_title,
        priority=candidate.provisional_priority,
        rationale=outcome.rationale,
        confidence=_confidence_for(candidate, outcome),
        matched_issue_key=outcome.matched_key,
        idempotency_key=key,
        needs_human_priority_call=candidate.needs_human_priority_call,
    )


def _rehydrate_candidate(entry: dict) -> Candidate:
    """Reconstruct just enough of a Candidate from a ledger entry to build
    payloads (account/turn_span/snippet) -- fields only needed during the
    original judge/dedup pass (keyword_hits, flags, raw_score, ...) are not
    persisted and are not needed again once a decision is queued."""
    turn_span = tuple(entry.get("turn_span", [0, 0]))
    return Candidate(
        call_id=entry["call_id"],
        account=entry.get("account"),
        primary_turn_index=turn_span[0],
        turn_span=turn_span,  # type: ignore[arg-type]
        snippet=entry.get("description", ""),
        signal_type="bug" if entry.get("issue_type") == "Bug" else "feature",
        draft_title=entry.get("summary", ""),
    )


def _rehydrate_decision(entry: dict, key: str) -> Decision:
    issue_type = IssueType(entry["issue_type"]) if entry.get("issue_type") else None
    return Decision(
        candidate=_rehydrate_candidate(entry),
        action=Action(entry["action"]),
        issue_type=issue_type,
        title=entry.get("summary", ""),
        priority=entry.get("priority", "P3"),
        rationale=entry.get("rationale", ""),
        confidence=entry.get("confidence", 0.0),
        matched_issue_key=entry.get("matched_key"),
        idempotency_key=key,
    )


def _reseed_pending_entries(store: StateStore, dedup: Deduplicator) -> None:
    """Fold currently-queued (not yet human-decided) file-new entries back
    into a freshly-constructed Deduplicator's pool, using their EXISTING
    PENDING key. Without this, re-running `run_review` before a human has
    approved anything would "forget" about not-yet-applied candidates
    between passes (state_store.filed_issues() only knows about candidates
    that were actually approved+filed), and a second call reporting the
    same not-yet-reviewed issue would wrongly open a second queue item
    instead of corroborating against the first.
    """
    for key, entry in store.all_entries().items():
        if entry.get("status") == "queued" and entry.get("action") in _FILE_NEW_ACTIONS:
            matched_key = entry.get("matched_key")
            if matched_key:
                dedup.register_new(matched_key, _rehydrate_candidate(entry))


def run_review(cfg: Optional[Config] = None) -> ReviewRunSummary:
    cfg = cfg or load_config()
    store = StateStore(cfg.state_path)
    logger = EventLogger(cfg.log_path)
    judge = _make_judge(cfg)

    base_issues = load_existing_issues(cfg.existing_issues_path)
    dedup = Deduplicator(base_issues + store.filed_issues(), similarity_threshold=cfg.similarity_threshold)
    _reseed_pending_entries(store, dedup)

    summary = ReviewRunSummary()
    logger.emit("run_review_started", judge=cfg.judge)

    for path in iter_transcript_paths(cfg.transcripts_dir):
        try:
            transcript = parse_transcript(path)
        except TranscriptParseError as exc:
            summary.calls_failed += 1
            logger.emit("call_parse_failed", path=str(path), error=str(exc))
            continue

        try:
            _process_call_for_review(transcript, judge, dedup, store, logger, summary)
            summary.calls_processed += 1
        except Exception as exc:  # noqa: BLE001 -- partial-failure isolation boundary
            summary.calls_failed += 1
            logger.emit("call_failed", call_id=transcript.call_id, error=str(exc))
            continue

    queued = queued_entries(store.all_entries())
    write_review_queue_markdown(queued, cfg.review_queue_path)
    sync_review_decisions(queued, cfg.review_decisions_path)

    logger.emit("run_review_completed", **summary.__dict__)
    return summary


def _process_call_for_review(
    transcript: Transcript,
    judge: IssueJudge,
    dedup: Deduplicator,
    store: StateStore,
    logger: EventLogger,
    summary: ReviewRunSummary,
) -> None:
    seen_targets_this_call: set[str] = set()

    for candidate in judge.find_candidates(transcript):
        summary.candidates_found += 1
        if candidate.suppressed:
            summary.candidates_suppressed += 1
            logger.emit(
                "candidate_suppressed", call_id=transcript.call_id,
                turn_span=list(candidate.turn_span), reason=candidate.suppression_reason,
            )
            continue

        key = candidate_key(candidate)
        existing = store.get(key)
        if existing is not None and existing.get("status") in _TERMINAL_STATUSES:
            summary.skipped_already_processed += 1
            logger.emit(
                "skipped_already_processed", call_id=transcript.call_id, key=key,
                status=existing.get("status"),
            )
            continue
        if existing is not None and existing.get("status") == "queued":
            if existing.get("matched_key"):
                seen_targets_this_call.add(existing["matched_key"])
            continue  # already queued (this run's reseed, or a prior review pass); nothing new to do

        outcome = dedup.evaluate(candidate, transcript=transcript)
        if outcome.action is Action.NONE:
            summary.not_actionable += 1
            store.upsert(
                key, status="not_actionable", call_id=transcript.call_id,
                action=outcome.action.value, matched_key=outcome.matched_key,
                rationale=outcome.rationale,
            )
            logger.emit("call_none_action", call_id=transcript.call_id, key=key, rationale=outcome.rationale)
            continue

        decision = _build_decision(candidate, outcome, key)
        if decision.action in (Action.FILE_NEW, Action.FILE_NEW_LOW):
            pending_key = dedup.next_pending_key()
            decision.matched_issue_key = pending_key
            dedup.register_new(pending_key, candidate)

        target = decision.matched_issue_key
        if decision.action is Action.CORROBORATE and target in seen_targets_this_call:
            summary.collapsed_duplicates += 1
            store.upsert(
                key, status="collapsed_duplicate", call_id=transcript.call_id,
                collapsed_into=target, action=decision.action.value,
            )
            logger.emit("collapsed_same_call_duplicate", call_id=transcript.call_id, key=key, target=target)
            continue
        if target:
            seen_targets_this_call.add(target)

        store.upsert(
            key, status="queued", call_id=transcript.call_id, account=candidate.account,
            action=decision.action.value, matched_key=decision.matched_issue_key,
            issue_type=decision.issue_type.value if decision.issue_type else None,
            summary=decision.title, description=candidate.snippet, priority=decision.priority,
            confidence=decision.confidence, rationale=decision.rationale,
            turn_span=list(candidate.turn_span),
        )
        summary.queued_for_review += 1
        logger.emit("queued_for_review", call_id=transcript.call_id, key=key, action=decision.action.value)


def run_apply(cfg: Optional[Config] = None) -> ApplyRunSummary:
    cfg = cfg or load_config()
    store = StateStore(cfg.state_path)
    logger = EventLogger(cfg.log_path)
    decisions = load_review_decisions(cfg.review_decisions_path)

    summary = ApplyRunSummary()
    logger.emit("run_apply_started")
    pending_key_map: dict[str, str] = {}

    all_entries = store.all_entries()

    # Pass 1: file every approved new ticket first, building up
    # pending-key -> real-key so pass 2's corroborations (which may point at
    # a PENDING key filed earlier in the SAME batch) can resolve it.
    for key, entry in all_entries.items():
        if entry.get("status") != "queued" or entry.get("action") not in _FILE_NEW_ACTIONS:
            continue
        review_decision = decisions.get(key, {}).get("decision", "pending")
        if review_decision == "rejected":
            store.upsert(key, status="rejected")
            summary.rejected += 1
            logger.emit("decision_rejected", key=key, call_id=entry.get("call_id"))
            continue
        if review_decision != "approved":
            continue  # still pending a human decision

        try:
            transcript = parse_transcript(_transcript_path(cfg, entry["call_id"]))
            decision = _rehydrate_decision(entry, key)
            record = jira_stub.create_issue(build_jira_payload(decision, transcript))
            real_key = record["key"]
            if str(entry.get("matched_key", "")).startswith(PENDING_KEY_PREFIX):
                pending_key_map[entry["matched_key"]] = real_key
            slack_stub.post_message(build_slack_payload(decision, transcript, issue_key=real_key))
            store.upsert(
                key, status="filed", issue_key=real_key, issue_type=entry.get("issue_type"),
                summary=entry.get("summary"), description=entry.get("description"),
                reported_by_accounts=[entry["account"]] if entry.get("account") else [],
            )
            summary.filed += 1
            logger.emit("ticket_filed", key=key, issue_key=real_key, call_id=entry.get("call_id"))
        except Exception as exc:  # noqa: BLE001 -- partial-failure isolation boundary
            summary.failed += 1
            logger.emit("apply_failed", key=key, call_id=entry.get("call_id"), error=str(exc))

    # Pass 2: corroborations, resolved through pending_key_map when needed.
    for key, entry in all_entries.items():
        if entry.get("status") != "queued" or entry.get("action") != Action.CORROBORATE.value:
            continue
        review_decision = decisions.get(key, {}).get("decision", "pending")
        if review_decision == "rejected":
            store.upsert(key, status="rejected")
            summary.rejected += 1
            logger.emit("decision_rejected", key=key, call_id=entry.get("call_id"))
            continue
        if review_decision != "approved":
            continue

        try:
            matched_key = str(entry.get("matched_key", ""))
            real_key = pending_key_map.get(matched_key, matched_key)
            transcript = parse_transcript(_transcript_path(cfg, entry["call_id"]))
            decision = _rehydrate_decision(entry, key)
            slack_stub.post_message(build_slack_payload(decision, transcript, issue_key=real_key))
            store.upsert(key, status="corroborated", issue_key=real_key)
            summary.corroborated += 1
            logger.emit("corroboration_notified", key=key, issue_key=real_key, call_id=entry.get("call_id"))
        except Exception as exc:  # noqa: BLE001 -- partial-failure isolation boundary
            summary.failed += 1
            logger.emit("apply_failed", key=key, call_id=entry.get("call_id"), error=str(exc))

    logger.emit("run_apply_completed", **summary.__dict__)
    return summary
