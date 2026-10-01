from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import tempfile
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from ..pipeline.config import Config, load_config
from ..pipeline.ingest import parse_transcript
from ..pipeline.orchestrator import run_review
from ..pipeline.state_store import StateStore


EXCLUDED_CALLS = [f"call-{number:03d}" for number in [*range(1, 16), 20, 40, 51, 80, 100, 140]]
SAMPLE_SEED = "june-tapes-prospective-assessment-v1"


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pipeline_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    paths = [*sorted((root / "pipeline").glob("*.py")), root / "cli.py"]
    return {path.relative_to(root).as_posix(): digest_file(path) for path in paths}


def input_hashes(cfg: Config) -> dict[str, str]:
    paths = [*sorted(cfg.transcripts_dir.glob("call-*.md")), cfg.existing_issues_path, cfg.dev_labels_path]
    return {path.name: digest_file(path) for path in paths}


def judge_settings(cfg: Config) -> dict:
    return {"judge": cfg.judge, "similarity_threshold": cfg.similarity_threshold, "openai_model": cfg.openai_model}


def select_calls(call_ids: list[str], count: int, seed: str = SAMPLE_SEED, excluded: list[str] = EXCLUDED_CALLS) -> list[str]:
    eligible = sorted(set(call_ids) - set(excluded))
    if not 1 <= count <= len(eligible):
        raise ValueError("Sample size must be positive and no larger than the eligible population")
    ranked = sorted(eligible, key=lambda call_id: hashlib.sha256(f"{seed}:{call_id}".encode()).hexdigest())
    return sorted(ranked[:count])


def prepare(cfg: Config, output: Path, count: int = 24, *, seed: str = SAMPLE_SEED,
           extra_excluded: list[str] = (), exclusion_reason: str | None = None) -> dict:
    if output.exists() and any(output.iterdir()):
        raise ValueError("Assessment directory is not empty; never overwrite a frozen assessment")
    excluded = sorted({*EXCLUDED_CALLS, *extra_excluded})
    paths = sorted(cfg.transcripts_dir.glob("call-*.md"))
    selected = select_calls([path.stem for path in paths], count, seed, excluded)
    manifest = {
        "schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(),
        "sampling": "Lowest SHA256(seed:call_id), without replacement, independent of pipeline outcomes",
        "seed": seed, "sample": selected, "excluded_calls": excluded,
        "exclusion_reason": exclusion_reason or "Supplied dev labels, five previous regression audits, and previously inspected call-051",
        "eligible_calls": sorted({path.stem for path in paths} - set(excluded)),
        "pipeline_sha256": pipeline_hashes(), "input_sha256": input_hashes(cfg), "config": judge_settings(cfg),
        "thresholds": {"precision": 0.85, "recall": 0.85, "negative_call_accuracy": 0.85},
        "minimum_repeats": 2,
        "matching_rule": "One-to-one action/type/target and source-evidence anchors; all low-confidence extras count as false positives",
        "independence_limit": "Same coding agent authors annotations; not independent human or official private labels. Prior exposure cannot be conclusively excluded.",
    }
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "manifest.json", manifest)
    write_json(output / "annotations.json", {
        "annotation_source": "pending", "human_confirmed": False,
        "cases": [{"call_id": call_id, "review_status": "pending", "reason": "", "evidence": [], "expected": []}
                  for call_id in selected],
    })
    return manifest


def validate_assessment(cfg: Config, directory: Path, *, sealed: bool = True) -> tuple[dict, dict]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    annotations = json.loads((directory / "annotations.json").read_text(encoding="utf-8"))
    if manifest["pipeline_sha256"] != pipeline_hashes():
        raise ValueError("Frozen pipeline changed; this assessment cannot certify a newly tuned version")
    if manifest["input_sha256"] != input_hashes(cfg) or manifest["config"] != judge_settings(cfg):
        raise ValueError("Frozen inputs or configuration changed")
    current_ids = sorted(path.stem for path in cfg.transcripts_dir.glob("call-*.md"))
    if not set(EXCLUDED_CALLS) <= set(manifest["excluded_calls"]):
        raise ValueError("Exclusion set must retain the baseline dev/audit/inspected exclusions")
    expected_sample = select_calls(current_ids, len(manifest["sample"]), manifest["seed"], manifest["excluded_calls"])
    if manifest["sample"] != expected_sample:
        raise ValueError("Sample does not match the frozen outcome-independent selection protocol")
    cases = annotations["cases"]
    if sorted(case["call_id"] for case in cases) != manifest["sample"]:
        raise ValueError("Annotations must cover each sampled call exactly once")
    if not annotations.get("annotation_source") or annotations["annotation_source"] == "pending":
        raise ValueError("Annotation provenance is required")
    tracked = {issue["key"]: issue for issue in json.loads(cfg.existing_issues_path.read_text(encoding="utf-8"))}
    for case in cases:
        if case["review_status"] != "reviewed" or not case["reason"] or not case["evidence"]:
            raise ValueError(f"Unreviewed or ungrounded annotation: {case['call_id']}")
        transcript = parse_transcript(cfg.transcripts_dir / f"{case['call_id']}.md")
        external = [turn.text for turn in transcript.turns if turn.speaker.value == "EXTERNAL"]
        if any(not quote or not any(quote in text for text in external) for quote in case["evidence"]):
            raise ValueError(f"Evidence is not an external source quote: {case['call_id']}")
        for expected in case["expected"]:
            if expected["action"] not in ("file-new", "corroborate") or expected["issue_type"] not in ("Bug", "Feature"):
                raise ValueError("Unsupported annotation action or issue type")
            if len(expected["patterns"]) < 2 or any(not pattern for pattern in expected["patterns"]):
                raise ValueError("Each issue requires at least two nonempty identity anchors")
            if not all(re.search(pattern, "\n".join(external), re.I) for pattern in expected["patterns"]):
                raise ValueError(f"Issue anchors unsupported by source: {case['call_id']}")
            if expected["action"] == "corroborate":
                target = tracked.get(expected.get("matched_key"))
                if not target or target["type"] != expected["issue_type"] or target["status"] == "Shipped":
                    raise ValueError("Corroboration annotation must identify an open tracked issue of the same type")
    if not any(case["expected"] for case in cases) or not any(not case["expected"] for case in cases):
        raise ValueError("Assessment must contain actionable and no-issue calls")
    if sealed:
        seal = json.loads((directory / "seal.json").read_text(encoding="utf-8"))
        hashes = {name: digest_file(directory / name) for name in ("manifest.json", "annotations.json")}
        if seal["files_sha256"] != hashes or seal["evaluator_sha256"] != digest_file(Path(__file__)):
            raise ValueError("Sealed annotations, protocol or evaluator changed; retain old evidence and create a new assessment")
    return manifest, annotations


