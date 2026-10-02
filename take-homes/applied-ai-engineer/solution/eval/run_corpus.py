from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import tempfile
from collections import Counter
from contextlib import ExitStack
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from stubs import jira_stub, slack_stub

from .run_holdout import evaluate as evaluate_holdout
from ..pipeline.config import Config, load_config
from ..pipeline.ingest import parse_transcript
from ..pipeline.logging_utils import EventLogger, assess_health
from ..pipeline.orchestrator import run_apply, run_review
from ..pipeline.review import load_review_decisions, write_review_queue_markdown
from ..pipeline.state_store import StateStore
from ..pipeline.triage import run_triage


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def audit_entries(entries: dict, cfg: Config) -> dict:
    annotations = json.loads(Path(__file__).with_name("audit_cases.json").read_text(encoding="utf-8"))
    outcomes = []
    for case in annotations["cases"]:
        actual = [entry for entry in entries.values() if entry.get("call_id") == case["call_id"] and entry.get("status") == "queued"]
        remaining = list(actual)
        missing = []
        for expected in case["expected"]:
            match = next((entry for entry in remaining if entry.get("action", "").replace("file-new-low", "file-new") == expected["action"]
                          and entry.get("issue_type") == expected["issue_type"]
                          and (not expected.get("matched_key") or entry.get("matched_key") == expected["matched_key"])
                          and all(re.search(pattern, entry.get("description", ""), re.I) for pattern in expected["patterns"])), None)
            if match is None:
                missing.append(expected)
            else:
                remaining.remove(match)
        path = cfg.transcripts_dir / (case["call_id"] + ".md")
        source = parse_transcript(path) if path.exists() else None
        outcomes.append({**case, "actual": actual, "missing": missing, "extra": remaining,
                         "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest() if source else None,
                         "source_quotes": [{"turn": turn.index, "speaker": turn.speaker.value, "text": turn.text}
                                           for turn in source.turns if turn.index in case["turns"]] if source else [],
                         "passed": not missing and not remaining and source is not None})
    return {"annotation_source": annotations["annotation_source"], "sampling": annotations["sampling"],
            "cases": outcomes, "passed": all(outcome["passed"] for outcome in outcomes)}


def write_audit_snapshot(cfg: Config, decisions_path: Path, output_path: Path) -> dict:
    report = audit_entries(json.loads(decisions_path.read_text(encoding="utf-8")), cfg)
    _write_json(output_path, report)
    return report


