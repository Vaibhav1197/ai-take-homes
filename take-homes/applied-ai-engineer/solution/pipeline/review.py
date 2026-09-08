"""Stage 4: the human-review gate.

The README's hard requirement: "Nothing files automatically: a human reviews
and approves before anything is written." This module owns the artifact
shapes for that gate -- it does not decide *what* goes in the queue (that's
state_store's ledger, populated by orchestrator.py), only how to present it
for fast human review and how to read back a human's decisions.

Two files, two audiences:
- `review_queue.md`: human-readable, grouped by priority so the highest-
  impact items are read first. Regenerated in full every run_review() --
  always reflects the CURRENT set of undecided items, nothing more.
- `review_decisions.json`: machine-readable, one entry per queued item, a
  human edits `"decision"` from `"pending"` to `"approved"`/`"rejected"`.
  Re-syncing (`sync_review_decisions`) is additive/non-destructive: it adds
  scaffolding for newly-queued keys and refreshes context fields on still-
  pending ones, but NEVER touches a key that already has a real decision,
  no matter how many times review is re-run before that decision is applied.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PRIORITY_ORDER = {"P1": 0, "P2": 1, "P3": 2, "P4": 3}


def queued_entries(all_entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Filter a state_store snapshot down to items awaiting a human decision."""
    return {k: v for k, v in all_entries.items() if v.get("status") == "queued"}


def write_review_queue_markdown(entries: dict[str, dict[str, Any]], path: Path) -> None:
    """Render `entries` (ledger key -> fields) as a priority-sorted Markdown
    review queue. Overwrites `path` in full every call -- this file is a
    projection of current ledger state, not something to hand-edit."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ordered = sorted(
        entries.items(),
        key=lambda kv: (_PRIORITY_ORDER.get(kv[1].get("priority", "P3"), 2), kv[0]),
    )

    lines = ["# Review queue", ""]
    if not ordered:
        lines.append("Nothing awaiting review.")
    else:
        lines.append(f"{len(ordered)} item(s) awaiting a decision. Edit `review_decisions.json` "
                      "(pending -> approved/rejected), then re-run `apply`.")
        lines.append("")
        for key, entry in ordered:
            lines.extend(_render_entry(key, entry))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_entry(key: str, entry: dict[str, Any]) -> list[str]:
    action = entry.get("action", "unknown")
    priority = entry.get("priority", "P3")
    account = entry.get("account") or "unknown account"
    call_id = entry.get("call_id", "unknown call")
    confidence = entry.get("confidence")
    confidence_str = f"{confidence:.2f}" if isinstance(confidence, (int, float)) else "n/a"
    out = [
        f"## [{priority}] {entry.get('summary', '(no title)')}",
        "",
        f"- key: `{key}`",
        f"- call: {call_id} ({account})",
        f"- action: **{action}**"
        + (f" -> matches `{entry['matched_key']}`" if entry.get("matched_key") else ""),
        f"- issue type: {entry.get('issue_type', 'n/a')}",
        f"- confidence: {confidence_str}",
        f"- rationale: {entry.get('rationale', 'n/a')}",
    ]
    if entry.get("description"):
        out.append(f"- evidence: \"{entry['description']}\"")
    out.append("")
    return out


def sync_review_decisions(entries: dict[str, dict[str, Any]], path: Path) -> dict[str, dict[str, Any]]:
    """Add `"decision": "pending"` scaffolding for any key in `entries` not
    already present in `path`, refresh convenience/context fields (summary,
    call_id, action, priority) on entries still pending, and NEVER modify a
    key that already has a non-"pending" decision recorded. Writes the
    merged result back to `path` and returns it.
    """
    path = Path(path)
    decisions = load_review_decisions(path)

    for key, entry in entries.items():
        existing = decisions.get(key)
        if existing is None:
            decisions[key] = {
                "decision": "pending",
                "note": "",
                "call_id": entry.get("call_id"),
                "action": entry.get("action"),
                "summary": entry.get("summary"),
                "priority": entry.get("priority"),
            }
        elif existing.get("decision") == "pending":
            existing.update(
                call_id=entry.get("call_id"),
                action=entry.get("action"),
                summary=entry.get("summary"),
                priority=entry.get("priority"),
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(decisions, indent=2, sort_keys=True), encoding="utf-8")
    return decisions


def load_review_decisions(path: Path) -> dict[str, dict[str, Any]]:
    """Read `review_decisions.json`, or `{}` if it doesn't exist yet."""
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
