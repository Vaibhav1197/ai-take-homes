"""Small deterministic text-processing helpers shared by the judge and dedup
stages. Pure stdlib string/regex work -- no ML, no network. Kept separate
from heuristic_judge.py so the number/keyword parsing can be unit-tested on
its own.
"""
from __future__ import annotations

import re
from typing import Optional

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = frozenset(
    """
    a an the of to in on for and or but is are was were be been being this
    that these those it its their our your my his her we you i he she they
    with as at by from into about over under again further then once here
    there all any both each few more most other some such no nor not only
    own same so than too very can will just don should now do does did
    have has had having if because while when where why how what which who
    whom
    """.split()
)

_NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90, "dozen": 12, "dozens": 24,
}

_IMPACT_NOUNS = (
    "members", "member", "users", "user", "people", "drivers", "driver",
    "employees", "employee", "accounts", "account", "seats", "tickets",
    "associates", "customers",
)


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def significant_tokens(text: str) -> list[str]:
    return [t for t in tokenize(text) if t not in _STOPWORDS and len(t) > 2]


def find_matches(text_lower: str, phrases: tuple[str, ...]) -> list[str]:
    return [p for p in phrases if p in text_lower]


def _word_group_to_number(phrase: str) -> Optional[int]:
    phrase = phrase.strip().lower()
    if not phrase:
        return None
    if phrase.isdigit():
        return int(phrase)
    parts = [p for p in re.split(r"[\s-]+", phrase) if p and p != "and"]
    if not parts:
        return None
    total = 0
    current = 0
    matched_any = False
    for part in parts:
        if part == "hundred":
            current = (current or 1) * 100
            matched_any = True
        elif part == "thousand":
            total += (current or 1) * 1000
            current = 0
            matched_any = True
        elif part in _NUMBER_WORDS:
            current += _NUMBER_WORDS[part]
            matched_any = True
        else:
            return None
    total += current
    return total if matched_any else None


_IMPACT_WINDOW_RE = re.compile(
    r"(?P<amount>(?:\d{1,7})|(?:[a-z]+(?:[\s-][a-z]+){0,3}))\s+(?:%|percent\s+of\s+)?"
    r"(?:" + "|".join(_IMPACT_NOUNS) + r")\b"
)


def extract_max_impact_count(text_lower: str) -> Optional[int]:
    """Best-effort extraction of an affected-population size, e.g. '31
    members', 'thirty-one members', 'two thousand seasonal store associates'.
    Used only as a severity *nudge* -- never the sole basis for a decision.
    """

    best: Optional[int] = None
    for m in _IMPACT_WINDOW_RE.finditer(text_lower):
        n = _word_group_to_number(m.group("amount"))
        if n is not None and (best is None or n > best):
            best = n
    return best


def jaccard_similarity(a_tokens: set[str], b_tokens: set[str]) -> float:
    if not a_tokens or not b_tokens:
        return 0.0
    intersection = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)
    return intersection / union if union else 0.0
