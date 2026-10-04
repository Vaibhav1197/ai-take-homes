# Evaluation and resubmission evidence

## Current Revision: 2026-10-02

**Acceptance remains FAIL.** [Current evidence](artifacts/resubmission/README.md)
includes 225 passing tests, two passing dev runs, full 140-call coverage, the
actual simulated triage workflow, sink-checkpoint fault tests, and historical
sample regression runs. Round 2 remains TP=6/FP=9/FN=5 in both fresh-state runs:
40.0% precision and 54.5% recall. No extraction-quality improvement is claimed.

Both previously inspected samples are now explicitly regression data. Use
`run_holdout regression` to compare current code against unchanged historical
labels. Normal `evaluate` and corpus acceptance still reject stale source seals;
do not reseal inspected samples to present them as fresh. Local-model inference
and independent human annotation remain blocked/pending. The detailed error
breakdown and reproducible commands are in the current evidence index.

## Historical Snapshot: 2026-10-01

The sections below preserve the earlier measurements and protocol. References
to a fresh sample, 209 tests, no review interface, or unreconciled checkpoint
windows describe that revision, not the current implementation.

**Historical acceptance: FAIL.** Full-corpus execution is reproducible, but the then-fresh 24-call sample failed the 0.85 gates (40.0% precision, 54.5% recall). [Historical acceptance.json](artifacts/acceptance.json) is retained unchanged; coverage alone is not acceptance.

## Scope and acceptance

The unit is an issue, not a call. The provided development set has **15 calls, 30 labels, 14 actionable issues and 16 `none` labels**. The same data was used to tune the heuristic: these are development results, not an unbiased accuracy estimate. No provided label or original exercise file was changed.

Matching is one-to-one within a call: action class and issue type must agree; new issues must include curated symptom anchors in their evidence, and corroborations must match the expected target. `file-new-low` can match a new issue, but **every unmatched low-confidence item is a false positive in the all-queue metric**. The lexical symptom anchors are inspectable in [run_eval.py](eval/run_eval.py); they are imperfect proxies for semantic identity, not an independent model judge. The five supplemental cases use separate annotations.

Pass requires **every** repetition to process all 15 calls without failure, confident precision >=0.85, all-queue precision >=0.85, recall >=0.85, all ten hard cases passing, and at least two fresh-state runs with identical complete decisions (including evidence, priority, type and target). A single run cannot demonstrate stability. F1 uses all-queue precision and recall. Precision with no predictions is defined as 1; missed expected issues still fail recall. CLI exit 0 means these gates passed; exit 1 means failure.

## Measured results

| Version / run | Expected issues | Queued | TP | FP (all tiers) | FN | All-queue precision | Recall | F1 | Hard cases |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Stricter baseline, run 1 | 14 | 24 | 14 | 10 | 0 | 0.5833 | 1.0000 | 0.7368 | 6/10 |
| Stricter baseline, run 2 | 14 | 24 | 14 | 10 | 0 | 0.5833 | 1.0000 | 0.7368 | 6/10 |
| Revised, run 1 | 14 | 14 | 14 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 10/10 |
| Revised, run 2 | 14 | 14 | 14 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 | 10/10 |

Revised confident tier: 13 predicted, 13 matched, 0 extra. Low-confidence tier: 1 predicted, 1 matched, 0 extra. Both are reported separately; neither is removed from total workload. The original mixed-tier precision figure is superseded.

Both revised fingerprints are `e66efdd4043f04829bcf129f675fbbf7729417f0c46920ea02ce6ba2e0ebce41`: **0/1 comparisons diverged across two runs**. This demonstrates deterministic repeatability, not a statistically established model failure probability. The optional LLM judge has not been live-evaluated.

Full machine-readable results, input hashes, predictions, denominators, disagreements and assertions: [results.json](eval/results.json). Preserved pre-filter measurements using the corrected matcher and metrics: [baseline.json](eval/baseline.json). The baseline is a historical snapshot; the reproduction command below runs the revised implementation.

The ten hard cases cover injection with a retained genuine report, cross-call clustering, distinct Azure AD versus Okta symptoms, SAML Feature classification, shipped-feature suppression, internal-only calls, cosmetic priority, embedded-email instructions, and two retracted/vague-only calls. Negative cases now check cardinality; the mere presence of one correct ticket is insufficient.

