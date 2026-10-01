from __future__ import annotations

import unittest
import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from solution.eval.run_eval import EvalRunOutcome, _match_call, _run_hard_cases, _run_once, build_report
from solution.eval.run_corpus import audit_entries, verify_acceptance
from solution.eval.run_holdout import EXCLUDED_CALLS, matches_issue, prepare, ratio_report, score_entries, seal_assessment, select_calls, validate_assessment
from solution.pipeline.config import load_config


class TestHoldoutAssessment(unittest.TestCase):
    def test_coverage_success_cannot_hide_failed_missing_or_stale_assessment(self) -> None:
        cfg = load_config()
        coverage = {"passed": True, "health": {"healthy": True}}
        with TemporaryDirectory() as tmp:
            output = Path(tmp)
            (output / "audit.json").write_text('{"passed": true}', encoding="utf-8")
            for problem in (ValueError("changed source"), FileNotFoundError("missing assessment")):
                with patch("solution.eval.run_corpus.evaluate_holdout", side_effect=problem):
                    self.assertFalse(verify_acceptance(cfg, output, coverage, output)["passed"])
            with patch("solution.eval.run_corpus.evaluate_holdout", return_value={"passed": False}):
                self.assertFalse(verify_acceptance(cfg, output, coverage, output)["passed"])
            with patch("solution.eval.run_corpus.evaluate_holdout", return_value={"passed": True, "human_confirmed": False}):
                result = verify_acceptance(cfg, output, coverage, output)
                self.assertTrue(result["passed"])
                self.assertFalse(result["human_confirmed_annotations"])

    def test_low_confidence_noise_and_silent_misses_fail_scoring(self) -> None:
        cases = [{"call_id": "call-positive", "expected": [{"action": "file-new", "issue_type": "Bug", "patterns": ["outlook", "time"]}]},
                 {"call_id": "call-negative", "expected": []}]
        entries = {"noise": {"call_id": "call-negative", "status": "queued", "action": "file-new-low", "issue_type": "Bug", "description": "vague app gripe"}}
        report = score_entries(cases, entries)
        self.assertEqual((report["true_positives"], report["false_positives"], report["false_negatives"]), (0, 1, 1))
        self.assertEqual(report["negative_call_accuracy"]["value"], 0)
        self.assertEqual(report["precision_by_tier"]["low_confidence"]["denominator"], 1)
        self.assertIsNone(ratio_report(0, 0)["value"])

    def test_maximum_matching_does_not_depend_on_expected_order(self) -> None:
        broad = {"action": "file-new", "issue_type": "Bug", "patterns": ["app"]}
        narrow = {**broad, "patterns": ["app", "outlook"]}
        entries = {key: {"call_id": "call-test", "status": "queued", "action": "file-new", "issue_type": "Bug", "description": description}
                   for key, description in [("first", "app outlook"), ("second", "app unrelated")]}
        report = score_entries([{"call_id": "call-test", "expected": [broad, narrow]}], entries)
        self.assertEqual(report["true_positives"], 2)

    def test_wrong_tracked_target_or_pending_parent_cannot_match(self) -> None:
        expected = {"action": "file-new", "issue_type": "Bug", "patterns": ["ping", "lock"]}
        actual = {"action": "corroborate", "issue_type": "Bug", "matched_key": "PROJ-064", "description": "ping lock"}
        self.assertFalse(matches_issue(expected, actual, {}))
        actual["matched_key"] = "PENDING:1"
        parent = {"action": "file-new-low", "issue_type": "Bug", "matched_key": "PENDING:1", "description": "okta expires"}
        self.assertFalse(matches_issue(expected, actual, {"parent": parent}))
        parent["description"] = "ping lock"
        self.assertTrue(matches_issue(expected, actual, {"parent": parent}))

    def test_validation_rejects_missing_labels_unquoted_evidence_and_source_drift(self) -> None:
        cfg = load_config()
        with TemporaryDirectory() as tmp:
            directory = Path(tmp) / "assessment"
            prepare(cfg, directory)
            with self.assertRaisesRegex(ValueError, "provenance"):
                validate_assessment(cfg, directory, sealed=False)
            source = Path(__file__).parents[1] / "eval" / "holdout" / "annotations.json"
            labels = json.loads(source.read_text(encoding="utf-8"))
            (directory / "annotations.json").write_text(json.dumps(labels), encoding="utf-8")
            validate_assessment(cfg, directory, sealed=False)
            with patch("solution.eval.run_holdout.pipeline_hashes", return_value={}):
                with self.assertRaisesRegex(ValueError, "pipeline changed"):
                    validate_assessment(cfg, directory, sealed=False)
            labels["cases"][0]["evidence"] = ["fabricated quote"]
            (directory / "annotations.json").write_text(json.dumps(labels), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "external source quote"):
                validate_assessment(cfg, directory, sealed=False)
            labels["cases"].pop()
            (directory / "annotations.json").write_text(json.dumps(labels), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exactly once"):
                validate_assessment(cfg, directory, sealed=False)

    def test_seal_detects_annotation_edits_and_cannot_be_overwritten(self) -> None:
        cfg = load_config()
        with TemporaryDirectory() as tmp:
            directory = Path(tmp) / "assessment"
            prepare(cfg, directory)
            source = Path(__file__).parents[1] / "eval" / "holdout" / "annotations.json"
            (directory / "annotations.json").write_bytes(source.read_bytes())
            seal_assessment(cfg, directory)
            validate_assessment(cfg, directory)
            with self.assertRaises(FileExistsError):
                seal_assessment(cfg, directory)
            with (directory / "annotations.json").open("a", encoding="utf-8") as handle:
                handle.write("\n")
            with self.assertRaisesRegex(ValueError, "Sealed annotations"):
                validate_assessment(cfg, directory)

    def test_sample_is_deterministic_and_excludes_known_development_calls(self) -> None:
        call_ids = [f"call-{number:03d}" for number in range(1, 141)]
        selected = select_calls(call_ids, 24)
        self.assertEqual(selected, select_calls(list(reversed(call_ids)), 24))
        self.assertEqual(len(selected), 24)
        self.assertFalse(set(selected) & set(EXCLUDED_CALLS))
        for count in (0, 120):
            with self.assertRaises(ValueError):
                select_calls(call_ids, count)

    def test_prepare_refuses_to_replace_a_frozen_assessment(self) -> None:
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "assessment"
            manifest = prepare(load_config(), output, 2)
            self.assertEqual(len(manifest["sample"]), 2)
            self.assertTrue(manifest["pipeline_sha256"])
            before = (output / "manifest.json").read_bytes()
            with self.assertRaises(ValueError):
                prepare(load_config(), output, 2)
            self.assertEqual(before, (output / "manifest.json").read_bytes())


class TestEvalMetrics(unittest.TestCase):
    def test_report_requires_every_run_to_pass_and_records_bad_label_control(self) -> None:
        cfg = load_config()
        passing = _run_once(cfg)
        failed = deepcopy(passing)
        failed.calls_failed = 1
        report = build_report(cfg, [failed, passing])
        self.assertFalse(report["passed"])
        self.assertTrue(report["stability"]["identical"])
        self.assertEqual(report["diagnostic_control"]["matched"], 0)
        self.assertEqual(report["diagnostic_control"]["missing"], 1)
        self.assertFalse(build_report(cfg, [passing])["passed"])

    def test_spot_audit_detects_missing_issues_and_negative_call_noise(self) -> None:
        entry = {"call_id": "call-140", "status": "queued", "action": "file-new-low", "issue_type": "Bug"}
        audit = audit_entries({"noise": entry}, load_config())
        self.assertFalse(audit["passed"])
        by_call = {case["call_id"]: case for case in audit["cases"]}
        self.assertEqual(len(by_call["call-040"]["missing"]), 1)
        self.assertEqual(len(by_call["call-140"]["extra"]), 1)

    def test_low_confidence_matches_do_not_inflate_confident_precision(self) -> None:
        confident_match = {"action": "file-new"}
        confident_miss = {"action": "file-new"}
        low_match = {"action": "file-new-low"}
        low_miss = {"action": "file-new-low"}
        outcome = EvalRunOutcome(
            entries_by_call={"call-001": [confident_match, confident_miss, low_match, low_miss]},
            true_positives=2,
            unmatched_confident=[("call-001", confident_miss)],
            unmatched_low_confidence=[("call-001", low_miss)],
        )
        self.assertEqual(outcome.precision, 0.5)
        self.assertEqual(outcome.all_queue_precision, 0.5)

    def test_unrelated_bug_cannot_match_expected_bug(self) -> None:
        matched, extra, missed = _match_call("call-011", [{"action": "file-new", "type": "Bug"}],
                                           [{"action": "file-new", "issue_type": "Bug", "description": "The export is broken."}])
        self.assertEqual((matched, len(extra), len(missed)), (0, 1, 1))

    def test_low_confidence_correct_evidence_matches_once(self) -> None:
        entry = {"action": "file-new-low", "issue_type": "Bug", "description": "The profile link truncates at an apostrophe and returns 404."}
        matched, extra, missed = _match_call("call-011", [{"action": "file-new", "type": "Bug"}], [entry, entry])
        self.assertEqual((matched, len(extra), len(missed)), (1, 1, 0))

    def test_extra_injection_call_item_fails_hard_case(self) -> None:
        results = _run_hard_cases({"call-005": [{"action": "corroborate", "matched_key": "PROJ-087"},
                                               {"action": "file-new-low", "issue_type": "Bug"}]})
        self.assertFalse(results[0][1])

    def test_fingerprint_detects_evidence_and_priority_changes(self) -> None:
        first = EvalRunOutcome(entries_by_call={"call-001": [{"priority": "P3", "description": "first"}]})
        second = EvalRunOutcome(entries_by_call={"call-001": [{"priority": "P1", "description": "second"}]})
        self.assertNotEqual(first.fingerprint(), second.fingerprint())


if __name__ == "__main__":
    unittest.main()