def export_demo(evidence_dir: Path, demo_dir: Path) -> None:
    report = json.loads((evidence_dir / "full_run.json").read_text(encoding="utf-8"))
    if not report["demo"]["performed"]:
        raise ValueError("Generate evidence with --demo-decisions before exporting the demo")
    entries = json.loads((evidence_dir / "decisions.json").read_text(encoding="utf-8"))
    selected = {key: entries[key] for key in report["demo"]["manifest"]}
    demo_dir.mkdir(parents=True, exist_ok=True)
    write_review_queue_markdown(selected, demo_dir / "review_queue_excerpt.md")
    payloads = json.loads((evidence_dir / "demo_payloads.json").read_text(encoding="utf-8"))
    for sink in ("jira", "slack"):
        (demo_dir / f"{sink}_outbox_excerpt.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in payloads[sink]), encoding="utf-8")


def _alert_probes(events: list[dict], expected_calls: int) -> dict:
    now = datetime.now(timezone.utc)
    last_run = events[-1]["run_id"]
    current = [event for event in events if event["run_id"] == last_run]
    completed = next(event for event in reversed(current) if event["event"] == "run_review_completed")
    scenarios = {
        "never_started": [],
        "stalled": [event for event in current if event["event"] != "run_review_completed"],
        "stale_completion": current,
        "silent_zero": [*current[:-1], {**completed, "candidates_found": 0}],
        "review_noise": [*current[:-1], {**completed, "queue_by_action": {"file-new-low": 9, "file-new": 1}}],
        "partial_failure": [*current[:-1], {**completed, "calls_failed": 1}],
    }
    results = {}
    for name, scenario in scenarios.items():
        check_time = now + timedelta(hours=2) if name in ("stalled", "stale_completion") else now
        results[name] = assess_health(scenario, now=check_time, expected_calls=expected_calls)
    return {"synthetic_fault_injection": True, "results": results}


def generate_evidence(cfg: Config, output: Path, expected_calls: int = 140,
                      demo_decisions: Path | None = None) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    paths = sorted(cfg.transcripts_dir.glob("call-*.md"))
    inputs = paths + [cfg.existing_issues_path, cfg.dev_labels_path]
    source_root = Path(__file__).resolve().parents[1]
    assessed = {f"call-{number:03d}": "supplied_dev_labels" for number in range(1, 16)}
    assessed.update({f"call-{number:03d}": "regression_audit" for number in (20, 40, 80, 100, 140)})
    assessed["call-051"] = "previously_inspected_unannotated"
    for name in ("holdout", "holdout_round2"):
        manifest = json.loads((Path(__file__).parent / name / "manifest.json").read_text(encoding="utf-8"))
        assessed.update({call_id: name + "_historical_regression" for call_id in manifest["sample"]})
    provenance = {
        "generated_at": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "judge": cfg.judge, "similarity_threshold": cfg.similarity_threshold,
        "model": cfg.openai_model, "llm_api_url": cfg.llm_api_url,
        "llm_timeout_seconds": cfg.llm_timeout_seconds,
        "input_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
        "source_sha256": {path.relative_to(source_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in sorted(source_root.rglob("*.py"))},
    }
    with tempfile.TemporaryDirectory(prefix="june_tapes_corpus_") as tmp, ExitStack() as stack:
        scratch = Path(tmp)
        scratch_cfg = replace(cfg, state_path=scratch / "ledger.json", log_path=scratch / "events.jsonl",
                              review_queue_path=scratch / "review_queue.md", review_decisions_path=scratch / "review_decisions.json")
        jira_path, slack_path = scratch / "jira.jsonl", scratch / "slack.jsonl"
        for module, log_name, path in ((jira_stub, "_JIRA_LOG", jira_path), (slack_stub, "_SLACK_LOG", slack_path)):
            stack.enter_context(patch.object(module, "_OUTBOX", str(scratch)))
            stack.enter_context(patch.object(module, log_name, str(path)))

        first = run_review(scratch_cfg)
        before = StateStore(scratch_cfg.state_path).all_entries()
        queue_before = load_review_decisions(scratch_cfg.review_decisions_path)
        pending_apply = run_apply(scratch_cfg)
        pending_writes = {"jira": len(_rows(jira_path)), "slack": len(_rows(slack_path))}
        second = run_review(scratch_cfg)
        after = StateStore(scratch_cfg.state_path).all_entries()
        queue_after = load_review_decisions(scratch_cfg.review_decisions_path)
        review_events = EventLogger(scratch_cfg.log_path).read_all()
        changed = sorted(key for key in before.keys() & after.keys() if before[key] != after[key])
        rerun = {"ledger_before_sha256": _digest(before), "ledger_after_sha256": _digest(after),
                 "added_keys": sorted(after.keys() - before.keys()), "removed_keys": sorted(before.keys() - after.keys()),
                 "changed_keys": changed, "review_decisions_identical": queue_before == queue_after,
                 "newly_queued": second.queued_for_review}
        per_call = []
        for path in paths:
            first_run_id = review_events[0]["run_id"]
            terminal = [event for event in review_events if event.get("call_id") == path.stem
                        and event["run_id"] == first_run_id and event["event"] in ("call_completed", "call_failed", "call_parse_failed")]
            entries = {key: entry for key, entry in before.items() if entry.get("call_id") == path.stem}
            per_call.append({"call_id": path.stem, "split": "dev" if int(path.stem.split("-")[1]) <= 15 else "unlabeled_holdout",
                             "assessment_status": assessed.get(path.stem, "unassessed"),
                             "outcome": terminal[-1] if terminal else {"event": "missing_completion"},
                             "queue_by_action": dict(Counter(entry["action"] for entry in entries.values() if entry["status"] == "queued")),
                             "ledger_keys": sorted(entries)})
        health = assess_health(review_events, expected_calls=expected_calls)
        probes = _alert_probes(review_events, expected_calls)
        demo = {"performed": False, "reason": "No demo approval manifest provided; all outputs remain gated."}
        if demo_decisions:
            manifest = load_review_decisions(demo_decisions)
            decisions = load_review_decisions(scratch_cfg.review_decisions_path)
            for key, decision in manifest.items():
                if key not in decisions or decision.get("decision") not in ("approved", "rejected"):
                    raise ValueError(f"Invalid or stale demo decision: {key}")
                if decision.get("action") != decisions[key]["action"]:
                    raise ValueError(f"Demo action changed for {key}; re-review required")
            views = []

            def capture_view(text: str) -> None:
                views.append(json.loads(text))

            def simulated_input(prompt: str) -> str:
                choice = manifest[views[-1]["key"]]
                if prompt.startswith("[a]"):
                    return "a" if choice["decision"] == "approved" else "r"
                return choice["note"]

            review_counts = run_triage(scratch_cfg, "GitHub Copilot (automated simulation)",
                                      keys=list(manifest), read=simulated_input, write=capture_view)
            recorded = load_review_decisions(scratch_cfg.review_decisions_path)
            _write_json(output / "review_session.json", {
                "simulation": True, "human_signoff": False,
                "timing_scope": "Measured automated input latency, NOT human review speed",
                "counts": review_counts, "views": views,
                "decisions": {key: recorded[key] for key in manifest},
            })
            applied = run_apply(scratch_cfg)
            writes_before = {"jira": _rows(jira_path), "slack": _rows(slack_path)}
            reapplied = run_apply(scratch_cfg)
            writes_after = {"jira": _rows(jira_path), "slack": _rows(slack_path)}
            demo = {"performed": True, "scope": "Explicit agent-reviewed demonstration, NOT human sign-off or full-corpus approval",
                    "manifest": manifest, "manifest_sha256": hashlib.sha256(demo_decisions.read_bytes()).hexdigest(),
                    "first_apply": asdict(applied), "second_apply": asdict(reapplied),
                    "outbox_counts_before_rerun": {name: len(rows) for name, rows in writes_before.items()},
                    "outbox_counts_after_rerun": {name: len(rows) for name, rows in writes_after.items()},
                    "outboxes_unchanged": writes_before == writes_after,
                    "passed": applied.failed == 0 and reapplied.failed == 0 and reapplied.filed == 0
                              and reapplied.corroborated == 0 and writes_before == writes_after}
            _write_json(output / "demo_payloads.json", writes_after)
        else:
            _write_json(output / "demo_payloads.json", {"jira": [], "slack": []})

        report = {
            "schema_version": 1, "provenance": provenance,
            "scope": "Coverage and repeatability over 140 supplied calls, NOT measured accuracy on the 125 unlabeled holdout calls.",
            "expected_calls": expected_calls, "discovered_calls": len(paths),
            "first_review": asdict(first), "second_review": asdict(second), "per_call": per_call,
            "split_counts": {split: {"calls": sum(row["split"] == split for row in per_call),
                                      "queue_by_action": dict(sum((Counter(row["queue_by_action"]) for row in per_call if row["split"] == split), Counter()))}
                             for split in ("dev", "unlabeled_holdout")},
            "pending_apply": asdict(pending_apply), "pending_outbox_counts": pending_writes,
            "rerun_diff": rerun, "health": health, "demo": demo,
            "passed": first.calls_processed == expected_calls and first.calls_failed == 0
                      and second.calls_processed == expected_calls and second.calls_failed == 0
                      and before == after and queue_before == queue_after and second.queued_for_review == 0
                      and pending_writes == {"jira": 0, "slack": 0} and pending_apply.failed == 0
                      and all(row["outcome"]["event"] == "call_completed" for row in per_call)
                      and (not demo["performed"] or demo["passed"]),
        }
        _write_json(output / "full_run.json", report)
        _write_json(output / "assessment_inventory.json", {
            "scope": "Annotation coverage inventory, NOT new adjudication or correctness labels",
            "counts": dict(Counter(row["assessment_status"] for row in per_call)),
            "calls": [{"call_id": row["call_id"], "assessment_status": row["assessment_status"],
                   "note": f"{row['assessment_status']}; {row['outcome']['event']}; "
                       f"{sum(row['queue_by_action'].values())} machine proposals, not adjudicated outcomes"}
                  for row in per_call],
        })
        _write_json(output / "decisions.json", before)
        _write_json(output / "audit.json", audit_entries(before, cfg))
        _write_json(output / "alert_examples.json", probes)
        shutil.copy2(scratch_cfg.review_queue_path, output / "review_queue.md")
        shutil.copy2(scratch_cfg.review_decisions_path, output / "review_decisions.json")
        shutil.copy2(scratch_cfg.log_path, output / "events.jsonl")
    return report


def _safe_evaluate(cfg: Config, directory: Path) -> dict:
    try:
        return evaluate_holdout(cfg, directory)
    except (ValueError, OSError, KeyError, TypeError, re.error) as error:
        return {"passed": False, "error": str(error), "scope": "Assessment invalid or missing; cannot certify semantic quality"}


def verify_acceptance(cfg: Config, output: Path, coverage: dict, assessment_dir: Path, *,
                      regression_assessment_dir: Path | None = None) -> dict:
    assessment = _safe_evaluate(cfg, assessment_dir)
    _write_json(output / "holdout.json", assessment)
    regression = _safe_evaluate(cfg, regression_assessment_dir) if regression_assessment_dir else None
    if regression is not None:
        _write_json(output / "holdout_regression.json", regression)
    audit = json.loads((output / "audit.json").read_text(encoding="utf-8"))
    acceptance = {
        "schema_version": 2, "generated_at": datetime.now(timezone.utc).isoformat(),
        "coverage_and_rerun_passed": coverage["passed"],
        "regression_audit_passed": audit["passed"],
        "semantic_assessment_passed": assessment["passed"],
        "semantic_assessment_scope": "Fresh sample never used to tune the pipeline; the real generalization gate",
        "regression_suite_passed": regression["passed"] if regression is not None else None,
        "regression_suite_scope": (
            "Earlier sample now used for tuning; confirms no regression only, NOT an unbiased generalization claim"
            if regression is not None else None
        ),
        "operational_health_clear": coverage["health"]["healthy"],
        "human_confirmed_annotations": assessment.get("human_confirmed", False),
        "passed": coverage["passed"] and audit["passed"] and assessment["passed"],
        "meaning": "Automated evidence gates only; not human approval, private-label certification or operational all-clear",
    }
    _write_json(output / "acceptance.json", acceptance)
    return acceptance


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate full-corpus coverage and rerun evidence in isolated state/outboxes.")
    parser.add_argument("--output-dir", type=Path, default=Path("solution/artifacts"))
    parser.add_argument("--expected-calls", type=int, default=140)
    parser.add_argument("--demo-decisions", type=Path)
    parser.add_argument("--demo-output-dir", type=Path, help="Also refresh curated queue and payload excerpts.")
    parser.add_argument("--assessment-dir", type=Path, default=Path(__file__).with_name("holdout_round2"))
    parser.add_argument("--regression-assessment-dir", type=Path, default=Path(__file__).with_name("holdout"))
    args = parser.parse_args(argv)
    if args.expected_calls < 1:
        parser.error("--expected-calls must be positive")
    if args.demo_output_dir and not args.demo_decisions:
        parser.error("--demo-output-dir requires --demo-decisions")
    cfg = load_config()
    report = generate_evidence(cfg, args.output_dir, args.expected_calls, args.demo_decisions)
    if args.demo_output_dir:
        export_demo(args.output_dir, args.demo_output_dir)
    acceptance = verify_acceptance(cfg, args.output_dir, report, args.assessment_dir,
                                   regression_assessment_dir=args.regression_assessment_dir)
    print(json.dumps({"acceptance": acceptance, **{key: report[key] for key in
                     ("first_review", "second_review", "pending_outbox_counts", "rerun_diff")}}, indent=2))
    return 0 if acceptance["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())