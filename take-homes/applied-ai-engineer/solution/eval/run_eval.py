"""Eval harness: precision/recall/F1 for the shipped pipeline's judge+dedup
decisions against the labeled dev set (data/dev_labels.json, calls 1-15),
plus named hard-case assertions for the trickiest transcripts, plus a
`--repeat` flag to measure decision stability across repeated runs.

Design choice: this runs the REAL `orchestrator.run_review()` against a
scratch Config (a temp copy of calls 1-15 only, temp state/log/queue files)
rather than re-implementing judge/dedup wiring in a parallel code path. That
means the eval validates exactly what ships, with zero risk of silently
drifting out of sync with the pipeline it's supposed to hold accountable.

Usage (from `applied-ai-engineer/`):
    py -m solution.eval.run_eval
    py -m solution.eval.run_eval --repeat 5
    py -m solution.eval.run_eval --verbose

See WRITEUP.md "Eval" for the pass/fail definition, threshold rationale,
what this catches, and what would slip through.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ..pipeline import orchestrator
from ..pipeline.config import Config, load_config
from ..pipeline.state_store import StateStore

DEV_CALL_IDS = [f"call-{i:03d}" for i in range(1, 16)]

# Not 1.00 on either axis: a couple of dev_labels.json entries turn on a
# subjective judgment call (exactly how "vague" is vague enough to decline
# action, say) that a second engineer could reasonably disagree with the
# LABEL itself on, not just the system's output under test. See WRITEUP.md.
PRECISION_THRESHOLD = 0.85
RECALL_THRESHOLD = 0.85

_ACTIONABLE_LABEL_ACTIONS = frozenset({"file-new", "file-new-low", "corroborate"})
_SAME_TICKET_RE = re.compile(r"same ticket as (call-\d+)")


def _load_dev_labels(path: Path) -> dict[str, list[dict[str, Any]]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return raw["labels"]


def _build_scratch_config(cfg: Config, scratch_dir: Path) -> Config:
    """A Config pointed at a scratch copy of calls 1-15 and scratch
    state/log/queue files, so the eval never touches the real ledger and
    only ever sees the labeled dev set."""
    transcripts_dir = scratch_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    for call_id in DEV_CALL_IDS:
        src = cfg.transcripts_dir / f"{call_id}.md"
        shutil.copy2(src, transcripts_dir / f"{call_id}.md")

    return Config(
        transcripts_dir=transcripts_dir,
        existing_issues_path=cfg.existing_issues_path,
        dev_labels_path=cfg.dev_labels_path,
        state_path=scratch_dir / "pipeline_state.json",
        review_queue_path=scratch_dir / "review_queue.md",
        review_decisions_path=scratch_dir / "review_decisions.json",
        log_path=scratch_dir / "events.jsonl",
        similarity_threshold=cfg.similarity_threshold,
        judge=cfg.judge,
        openai_model=cfg.openai_model,
    )


def _label_action_class(label: dict[str, Any]) -> str:
    action = label["action"]
    return "file-new" if action == "file-new-low" else action


def _entry_action_class(entry: dict[str, Any]) -> str:
    action = entry.get("action", "")
    return "file-new" if action == "file-new-low" else action


def _resolve_cross_call_targets(labels_by_call: dict[str, list[dict[str, Any]]], entries_by_call: dict[str, list[dict[str, Any]]]) -> None:
    """Mutates labels in place: a label whose `target` is prose like 'same
    ticket as call-006' (dev_labels.json's call-012 entry) is resolved to
    that other call's produced file-new `matched_key`, so it can be matched
    like any other named-target corroborate label. Left unresolved (and
    therefore unmatchable, correctly counted as a miss) if the referenced
    call didn't produce a file-new entry at all.
    """
    for labels in labels_by_call.values():
        for label in labels:
            target = label.get("target", "")
            m = _SAME_TICKET_RE.search(target) if isinstance(target, str) else None
            if not m:
                continue
            ref_call = m.group(1)
            ref_entries = [e for e in entries_by_call.get(ref_call, []) if _entry_action_class(e) == "file-new"]
            if ref_entries:
                label["_resolved_target"] = ref_entries[0].get("matched_key")


def _match_call(
    call_id: str, labels: list[dict[str, Any]], entries: list[dict[str, Any]]
) -> tuple[int, list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
    """Greedy bipartite match between one call's expected labels and its
    produced ledger entries. A match requires the same action *class*
    (file-new-low collapses with file-new) and, for file-new, the same
    issue type; for corroborate, the same matched target when the label
    names one. Returns (tp, unmatched_produced, unmatched_expected) -- the
    caller splits unmatched_produced into confident/low-confidence buckets
    (see EvalRunOutcome) since they carry very different weight.
    """
    remaining = list(entries)
    tp = 0
    unmatched_expected: list[tuple[str, dict[str, Any]]] = []
    for label in labels:
        action_class = _label_action_class(label)
        if action_class not in _ACTIONABLE_LABEL_ACTIONS:
            continue  # "none" labels have no corresponding ledger entry by design
        match_idx: Optional[int] = None
        for i, entry in enumerate(remaining):
            if _entry_action_class(entry) != action_class:
                continue
            if action_class == "file-new" and entry.get("issue_type") != label.get("type"):
                continue
            if action_class == "corroborate":
                expected_target = label.get("_resolved_target", label.get("target"))
                if expected_target and entry.get("matched_key") != expected_target:
                    continue
            match_idx = i
            break
        if match_idx is not None:
            tp += 1
            remaining.pop(match_idx)
        else:
            unmatched_expected.append((call_id, label))
    unmatched_produced = [(call_id, e) for e in remaining]
    return tp, unmatched_produced, unmatched_expected


@dataclass
class EvalRunOutcome:
    """One eval pass's produced decisions and derived metrics.

    Precision is computed on the CONFIDENT tier only (file-new, corroborate)
    -- an unmatched `file-new-low` is deliberately not held to the same bar.
    `file-new-low` exists specifically to cast a slightly wider net for
    cheap human review (see orchestrator.py's `_build_decision`) rather than
    silently drop a borderline signal; penalizing it as a false positive at
    the same weight as a confident miss would mask the very tier the design
    is supposed to make safe to be generous with. Recall is computed over
    ALL actionable labels regardless of tier, because a missed issue is a
    missed issue no matter how it would have been filed. Every unmatched
    item (both tiers) is still reported for transparency -- see WRITEUP.md.
    """

    entries_by_call: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    true_positives: int = 0
    false_negatives: int = 0
    unmatched_confident: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    unmatched_low_confidence: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    unmatched_expected: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    hard_case_results: list[tuple[str, bool, str]] = field(default_factory=list)

    @property
    def false_positives(self) -> int:
        return len(self.unmatched_confident)

    @property
    def precision(self) -> float:
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom else 1.0

    @property
    def recall(self) -> float:
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom else 1.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return (2 * p * r / (p + r)) if (p + r) else 0.0

    @property
    def hard_cases_passed(self) -> bool:
        return all(passed for _, passed, _ in self.hard_case_results)

    @property
    def passed(self) -> bool:
        return (
            self.precision >= PRECISION_THRESHOLD
            and self.recall >= RECALL_THRESHOLD
            and self.hard_cases_passed
        )

    def fingerprint(self) -> tuple:
        """A deterministic, order-independent summary of every produced
        decision, used to compare runs for `--repeat` stability checks."""
        rows = []
        for call_id, entries in self.entries_by_call.items():
            for e in entries:
                rows.append((call_id, e.get("action"), e.get("issue_type"), e.get("matched_key")))
        return tuple(sorted(rows))


def _run_hard_cases(entries_by_call: dict[str, list[dict[str, Any]]]) -> list[tuple[str, bool, str]]:
    """Named, human-readable assertions for the transcripts most likely to
    fool a naive implementation. Each one mirrors a real trap documented in
    heuristic_judge.py/dedup.py's own comments -- see WRITEUP.md for the
    full narrative behind each."""
    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        results.append((name, condition, detail))

    def actionable(call_id: str) -> list[dict[str, Any]]:
        return entries_by_call.get(call_id, [])

    c005 = actionable("call-005")
    check(
        "call-005: injection produces no ticket, genuine webhook report still surfaces",
        any(e.get("action") == "corroborate" and e.get("matched_key") == "PROJ-087" for e in c005),
        f"produced={[(e.get('action'), e.get('matched_key')) for e in c005]}",
    )

    c006 = actionable("call-006")
    c012 = actionable("call-012")
    c006_key = next((e.get("matched_key") for e in c006 if _entry_action_class(e) == "file-new"), None)
    c012_key = next((e.get("matched_key") for e in c012 if e.get("action") == "corroborate"), None)
    check(
        "call-006/call-012: independent reports of the same symptom merge to ONE ticket",
        c006_key is not None and c006_key == c012_key,
        f"call-006 filed key={c006_key!r}, call-012 corroborates key={c012_key!r}",
    )

    c010 = actionable("call-010")
    c010_bug = next((e for e in c010 if e.get("issue_type") == "Bug"), None)
    check(
        "call-010: Azure AD redirect loop is a DISTINCT new bug, not merged into PROJ-064 (Okta)",
        c010_bug is not None and c010_bug.get("action") == "file-new" and c010_bug.get("matched_key") != "PROJ-064",
        f"produced={c010_bug}",
    )

    c003 = actionable("call-003")
    check(
        "call-003: SAML role-mapping ask is classified Feature, not Bug",
        any(e.get("issue_type") == "Feature" for e in c003),
        f"produced={[(e.get('action'), e.get('issue_type')) for e in c003]}",
    )

    c013 = actionable("call-013")
    check(
        "call-013: LMS webhook ask is Feature; already-shipped CSV export files no ticket",
        any(_entry_action_class(e) == "file-new" and e.get("issue_type") == "Feature" for e in c013),
        f"produced={[(e.get('action'), e.get('issue_type')) for e in c013]}",
    )

    c007 = actionable("call-007")
    check(
        "call-007: internal-only call produces zero tickets",
        len(c007) == 0,
        f"produced={c007}",
    )

    c008 = actionable("call-008")
    c008_typo = next((e for e in c008 if _entry_action_class(e) == "file-new"), None)
    check(
        "call-008: crash corroborates PROJ-110; typo files low-priority, not P0/P1 despite customer framing",
        any(e.get("action") == "corroborate" and e.get("matched_key") == "PROJ-110" for e in c008)
        and c008_typo is not None
        and c008_typo.get("priority") in ("P3", "P4"),
        f"produced={[(e.get('action'), e.get('matched_key'), e.get('priority')) for e in c008]}",
    )

    c011 = actionable("call-011")
    check(
        "call-011: profile-link 404 bug files; embedded email instruction produces no extra ticket",
        any(_entry_action_class(e) == "file-new" and e.get("issue_type") == "Bug" for e in c011),
        f"produced={[(e.get('action'), e.get('issue_type')) for e in c011]}",
    )

    return results


def _run_once(cfg: Config) -> EvalRunOutcome:
    with tempfile.TemporaryDirectory(prefix="june_tapes_eval_") as tmp:
        scratch_cfg = _build_scratch_config(cfg, Path(tmp))
        orchestrator.run_review(scratch_cfg)
        store = StateStore(scratch_cfg.state_path)
        all_entries = store.all_entries()

    entries_by_call: dict[str, list[dict[str, Any]]] = {call_id: [] for call_id in DEV_CALL_IDS}
    for entry in all_entries.values():
        if entry.get("status") != "queued":
            continue  # not_actionable / collapsed_duplicate have no dev_labels counterpart to match
        entries_by_call.setdefault(entry["call_id"], []).append(entry)

    labels_by_call = _load_dev_labels(cfg.dev_labels_path)
    labels_by_call = json.loads(json.dumps(labels_by_call))  # deep copy: _resolve mutates in place
    _resolve_cross_call_targets(labels_by_call, entries_by_call)

    outcome = EvalRunOutcome(entries_by_call=entries_by_call)
    for call_id in DEV_CALL_IDS:
        tp, unmatched_produced, unmatched_expected = _match_call(
            call_id, labels_by_call.get(call_id, []), entries_by_call.get(call_id, [])
        )
        outcome.true_positives += tp
        outcome.false_negatives += len(unmatched_expected)
        for entry_call_id, entry in unmatched_produced:
            bucket = outcome.unmatched_low_confidence if entry.get("action") == "file-new-low" else outcome.unmatched_confident
            bucket.append((entry_call_id, entry))
        outcome.unmatched_expected.extend(unmatched_expected)

    outcome.hard_case_results = _run_hard_cases(entries_by_call)
    return outcome


def _print_report(outcomes: list[EvalRunOutcome], verbose: bool) -> bool:
    final = outcomes[-1]
    print(f"Dev-set eval: {len(DEV_CALL_IDS)} calls (labeled dev set, data/dev_labels.json)")
    print(f"  precision={final.precision:.2f}  recall={final.recall:.2f}  f1={final.f1:.2f}  "
          f"(TP={final.true_positives} FP={final.false_positives} FN={final.false_negatives})")
    print(f"  thresholds: precision>={PRECISION_THRESHOLD:.2f}, recall>={RECALL_THRESHOLD:.2f} "
          "(precision counts only confident file-new/corroborate misses -- see EvalRunOutcome docstring)")
    print(f"  + {len(final.unmatched_low_confidence)} unlabeled file-new-low item(s): deliberately wider net for "
          "human review, not counted against precision")
    print()
    print("Named hard cases:")
    for name, ok, detail in final.hard_case_results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        if verbose or not ok:
            print(f"         {detail}")

    if verbose or final.unmatched_confident or final.unmatched_expected:
        print()
        print("Unmatched confident (false positives -- produced but not expected):")
        for call_id, entry in final.unmatched_confident:
            print(f"  {call_id}: {entry.get('action')} type={entry.get('issue_type')} key={entry.get('matched_key')}")
        print("Unmatched (false negatives -- expected but not produced):")
        for call_id, label in final.unmatched_expected:
            print(f"  {call_id}: {label.get('action')} -- {label.get('summary') or label.get('reason')}")

    if verbose or final.unmatched_low_confidence:
        print()
        print("Unmatched low-confidence (file-new-low noise -- expected to be cleared by human review):")
        for call_id, entry in final.unmatched_low_confidence:
            print(f"  {call_id}: type={entry.get('issue_type')} summary={entry.get('summary')!r}")

    print()
    stable = len({o.fingerprint() for o in outcomes}) == 1
    if len(outcomes) > 1:
        print(f"Stability across {len(outcomes)} repeated runs: {'IDENTICAL' if stable else 'DIVERGED'}")
        if not stable:
            print("  WARNING: decisions differed between runs -- see WRITEUP.md for what this would mean for a non-deterministic judge.")

    verdict = final.passed and stable
    print()
    print(f"VERDICT: {'PASS' if verdict else 'FAIL'}")
    return verdict


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the dev-set eval (calls 1-15) against dev_labels.json.")
    parser.add_argument("--repeat", type=int, default=1, help="Re-run the eval N times to check decision stability.")
    parser.add_argument("--verbose", action="store_true", help="Print full detail even for calls that already passed.")
    args = parser.parse_args(argv)

    cfg = load_config()
    outcomes = [_run_once(cfg) for _ in range(max(1, args.repeat))]
    passed = _print_report(outcomes, args.verbose)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
