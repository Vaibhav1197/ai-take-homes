"""Deterministic, keyword/rule-based `IssueJudge` implementation.

This is the *shipped default* -- see WRITEUP.md "AI placement" for the full
rationale. Short version: classification here needs to be auditable, free,
instant, and 100% reproducible for the idempotency/reliability requirements
in the assignment, and the labeled dev set (data/dev_labels.json) is small
and pattern-shaped enough that a rule engine tuned against it is a
legitimate, inspectable stand-in for a model call. `llm_judge.py` implements
the exact same interface for teams that want a real model in this seat
instead (e.g. to generalize beyond the 140 sample calls without hand-tuning
more keyword lists).

Two-level segmentation, chosen after tracing real transcripts by hand:
  1. Coarse "blocks" on discourse-marker boundaries ("second thing", "one
     more thing", ...) -- an outer fence a candidate's context window can
     never cross, even if the finer clustering below misjudges a gap.
  2. Within each block, external turns that actually contain a bug/feature
     keyword are clustered by proximity (nearby signal turns = one
     candidate), and the suppression-phrase checks (retracted / resolved /
     hearsay / ...) are scoped to a small window around *that specific
     cluster* -- not the whole block. This matters a lot in practice: real
     calls often wrap a genuine bug report in many turns of pleasantries
     that can incidentally contain a suppression-flavored word (e.g. a much
     later "budget noise?" aside must not retroactively suppress an earlier,
     unrelated bug report just because they landed in the same coarse
     block).
"""
from __future__ import annotations

import re

from .keywords import (
    BUG_IDIOM_NEGATION_PATTERNS,
    BUG_KEYWORDS,
    BUSINESS_DRIVER_PHRASES,
    COSMETIC_PHRASES,
    FEATURE_KEYWORDS,
    HEARSAY_PHRASES,
    INJECTION_PHRASES,
    NONPRODUCT_PHRASES,
    NO_WORKAROUND_PHRASES,
    RESOLVED_ON_CALL_PHRASES,
    RETRACTION_NEGATION_PATTERNS,
    RETRACTION_PHRASES,
    SECURITY_OR_DATA_LOSS_PHRASES,
    SHIPPED_PHRASES,
    SOFT_BUG_KEYWORDS,
    TOPIC_BREAK_MARKERS,
    VAGUE_PHRASES,
)
from .models import Candidate, Speaker, Transcript, Turn
from .text_utils import extract_max_impact_count, find_matches, normalize_whitespace

_QUOTE_RE = re.compile(r"[\"'\u2018\u2019\u201c\u201d][^\"'\u2018\u2019\u201c\u201d]{2,60}[\"'\u2018\u2019\u201c\u201d]")
_DIGIT_RE = re.compile(r"\d")
_BUG_IDIOM_NEGATION_RE = re.compile("|".join(BUG_IDIOM_NEGATION_PATTERNS))
_RETRACTION_NEGATION_RE = re.compile("|".join(RETRACTION_NEGATION_PATTERNS))

_TITLE_MAX_LEN = 100
_CLUSTER_MAX_GAP = 6  # signal turns within this many turns of each other merge into one candidate
_CONTEXT_RADIUS_BACK = 1  # turns of leading context (the internal question that prompted the report)
_CONTEXT_RADIUS_FWD = 5  # turns of trailing context -- resolution/suppression language usually lands
# a few turns *after* the report itself (a wrap-up recap, a "turned out to be..." a beat later), so
# this is deliberately wider than the leading radius. See WRITEUP.md for the real transcript trace
# that motivated this asymmetry (call-003's clock-skew resolution lands 5 turns after the report).
_INJECTION_CONTEXT_RADIUS = 2  # kept small and symmetric: injection detection is higher-stakes and
# already validated at this radius; no evidence it needs the same widening as genuine issue reports.
_NARROW_SCAN_RADIUS_FWD = 2  # nonproduct/cosmetic/vague/hearsay checks use this tighter forward
# radius even though the candidate's own window is wider. Those are judgments about the content of
# the turn itself, not delayed confirmations, so a wide radius mostly just risks catching an
# unrelated aside later in the same block (call-014: "what's the procurement timeline" lands 5
# turns after a bug report that was explicitly wrapped up as "I'll keep it in the product lane" --
# scanning that far for NONPRODUCT_PHRASES would wrongly suppress a real, high-priority bug).


def _bug_keyword_hits(text_l: str) -> list[str]:
    """BUG_KEYWORDS matches, with one deliberate carve-out: the idiom "that's
    a feature, not a bug" contains the literal word "bug" but means the
    opposite of a bug report. Seen twice in the sample transcripts (call-004,
    call-010) as a red herring unrelated to the actual issue being discussed.
    """
    hits = find_matches(text_l, BUG_KEYWORDS)
    if "bug" in hits and _BUG_IDIOM_NEGATION_RE.search(text_l):
        hits = [h for h in hits if h != "bug"]
    return hits


