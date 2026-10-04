from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

from .run_holdout import input_hashes, judge_settings, pipeline_hashes, score_entries, validate_assessment
from ..pipeline import orchestrator
from ..pipeline.config import load_config
from ..pipeline.models import Candidate
from ..pipeline.state_store import StateStore, atomic_write_json


class CapturingJudge:
    def __init__(self, judge, directory: Path) -> None:
        self.judge = judge
        self.directory = directory

    def find_candidates(self, transcript):
        candidates = self.judge.find_candidates(transcript)
        atomic_write_json(self.directory / f"{transcript.call_id}.json", {
            "call_id": transcript.call_id,
            "source_sha256": hashlib.sha256(Path(transcript.path).read_bytes()).hexdigest(),
            "candidates": [asdict(candidate) for candidate in candidates],
        })
        print(json.dumps({"event": "semantic_call_captured", "call_id": transcript.call_id,
                          "candidates": len(candidates)}), flush=True)
        return candidates


class ReplayJudge:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def find_candidates(self, transcript):
        capture = json.loads((self.directory / f"{transcript.call_id}.json").read_text(encoding="utf-8"))
        if capture["source_sha256"] != hashlib.sha256(Path(transcript.path).read_bytes()).hexdigest():
            raise ValueError("Captured extraction does not match transcript bytes")
        return [Candidate(**{**item, "turn_span": tuple(item["turn_span"])}) for item in capture["candidates"]]


def run(cfg, output: Path, assessment: Path, repeat: int = 2) -> dict:
    if repeat < 2:
        raise ValueError("At least two independent inference passes are required")
    manifest, annotations = validate_assessment(cfg, assessment)
    if output.exists():
        raise ValueError("Refusing to overwrite prior semantic evidence")
    output.mkdir(parents=True)
    initial_hashes = pipeline_hashes()
    initial_inputs = input_hashes(cfg)
    judge = orchestrator._make_judge(cfg)
    runs = []
    for index in range(repeat):
        directory = output / f"run-{index + 1}"
        directory.mkdir()
        captures = directory / "extractions"
        with tempfile.TemporaryDirectory(prefix="june_semantic_") as tmp:
            scratch = Path(tmp)
            run_cfg = replace(cfg, state_path=scratch / "ledger.json", log_path=scratch / "events.jsonl",
                              review_queue_path=scratch / "queue.md", review_decisions_path=scratch / "decisions.json")
            with patch.object(orchestrator, "_make_judge", return_value=CapturingJudge(judge, captures)):
                summary = orchestrator.run_review(run_cfg)
            entries = StateStore(run_cfg.state_path).all_entries()
            score = score_entries(annotations["cases"], entries)
            score.update(run=index + 1, coverage=asdict(summary),
                         fingerprint=hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest())
            score["passed"] = (summary.calls_failed == 0 and summary.calls_processed == len(initial_inputs) - 2
                               and all(score[name]["value"] is not None and score[name]["value"] >= threshold
                                       for name, threshold in manifest["thresholds"].items()))
            atomic_write_json(directory / "ledger.json", entries)
            atomic_write_json(directory / "score.json", score)
            shutil.copy2(run_cfg.log_path, directory / "events.jsonl")
            runs.append(score)
    validate_assessment(cfg, assessment)
    if pipeline_hashes() != initial_hashes or input_hashes(cfg) != initial_inputs:
        raise ValueError("Source or input changed during inference")
    stable = len({item["fingerprint"] for item in runs}) == 1
    report = {"scope": "Two fresh-state live local-model inference passes; no extraction response cache",
              "pipeline_sha256": initial_hashes, "input_sha256": initial_inputs,
              "config": judge_settings(cfg), "manifest": manifest,
              "annotation_source": annotations["annotation_source"],
              "human_confirmed": annotations["human_confirmed"],
              "runs": runs, "stability": {"identical": stable, "repetitions": repeat},
              "passed": stable and all(item["passed"] for item in runs)}
    atomic_write_json(output / "assessment.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture two real semantic corpus passes with frozen source labels.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    args = parser.parse_args()
    report = run(load_config(), args.output, args.assessment)
    print(json.dumps({"passed": report["passed"], "stability": report["stability"],
                      "metrics": [{name: score[name] for name in ("precision", "recall", "negative_call_accuracy")}
                                  for score in report["runs"]]}, indent=2))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())