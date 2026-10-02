# Write-up: The June Tapes

**Time spent:** Initial implementation approximately 4 hours, estimated from author timestamps, not a time log. Additional remediation on 2026-10-01 and 2026-10-02 was not separately time-tracked. This exceeded the suggested timebox.

**Start here:** [Current evidence](artifacts/resubmission/README.md) maps the 2026-10-02 changes, measured results and blockers. [EVAL.md](EVAL.md) preserves the evaluation history. [README.md](README.md) has configuration and usage.

**Current acceptance fails:** the previously fresh second sample still finds 6 matches, 9 extras and 5 misses (54.5% recall, 40.0% precision) in two current regression runs. Review UX and delivery reliability are improved; semantic extraction is not yet improved. Neither green tests nor a desired panel score changes this result.

From `take-homes/applied-ai-engineer/`, with Python 3.11+ (stdlib only):

```sh
python -m unittest discover -s solution/tests -q
python -m solution.eval.run_eval --repeat 2 --output solution/artifacts/resubmission/dev_eval.json
python -m solution.eval.run_corpus --output-dir solution/artifacts/resubmission --demo-decisions solution/demo/review_decisions_excerpt.json
```

On Windows use `py` instead of `python` if needed. These evidence commands use temporary state and isolated local stub outboxes; they do not approve or change the normal runtime queue.

## What I built and the key design decisions

A pipeline over BetterBark's 140 call transcripts: **ingest → judge → de-dup → human review gate → apply**.

Typed speaker-aware ingestion feeds a pluggable judge. External topic fences and nearby signal clusters scope suppression locally. TF-IDF/cosine dedup uses **0.20** against existing, filed and pending issues, with same-call duplicate collapse. A durable ledger records `file-new`, `file-new-low`, `corroborate` and `none`.

`triage --reviewer Vaibhav` shows source quotes and turns, priority, the matched issue and similarity, and Jira/Slack payload previews. Approve/reject/skip/quit require no JSON editing; rejection requires a reason. Atomic decisions record identity, UTC time, elapsed seconds and a proposal hash. Changed hash-bound approvals cannot be applied. Review never calls sinks; `apply` remains separate. Legacy manual decisions lack these audit guarantees.

Concrete dedup evidence: call-004 says, **"That would explain the exact seven-hour thing. It's not random, it's a consistent shift."** It matches timezone issue **PROJ-101 at 0.271288**, above 0.20. The [review session](artifacts/resubmission/review_session.json) shows the existing issue, no Jira creation preview, and a corroboration notification.

## Where AI is, and isn't, in the pipeline

The deterministic default still has a measured paraphrase/recap ceiling. Historical repairs and failures are retained in EVAL.md; neither thresholds nor labels were changed to improve the reported score. Both inspected samples are now regression data; 71 calls remain unassessed, explicitly listed in the coverage inventory.

The semantic alternative reads the whole call, returns source-turn citations and re-quotes original external speech. Priority stays deterministic. Invalid types, spans, nonfinite confidence and truncated responses now fail visibly instead of silently losing issues. No automatic heuristic fallback hides model failure. A no-key localhost endpoint is supported. Research selected Qwen3-4B-Instruct-2507 Q4_K_M; its download matched the publisher hash, but Windows security blocked the portable runtime. No protection was bypassed; no inference or quality improvement is claimed.

## The hardest engineering problem (not the hardest prompt)

Segmentation must suppress chatter without merging distinct issues. An external-speaker fence fixed call-008; a gap increase from 6 to 8 was reverted after confusing Azure AD with Okta. This revision exposed mixed-tier precision and positive-only hard cases: the stricter baseline found 10 extras among 24 predictions. Grounding rules removed those extras. An initial filter lost the genuine timezone report; a regression test drove the repair. Original labels remain unchanged, and before/after artifacts preserve the failures.

## Idempotency, safe re-runs, and partial failure

