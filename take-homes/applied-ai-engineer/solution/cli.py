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
import sys
from typing import Optional, Sequence

from .pipeline.config import load_config
from .pipeline.orchestrator import ApplyRunSummary, ReviewRunSummary, run_apply, run_review


def _print_review_summary(summary: ReviewRunSummary, review_queue_path, review_decisions_path) -> None:
    print(f"Processed {summary.calls_processed} call(s), {summary.calls_failed} failed to parse.")
    print(
        f"Found {summary.candidates_found} candidate(s): "
        f"{summary.queued_for_review} queued for review, "
        f"{summary.candidates_suppressed} suppressed, "
        f"{summary.not_actionable} not actionable (e.g. already shipped), "
        f"{summary.collapsed_duplicates} collapsed same-call duplicate(s), "
        f"{summary.skipped_already_processed} already processed in a prior run."
    )
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

    args = parser.parse_args(argv)
    cfg = load_config()

    if args.command == "review":
        summary = run_review(cfg)
        _print_review_summary(summary, cfg.review_queue_path, cfg.review_decisions_path)
    elif args.command == "apply":
        summary = run_apply(cfg)
        _print_apply_summary(summary)
    else:  # pragma: no cover -- argparse `required=True` makes this unreachable
        parser.error(f"unknown command: {args.command}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