## Full corpus and rerun

| Measure | First review | Same-ledger rerun |
|---|---:|---:|
| Calls discovered / processed / failed | 140 / 140 / 0 | 140 / 140 / 0 |
| Candidates / suppressed | 228 / 128 | 228 / 128 |
| Newly queued | 94 | 0 |
| Already queued / terminal skips | 0 / 0 | 94 / 6 |
| Newly collapsed same-call duplicates | 6 | 0 |
| Jira / Slack writes while pending | 0 / 0 | 0 / 0 |

First-run accounting: `228 = 128 suppressed + 6 collapsed + 94 queued`. Rerun: `228 = 128 suppressed + 94 already queued + 6 terminal skips`. No entire calls are skipped; all are examined again. Both ledger hashes agree with zero added, removed or changed keys, and unchanged review decisions.

Queue actions: **42 file-new, 30 file-new-low, 22 corroborate** (up from 39/25/19 before the repair, consistent with recovering previously-missed reports). These are counts, not verified correctness labels. The full queue and every per-call completion (including calls with no output) are exported in [artifacts](artifacts/README.md).

Explicit demo decisions: one new ticket, one corroboration, one cosmetic rejection. Jira records stay **1 -> 1**, Slack records **2 -> 2** after reapply. The demo uses real local stub validation with temporary destinations, not live services; its approvals are agent-authored examples, not human sign-off. Tests additionally cover Jira success followed by Slack failure and later approval of a dependent corroboration.

## Supplemental audit and disagreement diagnosis

Five calls were selected before reading: 020, 040, 080, 100, 140. Source inspection found two misses and three extras. Those failures were then used for repairs, so the five are now **regression-development data**, not untouched holdout. Source quotes, exact turns and annotations are in [audit_cases.json](eval/audit_cases.json), with [before](eval/audit_before.json) and [after](artifacts/audit.json) outcomes. All five now pass these agent-authored annotations; independent human confirmation remains necessary. The separate assessment below adds 24 source-annotated calls without further pipeline tuning.

- **True miss:** call-040 turns 27/29 explicitly report logout after an iOS update, matching tracked PROJ-160. The earlier pipeline produced no item. That is a missed report supported by source evidence, not a reason to alter the expected result.
- **Bad-label control:** `diagnostic_control` in [results.json](eval/results.json) deliberately changes call-011's expected type to Feature while keeping the actual broken-link/404 evidence and the original Bug label visible. It produces a disagreement and calls for annotation review. This is a **synthetic diagnostic**, not a claim that any supplied label is wrong. Official labels and metrics remain unchanged.
- **Actual system false positives:** the audit preserved call-020's duplicate follow-up, call-100's manual-restoration ask treated as a separate Feature, and call-140's hypothetical breakage. These prompted fixes, not relabeling to excuse the system.

## Bounded repair and a second, fresh validation round

The round-1 failures were root-caused against real source turns (not guessed) and repaired narrowly: new vocabulary for previously invisible reports ("locked out", "vanish"/"disappear", "expired" gated to a nearby product noun, "no bulk", "would give a lot for", "error message"), a uniform product-noun gate for ambiguous hits (fixing an inconsistency where a literal "bug" could never pass it), stripped negated bug words ("nothing broken", "not like anything freezes or errors"), and narrow follow-up suppression for delivery/rollout questions and wrap-up recaps about an already-covered issue. Every fix is grounded in an exact quote and has its own regression test in `test_heuristic_judge.py::TestGeneralizationFixes`. The dev eval and 5-call audit were re-verified after every change and still pass at 100%.

Re-scoring the **same round-1 sample** (now debugging/regression data, not blind) went from TP4/FP5/FN10 to **TP12/FP5/FN2**: precision 44.4%→70.6%, recall 28.6%→85.7%. This shows the fixes work on the cases they were built for. It is explicitly **not** a generalization claim, and round-1's own integrity seal now proves that: attempting to formally re-certify it against the repaired pipeline fails with `"Frozen pipeline changed"`, because its manifest is still hashed against the original source. That lockout is the mechanism working correctly, not a bug — it stops a tuned sample from being silently re-reported as fresh evidence.

A **second, disjoint 24-call sample** (`eval/holdout_round2/`) was frozen with a new seed excluding every call used anywhere above, annotated source-first before any prediction was inspected, and sealed. This sample had zero influence on the repair and is the trustworthy generalization measurement:

