"""Transcript ingestion: parse the .md call transcripts into structured data.

Parsing here is 100% deterministic string/regex work -- there is no judgment
call in this file, only format extraction. Every `Turn.text` is preserved
verbatim from the source file so later stages can quote the transcript
exactly rather than paraphrase it (the raw transcript is the source of
truth; see WRITEUP.md).
"""
from __future__ import annotations

import re
from pathlib import Path

from .models import Speaker, Transcript, Turn

_TITLE_RE = re.compile(r"^#\s*Call\s*[\u2014-]\s*(?P<title>.+)$")
_DATE_RE = re.compile(r"Date:\s*(?P<date>[^\u00b7]+?)\s*\u00b7\s*Call ID:\s*(?P<call_id>\S+)")
_PARTICIPANTS_RE = re.compile(r"^Participants:\s*(?P<rest>.+)$")
_TURN_RE = re.compile(r"^\[(EXTERNAL|INTERNAL)\]\s*([^:]+):\s?(.*)$")
_SEGMENT_RE = re.compile(r"^\[(EXTERNAL|INTERNAL)\]\s*(?P<rest>.+)$")


class TranscriptParseError(ValueError):
    """Raised when a transcript file doesn't match the expected format."""


def parse_transcript(path: Path) -> Transcript:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title_match = None
    date_match = None
    participants_raw = ""
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if title_match is None:
            title_match = _TITLE_RE.match(line)
            if title_match:
                continue
        if date_match is None:
            date_match = _DATE_RE.search(line)
            if date_match:
                continue
        if not participants_raw:
            p_match = _PARTICIPANTS_RE.match(line)
            if p_match:
                participants_raw = p_match.group("rest").strip()

    if title_match is None or date_match is None:
        raise TranscriptParseError(
            f"{path.name}: missing '# Call \u2014 ...' title or 'Date: ... \u00b7 Call ID: ...' header line"
        )

    title = title_match.group("title").strip()
    call_id = date_match.group("call_id").strip()
    date = date_match.group("date").strip()

    if "\u00d7 BetterBark" in title:
        account_part, _, rest = title.partition("\u00d7 BetterBark")
        account = account_part.strip() or None
        call_type = rest.strip(" \u00b7").strip() or "Unknown"
    else:
        account = None
        call_type = title

    # Turns are identified purely by the [EXTERNAL]/[INTERNAL] line prefix, so
    # we can scan the whole file rather than trying to compute where the
    # header ends -- header lines never match _TURN_RE.
    turns: list[Turn] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        m = _TURN_RE.match(line)
        if m:
            speaker = Speaker.EXTERNAL if m.group(1) == "EXTERNAL" else Speaker.INTERNAL
            turns.append(
                Turn(index=len(turns), speaker=speaker, name=m.group(2).strip(), text=m.group(3).strip())
            )
        elif turns:
            # Defensive: a wrapped continuation line with no [SPEAKER] prefix.
            prev = turns[-1]
            turns[-1] = Turn(
                index=prev.index, speaker=prev.speaker, name=prev.name, text=f"{prev.text} {line}"
            )
        # else: stray text before the first turn (shouldn't happen) -- ignore.

    if not turns:
        raise TranscriptParseError(f"{path.name}: no [EXTERNAL]/[INTERNAL] dialogue turns found")

    return Transcript(
        call_id=call_id,
        title=title,
        account=account,
        date=date,
        call_type=call_type,
        participants_raw=participants_raw,
        turns=tuple(turns),
        path=str(path),
    )


def iter_transcript_paths(directory: Path) -> list[Path]:
    """All call-*.md files, sorted numerically by call id (not lexicographically)."""

    def _call_num(p: Path) -> int:
        m = re.search(r"(\d+)", p.stem)
        return int(m.group(1)) if m else 0

    return sorted(directory.glob("call-*.md"), key=_call_num)


def load_transcripts(directory: Path) -> list[Transcript]:
    """Parse every transcript in `directory`. Raises on the first bad file --
    used by tests/tools that want fail-fast behavior. The orchestrator does
    NOT use this; it parses file-by-file so one bad transcript can't take
    down the batch (see pipeline/orchestrator.py)."""

    return [parse_transcript(p) for p in iter_transcript_paths(directory)]


def internal_owner_name(transcript: Transcript) -> str:
    """Best-effort name of the internal call owner, for Slack routing."""

    for seg in transcript.participants_raw.split("\u00b7"):
        seg = seg.strip()
        m = _SEGMENT_RE.match(seg)
        if m and m.group(1) == "INTERNAL":
            name = m.group("rest").split(",")[0].strip()
            if name:
                return name
    for turn in transcript.turns:
        if turn.speaker is Speaker.INTERNAL:
            return turn.name
    return "unknown-owner"