def seal_assessment(cfg: Config, directory: Path) -> dict:
    validate_assessment(cfg, directory, sealed=False)
    report = {
        "sealed_at": datetime.now(timezone.utc).isoformat(),
        "files_sha256": {name: digest_file(directory / name) for name in ("manifest.json", "annotations.json")},
        "evaluator_sha256": digest_file(Path(__file__)),
        "purpose": "Integrity checkpoint before first score, not cryptographic proof of independent annotation",
    }
    with (directory / "seal.json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return report


def matches_issue(expected: dict, actual: dict, entries: dict) -> bool:
    if actual.get("issue_type") != expected["issue_type"]:
        return False
    if not all(re.search(pattern, actual.get("description", ""), re.I) for pattern in expected["patterns"]):
        return False
    if expected["action"] == "corroborate":
        return actual.get("action") == "corroborate" and actual.get("matched_key") == expected["matched_key"]
    if actual.get("action") in ("file-new", "file-new-low"):
        return True
    if actual.get("action") == "corroborate" and str(actual.get("matched_key", "")).startswith("PENDING:"):
        return any(parent.get("action") in ("file-new", "file-new-low")
                   and parent.get("matched_key") == actual["matched_key"]
                   and parent.get("issue_type") == expected["issue_type"]
                   and all(re.search(pattern, parent.get("description", ""), re.I) for pattern in expected["patterns"])
                   for parent in entries.values())
    return False


def ratio_report(numerator: int, denominator: int) -> dict:
    if denominator == 0:
        return {"numerator": numerator, "denominator": 0, "value": None, "wilson_95": None}
    value = numerator / denominator
    zscore = 1.959963984540054
    divisor = 1 + zscore ** 2 / denominator
    center = (value + zscore ** 2 / (2 * denominator)) / divisor
    margin = zscore * math.sqrt(value * (1 - value) / denominator + zscore ** 2 / (4 * denominator ** 2)) / divisor
    return {"numerator": numerator, "denominator": denominator, "value": value,
            "wilson_95": [max(0, center - margin), min(1, center + margin)]}


def score_entries(cases: list[dict], entries: dict) -> dict:
    outcomes = []
    for case in cases:
        actual = [{"ledger_key": key, **entry} for key, entry in sorted(entries.items())
                  if entry.get("call_id") == case["call_id"] and entry.get("status") == "queued"]
        expected = case["expected"]
        owners: dict[int, int] = {}

        def assign(expected_index: int, visited: set[int]) -> bool:
            for actual_index, entry in enumerate(actual):
                if actual_index in visited or not matches_issue(expected[expected_index], entry, entries):
                    continue
                visited.add(actual_index)
                if actual_index not in owners or assign(owners[actual_index], visited):
                    owners[actual_index] = expected_index
                    return True
            return False

        for expected_index in range(len(expected)):
            assign(expected_index, set())
        matched = [{"expected_index": expected_index, "actual": actual[actual_index]}
                   for actual_index, expected_index in sorted(owners.items())]
        extra = [entry for actual_index, entry in enumerate(actual) if actual_index not in owners]
        missing = [item for expected_index, item in enumerate(expected) if expected_index not in owners.values()]
        outcomes.append({**case, "matched": matched, "extra": extra, "missing": missing,
                         "passed": not extra and not missing})
    true_positives = sum(len(case["matched"]) for case in outcomes)
    false_positives = sum(len(case["extra"]) for case in outcomes)
    false_negatives = sum(len(case["missing"]) for case in outcomes)
    negatives = [case for case in outcomes if not case["expected"]]
    tiers = {}
    for tier, low in (("confident", False), ("low_confidence", True)):
        matched_count = sum((item["actual"].get("action") == "file-new-low") == low for case in outcomes for item in case["matched"])
        extra_count = sum((item.get("action") == "file-new-low") == low for case in outcomes for item in case["extra"])
        tiers[tier] = ratio_report(matched_count, matched_count + extra_count)
    return {
        "cases": outcomes, "true_positives": true_positives, "false_positives": false_positives, "false_negatives": false_negatives,
        "precision": ratio_report(true_positives, true_positives + false_positives),
        "recall": ratio_report(true_positives, true_positives + false_negatives),
        "negative_call_accuracy": ratio_report(sum(case["passed"] for case in negatives), len(negatives)),
        "exact_call_accuracy": ratio_report(sum(case["passed"] for case in outcomes), len(outcomes)),
        "precision_by_tier": tiers,
    }


def evaluate(cfg: Config, directory: Path, repeat: int = 2) -> dict:
    manifest, annotations = validate_assessment(cfg, directory)
    if repeat < manifest["minimum_repeats"]:
        raise ValueError("At least two fresh-state repetitions are required")
    runs = []
    for run_index in range(repeat):
        with tempfile.TemporaryDirectory(prefix="june_tapes_holdout_") as tmp:
            scratch = Path(tmp)
            scratch_cfg = replace(cfg, state_path=scratch / "ledger.json", log_path=scratch / "events.jsonl",
                                  review_queue_path=scratch / "queue.md", review_decisions_path=scratch / "decisions.json")
            summary = run_review(scratch_cfg)
            entries = StateStore(scratch_cfg.state_path).all_entries()
            result = score_entries(annotations["cases"], entries)
            result["run"] = run_index + 1
            result["coverage"] = asdict(summary)
            result["fingerprint"] = hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
            result["passed"] = (summary.calls_processed == len(manifest["input_sha256"]) - 2
                                and summary.calls_failed == 0
                                and all(result[name]["value"] is not None and result[name]["value"] >= threshold
                                        for name, threshold in manifest["thresholds"].items()))
            runs.append(result)
    validate_assessment(cfg, directory)
    stable = len({run["fingerprint"] for run in runs}) == 1
    return {
        "schema_version": 1, "generated_at": datetime.now(timezone.utc).isoformat(),
        "annotation_source": annotations["annotation_source"], "human_confirmed": annotations["human_confirmed"],
        "scope": "Frozen source-annotated sample; NOT official private-label or independent human accuracy",
        "interval_caveat": "Wilson intervals are descriptive binomial approximations; issue clustering, selection exclusions and annotation error are not captured. Thresholds use point estimates, not lower bounds.",
        "sample": manifest["sample"], "eligible_calls": len(manifest["eligible_calls"]),
        "unassessed_eligible_calls": len(manifest["eligible_calls"]) - len(manifest["sample"]),
        "thresholds": manifest["thresholds"], "seal": json.loads((directory / "seal.json").read_text(encoding="utf-8")),
        "provenance": {"pipeline_sha256": pipeline_hashes(), "input_sha256": input_hashes(cfg), "config": judge_settings(cfg)},
        "runs": runs, "stability": {"repetitions": repeat, "identical": stable},
        "passed": stable and all(run["passed"] for run in runs),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze and evaluate a source-annotated call sample without altering the pipeline.")
    parser.add_argument("command", choices=["prepare", "seal", "evaluate"])
    parser.add_argument("--assessment-dir", type=Path, default=Path("solution/eval/holdout"))
    parser.add_argument("--sample-size", type=int, default=24)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--output", type=Path, default=Path("solution/artifacts/holdout.json"))
    parser.add_argument("--seed", default=SAMPLE_SEED, help="Ranking seed; use a new value for a fresh, independently-ranked round.")
    parser.add_argument("--exclude-from-manifest", type=Path, action="append", default=[],
                        help="Prior round's manifest.json; its sample is added to this round's exclusions. Repeatable.")
    args = parser.parse_args(argv)
    try:
        cfg = load_config()
        if args.command == "prepare":
            extra_excluded = [call_id for path in args.exclude_from_manifest
                              for call_id in json.loads(path.read_text(encoding="utf-8"))["sample"]]
            report = prepare(cfg, args.assessment_dir, args.sample_size, seed=args.seed, extra_excluded=extra_excluded)
        elif args.command == "seal":
            report = seal_assessment(cfg, args.assessment_dir)
        else:
            report = evaluate(cfg, args.assessment_dir, args.repeat)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            write_json(args.output, report)
            print(json.dumps({"passed": report["passed"], "stability": report["stability"],
                              "metrics": [{key: run[key] for key in ("run", "precision", "recall", "negative_call_accuracy")}
                                          for run in report["runs"]]}, indent=2))
            return 0 if report["passed"] else 1
    except (ValueError, OSError, KeyError, TypeError, re.error) as error:
        print(json.dumps({"passed": False, "error": str(error)}))
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())