def _retraction_hits(text_l: str) -> list[str]:
    """RETRACTION_PHRASES matches, with one deliberate carve-out: "don't
    file"/"do not file" is a strong retraction signal on its own, but not
    when it's a general statement about a population's reporting habits
    ("warehouse folks don't file tickets") rather than an instruction about
    the issue just discussed. Seen in call-008 as a red herring.
    """
    hits = find_matches(text_l, RETRACTION_PHRASES)
    if _RETRACTION_NEGATION_RE.search(text_l):
        hits = [h for h in hits if h not in ("don't file", "do not file")]
    return hits


def _classify_signal_type(bug_hits: list[str], feat_hits: list[str]) -> str:
    """bug vs feature, weighted so SOFT_BUG_KEYWORDS can't single-handedly
    outvote a genuine feature ask. Customers routinely motivate a feature
    request by describing what's wrong with today's manual process ("it's
    error-prone", "someone gets the wrong role") -- that pain-point framing
    uses bug-flavored words while the ask itself is unambiguously a feature
    (call-003's SAML role mapping, call-013's LMS webhook both did exactly
    this and were misclassified as "bug" before this carve-out). Words that
    almost always mean an actual software defect regardless of context
    ("crash", "404", "duplicate", "stuck", ...) still count at full weight.
    """
    strong_bug_hits = [h for h in bug_hits if h not in SOFT_BUG_KEYWORDS]
    return "bug" if len(strong_bug_hits) >= len(feat_hits) else "feature"


def _segment_blocks(turns: tuple[Turn, ...]) -> list[tuple[int, int]]:
    """Split a call into topic spans on discourse-marker boundaries.

    A marker turn *starts* the new block (it's introducing the next topic),
    so the previous block ends the turn before it. Falls back to one block
    covering the whole call when no markers are present. This is an outer
    fence only -- see module docstring.

    Only EXTERNAL turns are checked. Found via the eval harness (call-008):
    TOPIC_BREAK_MARKERS includes wrap-up prompts like "anything else..." /
    "while I have you" that the INTERNAL rep routinely says when closing out
    a topic ("Anything else while I have you, or is that the two?"). If the
    customer's very next turn is just a short confirmation ("That's the two.
    Fix the crashing app before the typo, in case that needed saying") --
    itself still about the topic just discussed, not a new one -- treating
    the rep's question as a fence stranded that confirmation in its own
    block, split off from the report it was closing out, and it surfaced as
    a second, low-content, spurious candidate for the same issue. A customer
    actually introducing a new topic ("one more thing", "actually, unrelated
    but...") is a much stronger signal than the rep merely asking whether
    there's more.
    """
    if not turns:
        return []
    boundaries = [0]
    for i, t in enumerate(turns):
        if i == 0:
            continue
        if t.speaker is Speaker.EXTERNAL and find_matches(t.text.lower(), TOPIC_BREAK_MARKERS) and i != boundaries[-1]:
            boundaries.append(i)
    boundaries.append(len(turns))
    return [(boundaries[k], boundaries[k + 1] - 1) for k in range(len(boundaries) - 1)]


def _signal_indices(turns: tuple[Turn, ...], start: int, end: int) -> tuple[list[int], list[int]]:
    """Absolute indices (within [start, end]) of external turns carrying a
    bug/feature keyword, and separately, of external turns carrying *only*
    an injection phrase (no bug/feature keyword) -- kept for observability
    even when there's no other signal in that turn."""
    signal: list[int] = []
    injection_only: list[int] = []
    for i in range(start, end + 1):
        t = turns[i]
        if t.speaker is not Speaker.EXTERNAL:
            continue
        text_l = t.text.lower()
        has_bug_or_feature = bool(_bug_keyword_hits(text_l)) or bool(find_matches(text_l, FEATURE_KEYWORDS))
        if has_bug_or_feature:
            signal.append(i)
        elif find_matches(text_l, INJECTION_PHRASES):
            injection_only.append(i)
    return signal, injection_only


def _cluster(indices: list[int], max_gap: int) -> list[list[int]]:
    if not indices:
        return []
    clusters = [[indices[0]]]
    for idx in indices[1:]:
        if idx - clusters[-1][-1] <= max_gap + 1:
            clusters[-1].append(idx)
        else:
            clusters.append([idx])
    return clusters


def _ranges_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return not (a[1] < b[0] or a[0] > b[1])


def _has_concrete_specifics(ext_text: str, ext_text_l: str) -> bool:
    """Objective grounding check: a number, a quoted value, or an extractable
    affected-population count -- something a human could go verify."""
    if extract_max_impact_count(ext_text_l) is not None:
        return True
    if _DIGIT_RE.search(ext_text):
        return True
    if _QUOTE_RE.search(ext_text):
        return True
    return False


