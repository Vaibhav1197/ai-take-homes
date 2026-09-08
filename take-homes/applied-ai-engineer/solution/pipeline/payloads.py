"""Stage 3: build the structured Jira ticket + Slack notification payloads.

Only ever called for decisions a human has approved (see review.py /
orchestrator.py) -- this module has no opinion on *whether* something should
be filed, only on *how to shape the payload* once the answer is yes. Kept
pure/deterministic (string templating only, no I/O, no judgment calls) so it
is trivially unit-testable: given the same Decision + Transcript, it always
produces the same payload.

Covers the two genuine-new-issue outcomes (Action.FILE_NEW /
Action.FILE_NEW_LOW -> a new Jira ticket + a Slack ping) and the
duplicate-but-real outcome (Action.CORROBORATE -> no new ticket, just a
Slack ping noting the corroboration against the existing key). Action.NONE
(suppressed noise, or "already shipped") deliberately has no payload here --
the README's ask is a payload "for each genuine, new issue"; already-shipped
enablement replies and non-actionable noise are logged for observability
(see logging_utils.py) but are out of scope for Jira/Slack, so
`build_slack_payload`/`build_jira_payload` raise rather than silently
fabricate a payload for that case.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Optional

from .ingest import internal_owner_name
from .models import Action, Decision, Transcript

PROJECT_KEY = "PROJ"

_ACTIONABLE_FOR_TICKET = (Action.FILE_NEW, Action.FILE_NEW_LOW)


def _slugify_owner(name: str) -> str:
    """"Tomás Vela" -> "tomas.vela": ASCII-normalized, Slack-handle-shaped."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    parts = re.findall(r"[a-zA-Z0-9]+", ascii_name.lower())
    return ".".join(parts) if parts else "unknown-owner"


def _transcript_reference(decision: Decision, transcript: Transcript) -> str:
    lo, hi = decision.candidate.turn_span
    return f"{transcript.path}#turns={lo}-{hi}"


def build_jira_payload(decision: Decision, transcript: Transcript) -> dict:
    """Payload shape matching stubs/jira_stub.py's `_REQUIRED` fields plus
    `priority`/`source` (accepted as passthrough extras by the stub).

    Raises ValueError if `decision.action` isn't a file-new outcome -- this
    function must never be called for a corroborate/none decision, and
    calling it by mistake should fail loudly rather than open a bogus
    duplicate ticket.
    """
    if decision.action not in _ACTIONABLE_FOR_TICKET:
        raise ValueError(
            f"build_jira_payload: only FILE_NEW/FILE_NEW_LOW decisions open a ticket, "
            f"got action={decision.action.value!r}"
        )
    if decision.issue_type is None:
        raise ValueError("build_jira_payload: decision.issue_type is required to file a ticket")

    candidate = decision.candidate
    return {
        "project": PROJECT_KEY,
        "type": decision.issue_type.value,
        "summary": decision.title,
        "description": _build_description(decision, transcript),
        "priority": decision.priority,
        "source": {
            "call_id": decision.call_id,
            "account": candidate.account,
            "turn_span": list(candidate.turn_span),
            "snippet": candidate.snippet,
            "transcript_ref": _transcript_reference(decision, transcript),
        },
    }


def _build_description(decision: Decision, transcript: Transcript) -> str:
    candidate = decision.candidate
    lines = [
        f"Reported by: {candidate.account or 'unknown account'} "
        f"(call {decision.call_id}, {transcript.date})",
        "",
        f'"{candidate.snippet}"',
        "",
        f"Transcript: {_transcript_reference(decision, transcript)}",
        f"Judge rationale: {decision.rationale}",
    ]
    if decision.action is Action.FILE_NEW_LOW:
        lines.append(
            "Note: low-confidence auto-detection -- please confirm this is a genuine, "
            "actionable issue before triaging further."
        )
    return "\n".join(lines)


def build_slack_payload(decision: Decision, transcript: Transcript, issue_key: str) -> dict:
    """Payload shape matching stubs/slack_stub.py's `_REQUIRED` fields.

    `issue_key` is passed explicitly (rather than read off `decision`)
    because for a fresh FILE_NEW ticket it only exists *after*
    jira_stub.create_issue() has actually run -- the orchestrator is
    responsible for sequencing "file, then notify" and supplying the real
    key. For CORROBORATE it's simply the already-tracked key being matched.

    Raises ValueError for Action.NONE -- see module docstring.
    """
    if decision.action is Action.NONE:
        raise ValueError("build_slack_payload: Action.NONE decisions are not notified")

    owner = internal_owner_name(transcript)
    channel = f"@{_slugify_owner(owner)}"
    text = (
        _corroborate_text(decision, issue_key, owner)
        if decision.action is Action.CORROBORATE
        else _new_ticket_text(decision, issue_key, owner)
    )
    return {
        "channel": channel,
        "text": text,
        "source": {
            "call_id": decision.call_id,
            "action": decision.action.value,
            "issue_key": issue_key,
        },
    }


def _new_ticket_text(decision: Decision, issue_key: str, owner: str) -> str:
    candidate = decision.candidate
    account = candidate.account or "Unknown account"
    urgency = ":rotating_light:" if decision.priority in ("P1", "P2") else ":memo:"
    low_confidence_note = (
        " (low-confidence -- please verify)" if decision.action is Action.FILE_NEW_LOW else ""
    )
    issue_type = decision.issue_type.value if decision.issue_type else "Issue"
    return (
        f"{urgency} New {issue_type} filed from *{account}* (call {decision.call_id}, "
        f"priority {decision.priority}){low_confidence_note}: {decision.title}\n"
        f'> "{candidate.snippet}"\n'
        f"Jira: {issue_key} -- cc {owner}"
    )


def _corroborate_text(decision: Decision, issue_key: str, owner: str) -> str:
    candidate = decision.candidate
    account = candidate.account or "Unknown account"
    return (
        f":link: *{account}* (call {decision.call_id}) reported the same issue tracked as "
        f"*{issue_key}*: \"{candidate.snippet}\"\n"
        f"No new ticket filed -- added as a corroborating source on {issue_key}. cc {owner}"
    )
