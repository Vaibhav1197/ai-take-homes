# Resubmission Evidence: 2026-10-02

**Not ready to claim passing generalization or a 4.5/5 panel score.** The human
review workflow and reliability fixes are implemented and tested. The lexical
extractor still fails the measured semantic gate; free-model inference was
blocked by Windows security. No scores, approvals or favorable metrics were fabricated.

## Verified Results

| Check | Observed result |
|---|---|
| Unit/integration suite | 225 passed |
| Dev evaluation, two fresh runs | TP=14, FP=0, FN=0; 10/10 hard cases; identical decisions |
| Full corpus | 140 processed, 0 failed; 228 candidates; 94 queued |
| Pending gate | 0 Jira and 0 Slack writes |
| Review rerun | 0 added/removed/changed ledger keys; 0 newly queued |
| Demo apply / reapply | Jira 1 -> 1; Slack 2 -> 2; 1 rejection |
| Historical round 1, twice | TP=12, FP=5, FN=2; precision 70.6%, recall 85.7% |
| Historical round 2, twice | TP=6, FP=9, FN=5; precision 40.0%, recall 54.5% |
| Operational health | Warning: 30/94 low-confidence proposals exceeds 25% |

The corpus and both regression commands exit 1. Coverage success is not semantic
acceptance. The old sample seals intentionally cannot certify changed code.
Regression mode retains label/input integrity but explicitly does not certify freshness.

## Evidence Map

| Reviewer concern | Inspect |
|---|---|
| Complete outputs and per-call coverage | [full_run.json](full_run.json), [decisions.json](decisions.json) |
| Every call's assessment status | [assessment_inventory.json](assessment_inventory.json): 15 dev, 5 audits, 24 + 24 historical samples, 1 previously inspected, 71 unassessed |
| Reviewer view and approve/reject path | [review_session.json](review_session.json), [review_queue.md](review_queue.md) |
| Actual resulting payloads | [demo_payloads.json](demo_payloads.json) |
| Rerun diff and before/after sink counts | `rerun_diff` and `demo` in [full_run.json](full_run.json) |
| Repeated dev checks and bad-label control | [dev_eval.json](dev_eval.json) |
| All sample mismatches, denominators and intervals | [regression_round1.json](regression_round1.json), [regression_round2.json](regression_round2.json) |
| Failed overall gate | [acceptance.json](acceptance.json) |
| Real run logs and synthetic alert probes | [events.jsonl](events.jsonl), [alert_examples.json](alert_examples.json) |

The inventory is not newly invented adjudication. The 71 unassessed calls remain
available for a future source-first sample after a semantic model is frozen.
None has been certified correct simply because the pipeline processed it.

## Human Review

Run `py -m solution triage --reviewer Vaibhav` after `py -m solution review`.
Use `--key "call-004#23#bug"` to focus on one proposal. The reviewer sees source
quotes/turns, priority, existing-issue context, similarity and both payload previews.
Approve, reject, skip or quit; rejection requires a reason. The command records
identity, timestamp, elapsed time and proposal hash atomically, without calling
either sink. Only a later explicit `apply` writes approved items.

The committed session is **automated simulation, not human sign-off**. Its near-zero
elapsed values measure scripted input, not usability. A real timed review by the
candidate remains required. Legacy manually edited decisions lack hash/timing guarantees.

An [assisted session](human_review_session.json) was started and ended without
approvals or rejections: one proposal was skipped. It is retained as incomplete,
not human sign-off or a review-speed measurement. No sink writes occurred.

Concrete corroboration: [call-004](../../../transcripts/call-004.md) says,
"That would explain the exact seven-hour thing. It's not random, it's a consistent shift."
It matches [existing issue PROJ-101](../../../data/existing_issues.json) at
**0.271288**, above **0.20**. The review view includes the existing timezone issue,
`jira_preview: null`, and a Slack corroboration. No duplicate ticket is created.

## Reliability and Monitoring

Tests in [test_orchestrator.py](../../tests/test_orchestrator.py) inject failure
after Jira/Slack writes and before local checkpoints. Stable delivery IDs and
payload hashes reconcile retained receipts, leaving exactly one record per sink.
Malformed/conflicting receipts and changed hash-bound approvals fail closed.
Scope: one writer, stable keys and intact local receipt logs. This is not a claim
of remote exactly-once delivery, concurrent-writer safety or power-loss durability.