def _has_factual_defect(ext_text_l: str) -> bool:
    """Distinguishes a concrete cosmetic defect (real typo, a wrong value)
    from a subjective aesthetic preference ("looks unprofessional"). Note:
    deliberately does NOT treat "any quoted substring" as proof of a factual
    defect -- customers quote plenty of purely illustrative examples (e.g.
    a truncated label like "Editorial Stra...") that are not factual errors.
    """
    if "typo" in ext_text_l or "misspell" in ext_text_l:
        return True
    if re.search(r"\b\d+\b[^.]{0,20}\bvs\b[^.]{0,20}\d+", ext_text_l):
        return True
    return False


def _turn_signal_score(turn: Turn) -> int:
    text_l = turn.text.lower()
    return len(_bug_keyword_hits(text_l)) + len(find_matches(text_l, FEATURE_KEYWORDS))


def _build_snippet(ext_turns: list[Turn]) -> str:
    """Verbatim, speaker-attributed quote of every external turn in the
    window -- never a paraphrase. This is what actually gets linked into the
    Jira/Slack payloads as the evidence a reviewer can check against the
    source transcript."""
    return "\n".join(f"[EXTERNAL] {t.name}: {t.text}" for t in ext_turns)


def _draft_title(primary_text: str) -> str:
    """Deliberately dumb truncation, not a rewrite -- see module docstring
    on why the heuristic engine never paraphrases customer speech. A real
    LLMJudge is free to draft a cleaner imperative title instead; that's a
    documented, intentional capability difference between the two judges."""
    t = normalize_whitespace(primary_text)
    if len(t) > _TITLE_MAX_LEN:
        head = t[: _TITLE_MAX_LEN - 3]
        if " " in head:
            head = head.rsplit(" ", 1)[0]
        t = head + "..."
    return t


def estimate_priority(full_text_l: str, flags: list[str]) -> tuple[str, bool]:
    """Priority from *objective* impact signals only -- deliberately never
    reads the customer's own urgency framing (see
    keywords.CUSTOMER_DRAMA_WORDS_IGNORED_BY_DESIGN). Never returns P0
    outright without flagging for a human look; a human always makes the
    final call on true P0s/P1s.
    """
    score = 0
    if find_matches(full_text_l, SECURITY_OR_DATA_LOSS_PHRASES):
        score += 3
    if find_matches(full_text_l, NO_WORKAROUND_PHRASES):
        score += 2
    if find_matches(full_text_l, BUSINESS_DRIVER_PHRASES):
        score += 1
    impact = extract_max_impact_count(full_text_l)
    if impact is not None:
        if impact >= 100:
            score += 2
        elif impact >= 10:
            score += 1
    if "cosmetic-factual-low-severity" in flags:
        score -= 3

    if score <= -1:
        priority = "P4"
    elif score == 0:
        priority = "P3"
    elif score <= 2:
        priority = "P2"
    else:
        priority = "P1"
    needs_human_priority_call = score >= 5
    return priority, needs_human_priority_call


