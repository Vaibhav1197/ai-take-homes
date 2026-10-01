# Write-up: The June Tapes

**Time spent:** Initial implementation approximately 4 hours, estimated from author timestamps, not a time log. Additional remediation on 2026-10-01 was not separately time-tracked. This exceeded the suggested timebox.

**Start here:** [EVAL.md](EVAL.md) contains denominators, acceptance rules, two-run numbers and known limits. [artifacts/README.md](artifacts/README.md) maps the full-corpus evidence. [README.md](README.md) has configuration and usage.

**Current acceptance fails:** a bounded repair raised round-1 (now tuned-on) recall from 28.6% to 85.7%, but a second, fresh 24-call sample untouched by the repair still finds 6 matches, 9 extras and 5 misses (54.5% recall, 40.0% precision). Processing success and green dev tests do not establish generalization.

From `take-homes/applied-ai-engineer/`, with Python 3.11+ (stdlib only):

```sh
python -m unittest discover -s solution/tests -q
python -m solution.eval.run_eval --repeat 2 --output solution/eval/results.json
python -m solution.eval.run_corpus --demo-decisions solution/demo/review_decisions_excerpt.json
```

On Windows use `py` instead of `python` if needed. These evidence commands use temporary state and isolated local stub outboxes; they do not approve or change the normal runtime queue.

## What I built and the key design decisions

A pipeline over BetterBark's 140 call transcripts: **ingest → judge → de-dup → human review gate → apply**.

Typed speaker-aware ingestion feeds a pluggable judge. External topic fences and nearby signal clusters scope suppression locally. TF-IDF/cosine dedup uses **0.20** against existing, filed and pending issues, with same-call duplicate collapse. A durable ledger records `file-new`, `file-new-low`, `corroborate` and `none`. Reviewers edit `pending` to `approved`/`rejected`; only approved items reach Jira/Slack stubs.

## Where AI is, and isn't, in the pipeline

The deterministic default was repaired after root-causing exact source quotes: added vocabulary for previously invisible reports, a consistent product-noun gate, negated-bug-word stripping, and narrow follow-up/recap suppression (see EVAL.md). Re-scored on the same tuned sample, recall rose from 28.6% to 85.7%. A second, fresh 24-call sample with zero influence on the repair still shows real gaps: 54.5% recall, 40.0% precision. The remaining failures are mostly the same bug reported in different words (keyword matching doesn't generalize across paraphrase) and recap turns misread as new asks. Five earlier audits and 24 round-1 calls are now regression data; 71 calls remain fully unassessed. The optional `LLMJudge` shares the interface and priority calculation but is not live-tested. Transcript quotes remain the evidence with either judge.

## The hardest engineering problem (not the hardest prompt)

Segmentation must suppress chatter without merging distinct issues. An external-speaker fence fixed call-008; a gap increase from 6 to 8 was reverted after confusing Azure AD with Okta. This revision exposed mixed-tier precision and positive-only hard cases: the stricter baseline found 10 extras among 24 predictions. Grounding rules removed those extras. An initial filter lost the genuine timezone report; a regression test drove the repair. Original labels remain unchanged, and before/after artifacts preserve the failures.

## Idempotency, safe re-runs, and partial failure

Keys use `call_id#primary_turn_index#signal_type`. They require stable transcript identity and primary turns; they are not semantic hashes or guaranteed stable across different judges. One writer per ledger is assumed.

State uses a flushed/fsynced temporary file and atomic `os.replace`. On Windows, replacement retries `PermissionError` up to six attempts, 50ms apart, then raises; temporary files are cleaned up. Antivirus/indexer interference was a suspected cause, not proven. Failures are isolated per call/decision and exposed through counts and nonzero CLI exits.

Jira success is now persisted before Slack is attempted, so an ordinary Slack failure/retry reuses the ticket. Pending targets resolve across apply batches; unresolved targets fail closed. Tests cover both. **Not exactly-once delivery:** a crash between a remote side effect and its local checkpoint can still duplicate a ticket or notification. Production needs sink idempotency/reconciliation and a transactional outbox.

## What the eval catches, what would slip through, and reliability across repeated runs

Two fresh dev runs each produced **TP=14, FP=0, FN=0** and passed ten hard cases. A fresh, untouched 24-call sample instead gives **40.0% precision, 54.5% recall and 84.6% negative-call accuracy** twice (identical runs), below preregistered 0.85 gates. Low-confidence extras count as false positives. The corpus command now fails on failed, missing or stale semantic evidence, and the fresh sample is now the default gate — the earlier tuned sample is correctly locked out of re-certification by its own integrity seal. Source/label/evaluator hashes prevent silent changes; unfavorable results are retained. Lexical matching has a measured generalization ceiling (the same bug, reworded, was still missed); same-agent annotation requires human calibration. [EVAL.md](EVAL.md) gives the protocol and disagreements.

`python -m solution monitor` checks correlated run/call counts, freshness, failures, candidate-rate drift and review noise, emitting JSON and nonzero exit on alerts. An external scheduler must invoke it. Current health is **warning**: the low-confidence share of the queue is above the 25% limit. Source-backed call-040 miss evidence and a synthetic wrong-label control distinguish system errors from annotation-review questions without altering supplied labels.

## How I validated it actually works

**209 tests** passed, including temporary filesystem integration and mocked failures. Full run: **140 processed, 0 failed, 228 candidates, 128 suppressed, 6 collapsed, 94 queued** (42 new, 30 low-confidence new, 22 corroborations). Rerun: **0 newly queued**, identical ledger and review decisions. [Clean-source verification](artifacts/validation.json) checks reproducibility, not semantic acceptance.

The [demo](demo/README.md) simulates approvals: 1 ticket, 1 corroboration, 1 rejection; second apply adds no records. Pending items never write. It is not human sign-off. Source-linked queue entries include verbatim evidence; estimated review time is 45-90 seconds each, not a measured usability result.

## AI-tool disclosure

Tool: **GitHub Copilot, agentic mode**, for implementation, tests, eval, source inspection, generated evidence and documentation.

**Ownership:** I supplied the assignment and hiring feedback and delegated implementation and investigation to Copilot. Copilot authored remediation, five regression annotations and 24 source-first annotations. These and demo decisions require my review; I do not claim to have personally designed every rule or manually reviewed the full corpus.

**Rejected output:** The gap-widening experiment was reverted; the broad suppression proposal required a narrower repair after dropping the timezone report. Inflated precision and unqualified generalization/exactly-once claims were corrected. Tests and preserved artifacts, not agent assurances, support acceptance.

## What I'd do with another day, and what I deliberately left out

Next: independently adjudicate labels, improve contextual extraction and compare the real LLM judge, then validate on fresh data without recycling inspected failures as holdout. Delivery reconciliation and review UX follow. No passing private-holdout, production-readiness or unattended-filing claim is warranted: the default judge's failures are now measured, not merely suspected.
