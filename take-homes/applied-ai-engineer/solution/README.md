# Solution: The June Tapes

Turns BetterBark's call transcripts into de-duplicated, human-reviewed Jira/Slack payloads. See [`WRITEUP.md`](WRITEUP.md) for design decisions, the eval results, and the AI-tool disclosure. This file is the practical "how to run it" reference.

Python 3.11+, standard library only (no third-party dependencies, no `pip install` needed).

For the latest evidence, start with [artifacts/resubmission/README.md](artifacts/resubmission/README.md). [EVAL.md](EVAL.md) and [artifacts/README.md](artifacts/README.md) retain the earlier evaluation history.

**Not yet passing semantic acceptance:** current regression on the previously fresh second sample still finds 6 true positives, 9 false positives and 5 misses. A free local model path is implemented but inference was blocked by Windows security. The corpus command exits 1 despite processing all 140 calls successfully. See the [current verdict](artifacts/resubmission/acceptance.json); UX and reliability improvements are not evidence of improved generalization.

## Quickstart

From the `take-homes/applied-ai-engineer/` folder:

```
py -m unittest discover -s solution/tests   # 225 tests
py -m solution.eval.run_eval --repeat 2 --output solution/artifacts/resubmission/dev_eval.json
py -m solution.eval.run_corpus --output-dir solution/artifacts/resubmission --demo-decisions solution/demo/review_decisions_excerpt.json
py -m solution.eval.run_holdout regression --assessment-dir solution/eval/holdout_round2 --repeat 2 --output solution/artifacts/resubmission/regression_round2.json
py -m solution review                       # ingest + judge + de-dup -> queue for human review
py -m solution triage --reviewer "Vaibhav"   # inspect source/payloads; approve, reject, skip or quit
py -m solution apply                        # act on approved decisions -> stubs/outbox/*.jsonl
py -m solution monitor --expected-calls 140 --max-age-seconds 3600
```

On macOS/Linux, use `python3` instead of `py`. Check out the submission branch, not the fork's unchanged `main`. Evidence commands use isolated temporary state; `review`/`apply` use the normal configured state. `monitor` returns 1 on alerts (the measured low-confidence backlog currently warrants a warning). A scheduler must run it independently and notify an operator on nonzero exit. Set freshness and expected coverage to the actual schedule.

`py -m solution review` is safe to re-run any time (including on a schedule): already-decided or already-filed candidates are skipped, never re-queued or re-filed.

`triage` shows the source quote and turn span, priority, dedup target and rationale,
and exact proposed Jira/Slack payloads. It records reviewer identity, UTC time,
elapsed review seconds, a note, and the proposal hash with an atomic write.
Rejection requires a reason. Skipping, quitting or interrupted input never approves.
The command never invokes either sink; `apply` is a separate explicit step.
Hash-bound approvals fail closed if the proposal changes. Legacy manually edited
decisions remain supported but have no timing or hash guarantee. Use one writer
at a time; do not run triage concurrently with review/apply.

## Project structure

```
solution/
  pipeline/
    models.py           # Turn/Transcript/Candidate/Decision -- shared, dependency-free data shapes
    ingest.py            # parses transcripts/*.md into Transcript objects
    judge_base.py         # IssueJudge Protocol -- the pluggable judge boundary
    heuristic_judge.py    # default IssueJudge: deterministic keyword/rule engine
    keywords.py           # phrase lists the heuristic judge matches against
    llm_judge.py          # optional IssueJudge backed by a real model call (env-gated)
    dedup.py              # TF-IDF + cosine matching against existing/filed issues
    text_utils.py         # hand-rolled TF-IDF (stdlib only)
    state_store.py        # durable ledger: idempotency + partial-failure recovery
    review.py              # renders review_queue.md, reads back review_decisions.json
    payloads.py            # builds Jira/Slack payload dicts from a Decision
    orchestrator.py        # wires the stages above into run_review() / run_apply()
    logging_utils.py       # structured JSONL event log
    config.py              # env-driven Config (12-factor: config lives in the environment)
  cli.py / __main__.py     # `py -m solution {review,apply}`
  eval/run_eval.py          # precision/recall/F1 + named hard cases + --repeat stability check
  eval/run_corpus.py        # full-run artifacts and fail-closed semantic acceptance
  eval/run_holdout.py       # freeze, seal and score a source-annotated sample
  eval/holdout/             # protocol, sample, annotations and seal
  tests/                    # 225 unit and integration tests
  demo/                     # a curated, real excerpt of one review -> apply run (see demo/README.md)
  artifacts/                # full-corpus outputs, per-call coverage, rerun and alert evidence
  EVAL.md                   # denominators, gates, two-run results and audit limits
  state/                    # normal runtime ledger + logs (gitignored)
  WRITEUP.md
  README.md                 # this file
```