class HeuristicJudge:
    """Default `IssueJudge`: deterministic, explainable, zero network calls."""

    def find_candidates(self, transcript: Transcript) -> list[Candidate]:
        if not transcript.has_external_participant:
            return []

        turns = transcript.turns
        candidates: list[Candidate] = []

        for start, end in _segment_blocks(turns):
            signal_idx, injection_only_idx = _signal_indices(turns, start, end)
            signal_clusters = _cluster(signal_idx, _CLUSTER_MAX_GAP)
            injection_clusters = _cluster(injection_only_idx, 2)

            covered_ranges: list[tuple[int, int]] = []
            for cluster in signal_clusters:
                lo = max(start, min(cluster) - _CONTEXT_RADIUS_BACK)
                hi = min(end, max(cluster) + _CONTEXT_RADIUS_FWD)
                narrow_hi = min(end, max(cluster) + _NARROW_SCAN_RADIUS_FWD)
                covered_ranges.append((lo, hi))
                candidates.append(self._build_candidate(transcript, turns, lo, hi, narrow_hi=narrow_hi))

            for cluster in injection_clusters:
                lo = max(start, min(cluster) - _INJECTION_CONTEXT_RADIUS)
                hi = min(end, max(cluster) + _INJECTION_CONTEXT_RADIUS)
                if any(_ranges_overlap((lo, hi), covered) for covered in covered_ranges):
                    continue  # already surfaced as part of a nearby bug/feature candidate
                candidates.append(self._build_candidate(transcript, turns, lo, hi, injection_only=True))

        return candidates

    def _build_candidate(
        self,
        transcript: Transcript,
        turns: tuple[Turn, ...],
        lo: int,
        hi: int,
        injection_only: bool = False,
        narrow_hi: int | None = None,
    ) -> Candidate:
        window_turns = turns[lo : hi + 1]
        ext_turns = [t for t in window_turns if t.speaker is Speaker.EXTERNAL]
        ext_text = " ".join(t.text for t in ext_turns)
        ext_text_l = ext_text.lower()
        full_text_l = " ".join(t.text for t in window_turns).lower()

        narrow_hi_eff = hi if narrow_hi is None else min(hi, narrow_hi)
        narrow_window_turns = turns[lo : narrow_hi_eff + 1]
        narrow_ext_text_l = " ".join(
            t.text for t in narrow_window_turns if t.speaker is Speaker.EXTERNAL
        ).lower()
        narrow_full_text_l = " ".join(t.text for t in narrow_window_turns).lower()

        bug_hits = _bug_keyword_hits(ext_text_l)
        feat_hits = find_matches(ext_text_l, FEATURE_KEYWORDS)

        flags: list[str] = []
        suppressed = False
        reason = ""

        injection_hits = find_matches(full_text_l, INJECTION_PHRASES)
        retraction_hits = _retraction_hits(full_text_l)
        resolved_hits = find_matches(full_text_l, RESOLVED_ON_CALL_PHRASES)
        shipped_hits = find_matches(full_text_l, SHIPPED_PHRASES)
        hearsay_hits = find_matches(narrow_ext_text_l, HEARSAY_PHRASES)
        nonproduct_hits = find_matches(narrow_full_text_l, NONPRODUCT_PHRASES)
        cosmetic_hits = find_matches(narrow_ext_text_l, COSMETIC_PHRASES)
        vague_hits = find_matches(narrow_ext_text_l, VAGUE_PHRASES)
        has_specifics = _has_concrete_specifics(ext_text, ext_text_l)
        has_factual_defect = _has_factual_defect(ext_text_l)

        if injection_hits:
            flags.append("injection")
            suppressed = True
            reason = (
                f"prompt-injection / embedded instruction detected ({injection_hits[0]!r}); "
                "treated as transcript data, never as an instruction -- zero writes for this thread"
            )
        elif retraction_hits:
            flags.append("retraction")
            suppressed = True
            reason = f"customer explicitly retracted/waved off the concern ({retraction_hits[0]!r})"
        elif resolved_hits:
            flags.append("resolved-on-call")
            suppressed = True
            reason = f"resolved or already attributed/explained on the call itself ({resolved_hits[0]!r})"
        elif shipped_hits:
            flags.append("already-shipped")
            suppressed = True
            reason = f"functionality already shipped per the call ({shipped_hits[0]!r}); enablement, not a new ticket"
        elif hearsay_hits and not has_specifics:
            flags.append("hearsay")
            suppressed = True
            reason = f"secondhand/hearsay with no first-hand specifics ({hearsay_hits[0]!r})"
        elif nonproduct_hits:
            flags.append("nonproduct")
            suppressed = True
            reason = f"not a product-engineering matter ({nonproduct_hits[0]!r})"
        elif cosmetic_hits and not has_factual_defect:
            flags.append("cosmetic-subjective")
            suppressed = True
            reason = f"subjective aesthetic preference, no confirmed functional defect ({cosmetic_hits[0]!r})"
        elif vague_hits and not has_specifics:
            flags.append("vague")
            suppressed = True
            reason = f"no repro steps or specifics offered, declines to substantiate ({vague_hits[0]!r})"
        elif injection_only:
            # No suppression phrase and no bug/feature keyword either -- this
            # cluster exists purely because of an injection phrase spoken
            # with no other content. Still force-suppress: an injection
            # attempt is never actionable on its own.
            flags.append("injection-adjacent")
            suppressed = True
            reason = "no genuine bug/feature content in this span; flagged only due to nearby injection-style phrasing"

        if cosmetic_hits and has_factual_defect:
            flags.append("cosmetic-factual-low-severity")

        signal_type = _classify_signal_type(bug_hits, feat_hits)
        if ext_turns:
            primary_turn = max(ext_turns, key=_turn_signal_score)
        else:
            primary_turn = window_turns[0]
        priority, needs_human_priority_call = estimate_priority(full_text_l, flags)

        return Candidate(
            call_id=transcript.call_id,
            account=transcript.account,
            primary_turn_index=primary_turn.index,
            turn_span=(lo, hi),
            snippet=_build_snippet(ext_turns) if ext_turns else primary_turn.text,
            signal_type=signal_type,
            keyword_hits=list(dict.fromkeys(bug_hits + feat_hits)),
            raw_score=float(len(bug_hits) + len(feat_hits)),
            flags=flags,
            provisional_priority=priority,
            draft_title=_draft_title(primary_turn.text),
            suppressed=suppressed,
            suppression_reason=reason,
            needs_human_priority_call=needs_human_priority_call,
        )
