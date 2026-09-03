"""Unit tests for cli.py -- argument parsing and dispatch only. The actual
pipeline behavior is orchestrator.py's responsibility (see
test_orchestrator.py); these tests mock run_review/run_apply so they stay
fast and independent of transcripts/state on disk.
"""
from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from solution import cli
from solution.pipeline.config import Config
from solution.pipeline.orchestrator import ApplyRunSummary, ReviewRunSummary


def _make_cfg() -> Config:
    return Config(
        transcripts_dir=Path("/tmp/transcripts"),
        existing_issues_path=Path("/tmp/existing_issues.json"),
        dev_labels_path=Path("/tmp/dev_labels.json"),
        state_path=Path("/tmp/state/pipeline_state.json"),
        review_queue_path=Path("/tmp/state/review_queue.md"),
        review_decisions_path=Path("/tmp/state/review_decisions.json"),
        log_path=Path("/tmp/state/events.jsonl"),
        similarity_threshold=0.2,
        judge="heuristic",
        openai_model="gpt-4o-mini",
    )


class TestCliDispatch(unittest.TestCase):
    def test_review_command_calls_run_review_and_prints_summary(self) -> None:
        cfg = _make_cfg()
        summary = ReviewRunSummary(calls_processed=3, queued_for_review=2)
        with patch.object(cli, "load_config", return_value=cfg), \
             patch.object(cli, "run_review", return_value=summary) as mock_run_review:
            out = io.StringIO()
            with redirect_stdout(out):
                exit_code = cli.main(["review"])

        mock_run_review.assert_called_once_with(cfg)
        self.assertEqual(exit_code, 0)
        self.assertIn("queued for review", out.getvalue())
        self.assertIn(str(cfg.review_queue_path), out.getvalue())

    def test_apply_command_calls_run_apply_and_prints_summary(self) -> None:
        cfg = _make_cfg()
        summary = ApplyRunSummary(filed=1, corroborated=1)
        with patch.object(cli, "load_config", return_value=cfg), \
             patch.object(cli, "run_apply", return_value=summary) as mock_run_apply:
            out = io.StringIO()
            with redirect_stdout(out):
                exit_code = cli.main(["apply"])

        mock_run_apply.assert_called_once_with(cfg)
        self.assertEqual(exit_code, 0)
        self.assertIn("Filed 1", out.getvalue())

    def test_missing_command_errors(self) -> None:
        with self.assertRaises(SystemExit):
            cli.main([])

    def test_unknown_command_errors(self) -> None:
        with self.assertRaises(SystemExit):
            cli.main(["bogus"])


if __name__ == "__main__":
    unittest.main()