For real sinks, persist an approved payload and per-sink outbox intent in one
database transaction. Workers send with provider idempotency keys, query receipts
after ambiguous timeouts, then checkpoint acknowledgements. Jira acknowledgement
unblocks Slack; exhausted retries enter a dead-letter queue for operator resolution.

[Pipeline Health](../../../../../.github/workflows/pipeline-health.yml) schedules
an hourly review-only canary, retains evidence and maintains one operator-alert
GitHub issue. It closes that issue on recovery and never runs `apply`. YAML and
the no-apply guard were checked locally. **Not deployed or cloud-tested:** no push
was authorized. Enable fork Actions, publish the workflow to the fork's default
branch, subscribe to notifications, and test manual dispatch before relying on it.
Fresh runners do not replace a persistent production queue or external dead-man monitoring.

## Error Breakdown

Current round-2 failures are retained, not relabeled:

| Calls | Measured discrepancy |
|---|---|
| 023 | Custom-profile-field Feature missed; 2 extra low-confidence proposals |
| 034 | Coach-filter reset Bug missed; 2 extra fragments/follow-ups |
| 047 | UTC/report-timezone corroboration to PROJ-101 missed |
| 053 | Webhook corroboration to PROJ-087 missed; recap filed as new |
| 132 | Automatic release of no-show calendar slots Feature missed |
| 028, 039, 055, 057 | 4 additional unmatched proposals |

These are end-to-end action/evidence mismatches, not proof that extraction alone
caused every error. Semantic extraction and dedup must be evaluated together.
Adding synonyms for these inspected failures would not prove generalization.

## Free Model Research

No paid API was used. The selected experiment was
[Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507),
an Apache-2.0, non-thinking instruction model, with
[Unsloth Q4_K_M weights](https://huggingface.co/unsloth/Qwen3-4B-Instruct-2507-GGUF).
The machine reports about 32 GB RAM and an Intel Arc integrated GPU. A 2.5 GB
quantization was a feasible initial benchmark, not a proven quality choice.

Downloaded size: **2,497,281,120 bytes**. Local SHA-256 matched the publisher LFS hash:
`3605803b982cb64aead44f6c1b2ae36e3acdb41d8e46c8a94c6533bc4c67e597`.
The official llama.cpp b11342 Vulkan executable was blocked by Windows as a virus
or potentially unwanted application. No exclusion, disabled protection or renamed
executable was used. The user chose to leave inference blocked. The model has
**not run**; neither extraction accuracy nor latency is available.

[Ollama's documented localhost API](https://docs.ollama.com/openai) is another
supported no-key option, subject to an approved installation. Configure an
approved server's actual model name and complete endpoint in
`PIPELINE_OPENAI_MODEL` and `PIPELINE_LLM_API_URL`, set `PIPELINE_JUDGE=llm`, and
choose an explicit timeout. The transport is covered by mock-based tests only.
Model-card benchmarks are not results on this assignment.

## Reproduce and Finish

From `take-homes/applied-ai-engineer/`:

```sh
py -m unittest discover -s solution/tests -q
py -m solution.eval.run_eval --repeat 2 --output solution/artifacts/resubmission/dev_eval.json
py -m solution.eval.run_corpus --output-dir solution/artifacts/resubmission --demo-decisions solution/demo/review_decisions_excerpt.json
py -m solution.eval.run_holdout regression --assessment-dir solution/eval/holdout --repeat 2 --output solution/artifacts/resubmission/regression_round1.json
py -m solution.eval.run_holdout regression --assessment-dir solution/eval/holdout_round2 --repeat 2 --output solution/artifacts/resubmission/regression_round2.json
```

Use `python3` instead of `py` outside Windows. These commands isolate runtime
state and stub outboxes. Timestamps and automated timing vary; decisions and
metrics should agree. Prior evidence outside this directory remains unchanged.

Before claiming readiness: run the approved free model, compare dev/regression
behavior, freeze implementation/configuration, select a fresh sample excluding
all inspected calls, obtain source-first human annotations, seal before scoring,
and run at least twice against the unchanged 0.85 gates. Retain failures. Complete
a real timed human review and activate/test the scheduler. A hiring panel, not
this repository or its assistant, determines the final score.