Keys use `call_id#primary_turn_index#signal_type`. They require stable transcript identity and primary turns; they are not semantic hashes or guaranteed stable across different judges. One writer per ledger is assumed.

State uses a flushed/fsynced temporary file and atomic `os.replace`. On Windows, replacement retries `PermissionError` up to six attempts, 50ms apart, then raises; temporary files are cleaned up. Antivirus/indexer interference was a suspected cause, not proven. Failures are isolated per call/decision and exposed through counts and nonzero CLI exits.

Jira success is persisted before Slack. Stable per-sink delivery IDs and payload hashes now reconcile retained stub receipts before retries. Tests inject failures after Jira and Slack writes but before checkpoints: retries leave one record in each sink. Conflicting or malformed receipts fail closed. Pending targets resolve across batches; unresolved targets cannot notify. This is single-writer reconciliation with readable, retained local receipts, not a claim of remote exactly-once delivery. Production needs provider idempotency/search, durable outbox intents, bounded retry and a dead-letter queue; concurrent writers, lost receipts and power-loss durability remain outside the stub guarantee.

## What the eval catches, what would slip through, and reliability across repeated runs

Two fresh dev runs each produced **TP=14, FP=0, FN=0**, ten hard cases passed. Current round-2 regression gives **40.0% precision, 54.5% recall, 84.6% negative-call accuracy** twice, below preregistered 0.85 gates. Every low-confidence extra counts as an FP. The explicit regression mode verifies historical label/input seals but never certifies freshness. Normal acceptance still rejects changed pipeline/evaluator seals; unfavorable results remain committed. Source-first human calibration and a genuinely fresh sample are still required after a model change.

`monitor` checks correlated counts, freshness, failures, drift and review noise. An hourly/manual GitHub Actions canary now retains artifacts and maintains an operator-alert issue; it never applies approvals. It is not deployed: this branch was not pushed and fork schedules need activation. Current health remains **warning** at 30/94 low-confidence proposals, above 25%. Source-backed misses and a synthetic wrong-label control distinguish system errors from annotation questions without changing supplied labels.

## How I validated it actually works

**225 tests** passed. Full run: **140 processed, 0 failed, 228 candidates, 128 suppressed, 6 collapsed, 94 queued** (42 new, 30 low-confidence new, 22 corroborations). Rerun: **0 newly queued**, identical ledger and review decisions. Current [full-run JSON](artifacts/resubmission/full_run.json) records the hashes and per-call outcomes.

The [review-session JSON](artifacts/resubmission/review_session.json) exercises actual triage logic: 1 ticket, 1 corroboration, 1 rejection; second apply adds no records. Pending items never write. Its automated elapsed times are **not human review speed** and its decisions are not human sign-off. A real reviewer must complete the timed workflow before any usability claim.

## AI-tool disclosure

Tool: **GitHub Copilot, agentic mode**, for implementation, tests, eval, source inspection, generated evidence and documentation.

**Ownership:** I supplied the assignment, hiring feedback and no-paid-API constraint, and delegated investigation, code, tests, annotations and documentation to Copilot. I authorized local commits without pushing and chose to leave model evaluation blocked after Windows security rejected the runtime. I do not claim hand-written implementation or personal adjudication of the corpus. Agent-authored labels and demo decisions still need my review.

**Rejected output:** The gap-widening experiment was reverted; the broad suppression proposal required a narrower repair after dropping the timezone report. Inflated precision and unqualified generalization/exactly-once claims were corrected. Tests and preserved artifacts, not agent assurances, support acceptance.

## What I'd do with another day, and what I deliberately left out

Next: run an approved free local model, compare semantic extraction on dev/regression cases, freeze code, then obtain independent source-first labels on a fresh sample. Human review timing and schedule activation remain pending. The 71 unassessed calls were not bulk-labeled by the same coding agent just to make completeness look higher. No passing private-holdout, production-readiness, guaranteed panel score or unattended-filing claim is warranted.