## Configuration (environment variables)

Every path/tunable has a working default (this repo's own `transcripts/`/`data/`), so nothing below is required to just run it. All are read once per CLI invocation by `pipeline/config.py`.

| Variable | Default | Purpose |
|---|---|---|
| `PIPELINE_JUDGE` | `heuristic` | `heuristic` or `llm` — which `IssueJudge` to use |
| `OPENAI_API_KEY` | *(none)* | required for remote LLM endpoints; not required for localhost |
| `PIPELINE_OPENAI_MODEL` | `gpt-4o-mini` | model name passed to `LLMJudge` |
| `PIPELINE_LLM_API_URL` | `https://api.openai.com/v1/chat/completions` | OpenAI-compatible endpoint; HTTP allowed only on loopback |
| `PIPELINE_LLM_TIMEOUT_SECONDS` | `60` | positive finite model-call timeout; raise explicitly for slower local inference |
| `PIPELINE_TRANSCRIPTS_DIR` | `transcripts/` | where to read `call-*.md` from |
| `PIPELINE_EXISTING_ISSUES` | `data/existing_issues.json` | de-dup seed corpus |
| `PIPELINE_DEV_LABELS` | `data/dev_labels.json` | used by the eval, not the pipeline itself |
| `PIPELINE_SIMILARITY_THRESHOLD` | `0.20` (see `dedup.py`) | TF-IDF cosine threshold for a de-dup match |
| `PIPELINE_STATE_PATH` | `solution/state/pipeline_state.json` | the idempotency ledger |
| `PIPELINE_REVIEW_QUEUE` | `solution/state/review_queue.md` | human-readable queue |
| `PIPELINE_REVIEW_DECISIONS` | `solution/state/review_decisions.json` | human-edited decisions |
| `PIPELINE_LOG_PATH` | `solution/state/events.jsonl` | structured event log |

Overriding paths is mainly how the eval runs against a scratch ledger without ever touching the real one — see `eval/run_eval.py`.

For an approved local runtime, set `PIPELINE_JUDGE=llm`, the actual server model
name in `PIPELINE_OPENAI_MODEL`, and its complete chat-completions URL in
`PIPELINE_LLM_API_URL`. No paid key is needed. Use fresh state when comparing
judges; primary-turn identity can differ. Run dev and regression evaluations
before freezing a new assessment. No automatic fallback hides model failures.
The attempted Qwen3 runtime was blocked; see the [research record](artifacts/resubmission/README.md#free-model-research).

## Notes

### Scheduled Monitoring

[Pipeline Health](../../../.github/workflows/pipeline-health.yml) runs hourly and
on manual dispatch: tests, a fresh review-only batch, health checks, retained
artifacts, and one maintained GitHub issue for operator alerts. Recovery closes
the alert. It never applies approvals. Subscribe to repository Issues/Actions
notifications to receive the alert; a failed alert-routing step also fails the job.

This workflow is configuration, not a deployed service in the local branch.
After publishing, enable Actions on your own fork and dispatch the workflow once.
Scheduled runs require the workflow on that fork's default branch; fork schedules
are disabled by default. Do not open a PR against the upstream assignment repo.
Runners use isolated state, so this is an extraction/health canary, not a durable
production review queue. A production deployment must mount persistent state and
have an external dead-man alert for scheduler-wide outages. Current heuristic
review-noise warnings are real and should not be silenced by raising thresholds.

- `solution/state/*` and `stubs/outbox/*.jsonl` are gitignored: they're run-specific (timestamps, machine-local paths), not source. [`solution/demo/`](demo/README.md) is a small, real, checked-in excerpt of one full run so the human-review gate and its outputs are inspectable without re-running anything.
- No CI or scheduler is deployed. Run the suite, two-run eval and full-corpus evidence command before resubmitting. Tests include real temporary filesystem integration; no API credentials are required for the default judge.
