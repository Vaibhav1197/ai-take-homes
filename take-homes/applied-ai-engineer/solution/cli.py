"""Command-line entry point.

    py -m solution review   # parse transcripts, judge + dedup, queue for human review
    py -m solution apply    # apply human-approved decisions: file tickets, send notifications

All actual configuration (paths, similarity threshold, judge selection) comes
from the environment via config.py -- see that module's docstring. This file
only parses the subcommand and prints a short human-readable summary; all the
real work happens in orchestrator.py, which is what's actually unit tested.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from .pipeline.config import load_config
from .pipeline.orchestrator import ApplyRunSummary, ReviewRunSummary, run_apply, run_review
from .pipeline.logging_utils import EventLogger, assess_health
from .pipeline.triage import run_triage


def _print_review_summary(summary: ReviewRunSummary, review_queue_path, review_decisions_path) -> None:
    print(f"Processed {summary.calls_processed} call(s), {summary.calls_failed} failed.")
    print(
        f"Found {summary.candidates_found} candidate(s): "
        f"{summary.queued_for_review} queued for review, "
        f"{summary.candidates_suppressed} suppressed, "
        f"{summary.not_actionable} not actionable (e.g. already shipped), "
        f"{summary.collapsed_duplicates} collapsed same-call duplicate(s), "
        f"{summary.skipped_already_processed} already processed in a prior run."
    )
    print(f"Already queued: {summary.already_queued}; outstanding queue by action: {summary.queue_by_action}")
    print(f"Review queue:      {review_queue_path}")
    print(f"Edit decisions in: {review_decisions_path}")


def _print_apply_summary(summary: ApplyRunSummary) -> None:
    print(
        f"Filed {summary.filed} new ticket(s), notified {summary.corroborated} corroboration(s), "
        f"{summary.rejected} rejected, {summary.failed} failed to apply."
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="solution", description="The June Tapes pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("review", help="Parse transcripts, judge + dedup, queue genuine issues for human review.")
    sub.add_parser("apply", help="Apply human-approved decisions: file Jira tickets, send Slack notifications.")
    triage = sub.add_parser("triage", help="Review evidence and payloads; record decisions without filing.")
    triage.add_argument("--reviewer", required=True)
    monitor = sub.add_parser("monitor", help="Check batch freshness, coverage, failures and review noise; exits 1 on alerts.")
    monitor.add_argument("--expected-calls", type=int, default=140)
    monitor.add_argument("--max-age-seconds", type=float, default=3600)
    monitor.add_argument("--baseline-rate", type=float)

    args = parser.parse_args(argv)
    cfg = load_config()

    if args.command == "review":
        summary = run_review(cfg)
        _print_review_summary(summary, cfg.review_queue_path, cfg.review_decisions_path)
        return int(summary.calls_failed > 0 or summary.calls_processed == 0)
    elif args.command == "apply":
        summary = run_apply(cfg)
        _print_apply_summary(summary)
        return int(summary.failed > 0)
    elif args.command == "triage":
        print(json.dumps(run_triage(cfg, args.reviewer), indent=2))
        return 0
    elif args.command == "monitor":
        if args.expected_calls < 1 or args.max_age_seconds <= 0 or (args.baseline_rate is not None and args.baseline_rate <= 0):
            parser.error("monitor counts, age and baseline rate must be positive")
        try:
            health = assess_health(EventLogger(cfg.log_path).read_all(), expected_calls=args.expected_calls,
                                   max_age_seconds=args.max_age_seconds, baseline_candidates_per_call=args.baseline_rate)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(json.dumps({"healthy": False, "alerts": [{"code": "INVALID_LOG", "detail": str(exc)}]}))
            return 1
        print(json.dumps(health, indent=2))
        return int(not health["healthy"])
    else:  # pragma: no cover -- argparse `required=True` makes this unreachable
        parser.error(f"unknown command: {args.command}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
