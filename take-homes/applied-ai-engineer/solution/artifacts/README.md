# Historical Full-run Evidence

For the 2026-10-02 implementation and freshly generated evidence, start with
[resubmission/README.md](resubmission/README.md). The files below are preserved
2026-10-01 snapshots, not certification of the current source tree.

Start with [../EVAL.md](../EVAL.md) for the acceptance rules and measured tables. These are generated outputs from the real pipeline, not hand-written example results.

**Acceptance currently fails.** Full-corpus execution succeeds, and a bounded repair measurably improved generalization, but the fresh round-2 sample still shows 6 TP, 9 FP and 5 FN. Do not present processing success, or round-1's tuned-on numbers, as passing generalization.

| File | What to inspect |
|---|---|
| [full_run.json](full_run.json) | 140 per-call outcomes, dev/holdout counts, source/input hashes, two review summaries, identical-ledger rerun diff, real health warning and demo reapply counts |
| [decisions.json](decisions.json) | Complete pre-approval ledger, including evidence, target, rationale, type and priority for every queued issue |
| [review_queue.md](review_queue.md) | Full source-linked review queue before demo approval |
| [review_decisions.json](review_decisions.json) | Decision file after the explicit three-item demo manifest; other items remain pending |
| [events.jsonl](events.jsonl) | Actual correlated run/call events, including zero-output calls and both apply passes |
| [demo_payloads.json](demo_payloads.json) | One Jira payload and two Slack payloads from real isolated stubs |
| [alert_examples.json](alert_examples.json) | Synthetic fault-injection examples; not actual failures of the full run |
| [audit.json](audit.json) | Five source-reviewed supplemental regression cases with verbatim quotes and actual decisions |
| [holdout.json](holdout.json) | **Fresh round-2** sealed 24-call source-first assessment, two repetitions, 11 expected issues and all mismatches/denominators — the real semantic gate |
| [holdout_regression.json](holdout_regression.json) | Round-1's result against the repaired pipeline: correctly locked out (`"Frozen pipeline changed"`) because it was used for tuning, not a live gate |
| [acceptance.json](acceptance.json) | Combined coverage, regression and semantic verdict, with separate health and human-confirmation fields |
| [validation.json](validation.json) | Actual clean-source-copy test/eval/corpus command outputs, source/decision hash agreement, alert probes and link validation |

`full_run.json.passed` means coverage, pending-gate safety and rerun checks passed. It does **not** mean all issues are correct or all alerts are clear. The corpus CLI also writes `acceptance.json` and exits 1 on failed/missing/stale semantic evidence. Health is false because the low-confidence share of the queue exceeds 25%. Of the original 125-call holdout: 5 are development-audit calls, 24 are round-1 (now tuned-on regression data), 24 are round-2 (fresh, the real gate), 1 (call-051) was previously inspected without formal annotation, leaving **71 calls unassessed**. Official private labels and independent human confirmation remain unavailable.

Rebuild from `take-homes/applied-ai-engineer/`:

```sh
python -m solution.eval.run_corpus --demo-decisions solution/demo/review_decisions_excerpt.json
```

Expected exit is currently 1 for semantic failures, with all reports still written. The command redirects only local stub output paths into temporary storage; normal state and outboxes stay untouched. Omit `--demo-decisions` for zero approvals. Add `--demo-output-dir solution/demo` only to deliberately refresh excerpts. The demo manifest never authorizes applying the normal runtime queue.