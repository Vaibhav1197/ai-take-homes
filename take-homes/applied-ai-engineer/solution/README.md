# Solution: The June Tapes

Turns BetterBark's call transcripts into de-duplicated, human-reviewed Jira/Slack payloads. See [`WRITEUP.md`](WRITEUP.md) for design decisions, the eval results, and the AI-tool disclosure. This file is the practical "how to run it" reference.

Python 3.11+, standard library only (no third-party dependencies, no `pip install` needed).

## Quickstart

From the `take-homes/applied-ai-engineer/` folder:

```
py -m unittest discover -s solution/tests   # 170 tests
py -m solution.eval.run_eval --repeat 5     # eval against data/dev_labels.json
py -m solution review                       # ingest + judge + de-dup -> queue for human review
#   ... edit solution/state/review_decisions.json: "pending" -> "approved" / "rejected" ...
py -m solution apply                        # act on approved decisions -> stubs/outbox/*.jsonl
```

`py -m solution review` is safe to re-run any time (including on a schedule): already-decided or already-filed candidates are skipped, never re-queued or re-filed.

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
  tests/                    # 170 unit tests, one file per pipeline module
  demo/                     # a curated, real excerpt of one review -> apply run (see demo/README.md)
  state/                    # generated ledger + logs (gitignored, run-specific -- see demo/ instead)
  WRITEUP.md
  README.md                 # this file
```

## Configuration (environment variables)

Every path/tunable has a working default (this repo's own `transcripts/`/`data/`), so nothing below is required to just run it. All are read once per CLI invocation by `pipeline/config.py`.

| Variable | Default | Purpose |
|---|---|---|
| `PIPELINE_JUDGE` | `heuristic` | `heuristic` or `llm` — which `IssueJudge` to use |
| `OPENAI_API_KEY` | *(none)* | required if `PIPELINE_JUDGE=llm` |
| `PIPELINE_OPENAI_MODEL` | `gpt-4o-mini` | model name passed to `LLMJudge` |
| `PIPELINE_TRANSCRIPTS_DIR` | `transcripts/` | where to read `call-*.md` from |
| `PIPELINE_EXISTING_ISSUES` | `data/existing_issues.json` | de-dup seed corpus |
| `PIPELINE_DEV_LABELS` | `data/dev_labels.json` | used by the eval, not the pipeline itself |
| `PIPELINE_SIMILARITY_THRESHOLD` | `0.20` (see `dedup.py`) | TF-IDF cosine threshold for a de-dup match |
| `PIPELINE_STATE_PATH` | `solution/state/pipeline_state.json` | the idempotency ledger |
| `PIPELINE_REVIEW_QUEUE` | `solution/state/review_queue.md` | human-readable queue |
| `PIPELINE_REVIEW_DECISIONS` | `solution/state/review_decisions.json` | human-edited decisions |
| `PIPELINE_LOG_PATH` | `solution/state/events.jsonl` | structured event log |

Overriding paths is mainly how the eval runs against a scratch ledger without ever touching the real one — see `eval/run_eval.py`.

## Notes

- `solution/state/*` and `stubs/outbox/*.jsonl` are gitignored: they're run-specific (timestamps, machine-local paths), not source. [`solution/demo/`](demo/README.md) is a small, real, checked-in excerpt of one full run so the human-review gate and its outputs are inspectable without re-running anything.
- No CI is configured for this take-home; run the unit suite and the eval locally (`py -m unittest discover -s solution/tests` and `py -m solution.eval.run_eval --repeat 5`) before every commit — that was the actual workflow used to build this, see the git history.
