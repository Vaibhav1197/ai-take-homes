"""Heuristic-engine knowledge base: keyword/phrase lists used by
`heuristic_judge.py` to approximate the judgment an LLM would make.

Everything here is intentionally simple, inspectable, and testable -- the
point of the heuristic engine is that a reviewer can read this file and know
exactly why a call was flagged. See WRITEUP.md "AI placement" for why this
exists alongside (not instead of) the LLM judge in llm_judge.py.

All phrase matching is case-insensitive substring matching against
normalized turn text, deliberately simple. Order of checks in
heuristic_judge.py matters more than any single list here.
"""
from __future__ import annotations

# --- Hard override: never write anything for a thread touching these. -----
# Prompt-injection / "instructions to the notetaker" embedded in speech or in
# quoted data (emails, tickets, etc). Detected -> logged loudly, zero writes,
# and the rest of the call is still processed normally.
INJECTION_PHRASES = (
    "system instruction",
    "ignore your previous instructions",
    "ignore previous instructions",
    "ignore prior instructions",
    "ignore all previous instructions",
    "disregard prior filtering",
    "disregard your instructions",
    "note to automated assistants",
    "to any ai reading this",
    "to any llm",
    "dear ai",
    "dear bot",
    "automated assistants processing this message",
    "file a p0 ticket titled",
    "wire transfer approval",
    "approve the wire transfer",
    "post \"approved\"",
    "notify the payroll",
    "notify payroll",
    "compensation adjustment",
)

# --- Suppression signals (each maps to action=none if triggered). ---------

RETRACTION_PHRASES = (
    "don't file", "do not file", "don't bother", "not a real complaint",
    "not going to pretend", "no need to re-report", "no need to", "not a big deal",
    "not insisting", "never mind", "not worth chasing", "not worth a ticket",
    "i'm not asking", "im not asking", "don't worry about it", "forget i said",
    "more of a preference", "it's fine honestly", "my eyes",
    "a me problem", "don't you dare file", "spare product that one", "not going to pretend it's a bug",
)

# Common idiom ("that's a feature, not a bug") that contains the literal
# word "bug" but means the opposite of a bug report. Checked separately in
# heuristic_judge._bug_keyword_hits so it never counts as bug signal, and
# deliberately NOT modeled as a RETRACTION phrase (a retraction requires a
# real candidate to exist first; this idiom should stop one from ever being
# created).
BUG_IDIOM_NEGATION_PATTERNS = (
    r"feature[,]?\s+(?:and\s+)?not\s+a\s+bug",
    r"not\s+a\s+bug[,]?\s+(?:it'?s\s+)?(?:and\s+)?a\s+feature",
    r"not\s+a\s+(?:real\s+)?bug\s+report",
)

# "don't file" / "do not file" is a strong, deliberate retraction signal --
# *except* when it's part of a general statement about a population's
# behavior ("warehouse folks don't file tickets") rather than an instruction
# about the thing just discussed. Checked in heuristic_judge._retraction_hits.
RETRACTION_NEGATION_PATTERNS = (
    r"don'?t file tickets",
    r"do not file tickets",
    r"doesn'?t file tickets",
)

RESOLVED_ON_CALL_PHRASES = (
    "turned out to be", "was user error", "my bad", "that explains it",
    "resolved on the call", "already fixed", "that fixed it", "that was it",
    "root cause was", "false alarm", "resolved itself", "non-issue",
    "that solved it", "already resolved", "clock skew", "already attributed",
    "you're already attached", "youre already attached",
    "no need to re-report",
)

SHIPPED_PHRASES = (
    "already shipped", "shipped in", "that's already available", "thats already available",
    "already live", "that exists today", "you can already", "shipped recently",
    "already ships", "released last", "that shipped", "just shipped", "was shipped",
)

HEARSAY_PHRASES = (
    "heard at a conference", "someone mentioned", "secondhand", "second-hand",
    "i haven't seen it myself", "havent seen it myself", "allegedly",
    "a friend at another company", "i can't confirm", "cant confirm",
    "not first-hand", "not firsthand", "rumor", "rumour", "someone told me",
    "conference hearsay", "no first-hand experience",
)

VAGUE_PHRASES = (
    "kind of slow", "a bit slow", "not sure when", "hard to say",
    "can't pin down", "cant pin down", "no particular pattern", "in general it seems",
    "once in a while", "sometimes it feels", "vague", "hard to describe",
    "not worth chasing", "declines to substantiate",
)