| Run | Calls | Expected issues | Predicted | TP | FP | FN | All-queue precision | Recall | No-issue calls correct |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 24 | 11 | 15 | 6 | 9 | 5 | 6/15 = 40.0% | 6/11 = 54.5% | 11/13 = 84.6% |
| 2 | 24 | 11 | 15 | 6 | 9 | 5 | 6/15 = 40.0% | 6/11 = 54.5% | 11/13 = 84.6% |

Both runs are identical. All three 0.85 gates still fail. [holdout.json](artifacts/holdout.json) is this fresh result (the real semantic gate); [holdout_regression.json](artifacts/holdout_regression.json) is round-1's now-locked historical record.

The round-2 failures diagnose a real architectural ceiling, not a short list of missing words:

| Failure | Call | Observed mechanism |
|---|---|---|
| Same bug class as a fixed round-1 case, missed anyway | 034 | Coach-search filter reset described as "gone"/"completely reset", not "vanish"/"disappear" — the exact words the round-1 fix targeted |
| No candidate for explicit issue | 023, 047, 132 | Vocabulary for custom profile fields, UTC-shifted reports and "auto-release"/contraction phrasing ("I'd love") still absent |
| Recap of an already-covered topic misread as new | 028, 053, 055, 057 | A later wrap-up/confirmation turn about an issue already handled earlier in the same call forms its own candidate |

This is the clearest evidence yet that keyword matching does not generalize across paraphrases of the same real-world report. Closing this gap needs either a more general cross-turn "is this the same topic already covered" suppression, or the `LLMJudge`, not more one-off phrase additions — adding a keyword for each new wording chases an unbounded tail and risks exactly the overfitting this process has been guarding against.

## Observability and remaining risk

The corpus coverage check passes, but operational health is **warning**: `LOW_CONFIDENCE_BACKLOG` exceeds the preset 25% limit. Do not silence this by raising the limit to fit the run. Review the backlog, independently sample suppressed and queued items, and measure reviewer acceptance/rejection. Counts can flag suspicious behavior, but only source-backed adjudication can establish semantic errors.

`python -m solution monitor --expected-calls 140 --max-age-seconds 3600` emits JSON and exits 1 on alerts. Configure freshness for the actual schedule; invoke it from an external scheduler so a process that never starts can still be detected. `--baseline-rate` enables a 0.5x-2x candidate-rate check. The healthy rerun rule uses candidates, not newly queued items. [alert_examples.json](artifacts/alert_examples.json) contains explicitly synthetic never-started, stalled, stale, zero-output, noisy and partial-failure probes alongside the real warning in [full_run.json](artifacts/full_run.json).

Remaining limits: a now-measured generalization ceiling in lexical matching (see above), same-agent annotation, single-writer state, stable primary-turn keys, and the remote-write/local-checkpoint crash window. There is no dashboard service, deployed scheduler, calibrated probability score, live LLM result or private-label accuracy claim.

## Reproduce

From `take-homes/applied-ai-engineer/`, Python 3.11+ with standard library only (`py` on Windows):

```sh
python -m unittest discover -s solution/tests -q
python -m solution.eval.run_eval --repeat 2 --output solution/eval/results.json
python -m solution.eval.run_corpus --demo-decisions solution/demo/review_decisions_excerpt.json
python -m solution.eval.run_holdout evaluate --assessment-dir solution/eval/holdout_round2 --repeat 2 --output solution/artifacts/holdout.json
```

All evidence runs use fresh temporary state and isolated outboxes. Current suite: **209 passing tests**; dev eval exits 0. **Corpus acceptance and the fresh round-2 evaluation both exit 1** for measured semantic failures. `run_corpus` now defaults `--assessment-dir` to the fresh round-2 sample (the real gate) and `--regression-assessment-dir` to round-1 (reported, not gating, and correctly locked against re-certification). Timestamps, run IDs and timings differ; decisions, hashes, counts and rerun comparisons should agree. Add `--demo-output-dir solution/demo` only when intentionally refreshing excerpts. Changes must be committed and pushed before the existing PR reflects them.

[validation.json](artifacts/validation.json) records a successful verification from a clean copy of tracked plus new nonignored source files, with no runtime state or outboxes. This is a clean-source test of the pending changes, not a claim that they have already been committed or pushed.