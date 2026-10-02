from __future__ import annotations

import json
from time import monotonic
from typing import Callable

from .config import Config
from .ingest import parse_transcript
from .orchestrator import _rehydrate_decision
from .payloads import build_jira_payload, build_slack_payload
from .review import load_review_decisions, proposal_digest, queued_entries, record_decision
from .state_store import StateStore


def review_view(cfg: Config, key: str, entry: dict) -> dict:
    transcript = parse_transcript(cfg.transcripts_dir / f"{entry['call_id']}.md")
    decision = _rehydrate_decision(entry, key)
    target = entry.get("matched_key")
    issues = json.loads(cfg.existing_issues_path.read_text(encoding="utf-8"))
    matched = next((issue for issue in issues if issue["key"] == target), None)
    if matched is None:
        matched = next((value for value in StateStore(cfg.state_path).all_entries().values()
                        if value.get("matched_key") == target and value.get("action") in
                        ("file-new", "file-new-low")), None)
    corroboration = entry["action"] == "corroborate"
    return {
        "key": key, "priority": entry["priority"], "account": entry.get("account"),
        "title": entry["summary"], "action": entry["action"],
        "source": {"path": str(transcript.path), "turn_span": entry.get("turn_span"),
                   "quote": entry.get("description")},
        "dedup": {"target": target if corroboration else None, "issue": matched if corroboration else None,
                  "rationale": entry.get("rationale")},
        "jira_preview": None if corroboration else build_jira_payload(decision, transcript),
        "slack_preview": build_slack_payload(decision, transcript, issue_key=target or "AFTER_APPROVAL"),
        "proposal_sha256": proposal_digest(entry),
    }


def run_triage(cfg: Config, reviewer: str, *, read: Callable[[str], str] = input,
               write: Callable[[str], None] = print, clock: Callable[[], float] = monotonic) -> dict:
    if not reviewer.strip():
        raise ValueError("Reviewer identity is required")
    entries = queued_entries(StateStore(cfg.state_path).all_entries())
    decisions = load_review_decisions(cfg.review_decisions_path)
    counts = {"approved": 0, "rejected": 0, "skipped": 0}
    for key, entry in sorted(entries.items(), key=lambda item: (item[1].get("priority", "P3"), item[0])):
        if decisions.get(key, {}).get("decision", "pending") != "pending":
            continue
        write(json.dumps(review_view(cfg, key, entry), indent=2, ensure_ascii=True))
        started = clock()
        while True:
            try:
                answer = read("[a]pprove / [r]eject / [s]kip / [q]uit: ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return counts
            if answer == "q":
                return counts
            if answer == "s":
                counts["skipped"] += 1
                break
            if answer not in ("a", "r"):
                continue
            try:
                note = read("Reason (required for rejection): ")
            except (EOFError, KeyboardInterrupt):
                return counts
            current = StateStore(cfg.state_path).get(key)
            if current is None or proposal_digest(current) != proposal_digest(entry):
                raise ValueError("Proposal changed during review; reopen it before deciding")
            decision = "approved" if answer == "a" else "rejected"
            try:
                record_decision(cfg.review_decisions_path, key, current, decision=decision,
                                reviewer=reviewer, note=note, elapsed_seconds=clock() - started)
            except ValueError as exc:
                write(str(exc))
                continue
            counts[decision] += 1
            break
    return counts