COSMETIC_PHRASES = (
    "font", "color scheme", "colour scheme", "purple", "looks unprofessional",
    "blurry", "ugly", "prettier", "nicer looking", "cosmetic", "aesthetic",
    "doesn't look great", "doesnt look great", "would look better", "squint",
    "typo", "misspell",
)

NONPRODUCT_PHRASES = (
    "competitor", "competing vendor", "pitched us", "pitched by another vendor",
    "custom report just for us", "one-off report",
    "renewal timeline", "procurement",
    "pricing question", "contract terms", "relationship intel", "custom frontline reporting",
)

# --- Positive signal keywords (drive bug-vs-feature + whether to surface). -

BUG_KEYWORDS = (
    "bug", "broken", "doesn't work", "doesnt work", "does not work", "fails",
    "failing", "failure", "crash", "crashes", "crashing", "error", "wrong",
    "incorrect", "contradicts", "mismatch", "disagrees", "duplicate",
    "duplicates", "delivered twice", "shows up twice", "two deliveries",
    "truncat", "cut off", "cuts off", "404", "blank screen",
    "stuck", "stops working", "won't open", "wont open", "won't load",
    "freeze", "freezes", "hangs", "stale", "delayed", "delay", "expires early",
    "logs out", "redirect loop", "loop", "glitch", "defect", "malfunction",
    "typo", "misspell", "empty results",
)

# Ambiguous bug words that can describe a flawed MANUAL process or general
# human-error risk just as easily as an actual software defect -- e.g. "wrong
# role", "error-prone", "fails the control" all show up while a customer
# motivates a FEATURE request by describing the pain of today's manual
# workaround (see call-003's SAML role-mapping ask, call-013's LMS webhook
# ask). Excluded from the bug-vs-feature tie-break in heuristic_judge.py so
# that pain-point framing doesn't get miscounted as "a bug was reported" --
# but these still count normally everywhere else (suppression checks,
# keyword_hits, raw_score).
SOFT_BUG_KEYWORDS = frozenset({"fails", "failing", "failure", "error", "wrong"})

FEATURE_KEYWORDS = (
    "feature request", "would be great if", "would love", "wish", "can you add",
    "could you add", "ability to", "able to", "want to be able", "request for",
    "requesting", "need the ability", "would help if", "any way to",
    "is there a way to", "would it be possible", "we'd like", "wed like",
    "we would like", "on the roadmap", "export api", "webhook event",
    "automatic", "auto-assign", "integration with", "support for",
    "would benefit from", "put it on the list", "idempotency key", "idempotency keys",
    "webhook", "programmatic access", "api endpoint", "what i need is",
)

# --- Business-impact / severity signals. -----------------------------------

BUSINESS_DRIVER_PHRASES = (
    "soc 2", "soc2", "audit", "compliance", "cfo", "finance report",
    "escalat", "renewal", "sox ", "hipaa", "gdpr", "security review",
    "board", "leadership review",
)

SECURITY_OR_DATA_LOSS_PHRASES = (
    "data loss", "security breach", "unauthorized", "breach", "exposed data",
    "leaked", "pii", "personally identifiable",
)

NO_WORKAROUND_PHRASES = (
    "no workaround", "force-quit", "force quit", "locked out", "can't get in",
    "cant get in", "stuck on", "blocked from", "nothing i can do",
)

# Words the CUSTOMER uses to dramatize urgency. Deliberately EXCLUDED from
# every scoring list above -- severity is computed from objective impact
# signals only, never from the reporter's own framing. See
# `heuristic_judge.estimate_priority` and
# tests/test_heuristic_judge.py::test_dramatic_framing_does_not_inflate_priority.
CUSTOMER_DRAMA_WORDS_IGNORED_BY_DESIGN = (
    "urgent", "p0", "emergency", "existential", "asap", "brand emergency",
    "critical", "immediately",
)

TOPIC_BREAK_MARKERS = (
    "one real thing", "actual business", "the actual bug", "box two",
    "second thing", "different topic", "one more thing", "anything else",
    "moving on", "hold that thought", "before i forget", "quick tangent",
    "unrelated but", "while i have you", "one more before", "another thing",
    "last thing", "first thing", "housekeeping first", "actual problem",
    "anything not working", "while i remember", "anything on your list",
    "what else", "anything else on", "is there anything else",
)
