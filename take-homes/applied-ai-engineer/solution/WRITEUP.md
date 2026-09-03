# Write-up: The June Tapes

## What I built and the key design decisions

A pipeline over BetterBark's 140 call transcripts: **ingest → judge → de-dup → human review gate → apply**.

- `pipeline/ingest.py` parses `[EXTERNAL]`/`[INTERNAL]`-tagged transcripts into typed `Turn`/`Transcript` records.
- `pipeline/heuristic_judge.py` (the shipped default `IssueJudge`) finds candidate bugs/features via two-level segmentation: coarse "topic blocks" on discourse markers ("one more thing", "second thing", ...) as an outer fence, then proximity-clustering of keyword-bearing turns *within* a block. This lets one call surface several distinct issues and scopes suppression checks (retracted / already-fixed / hearsay / prompt-injection) to the right few turns instead of the whole call.
- `pipeline/dedup.py` matches candidates against `data/existing_issues.json` with hand-rolled TF-IDF + cosine similarity (stdlib only) — no embeddings API, deterministic, fast enough at this corpus size.
- `pipeline/state_store.py` is a durable, atomically-written ledger and the single source of idempotency truth (detail below).
- `pipeline/review.py` renders a human-readable `review_queue.md` and a `review_decisions.json` a reviewer edits (`pending` → `approved`/`rejected`); `pipeline/payloads.py` + `stubs/` only ever fire for `approved` decisions.
- The decision vocabulary mirrors `data/dev_labels.json` exactly: `file-new` / `file-new-low` / `corroborate` / `none`. `file-new-low` is a deliberately wider net for cheap human review, not a confident final call — and the eval (below) treats it that way too.
- The judge is pluggable behind one `Protocol` (`judge_base.py`): `HeuristicJudge` (default) and `LLMJudge` (env-gated via `PIPELINE_JUDGE=llm` + `OPENAI_API_KEY`, stdlib `urllib` only) both implement `find_candidates(transcript) -> list[Candidate]`; `orchestrator.py` cannot tell them apart.

## Where AI is, and isn't, in the pipeline

No LLM call sits on the default hot path. The shipped judge is deterministic keyword/pattern matching over verbatim transcript text, chosen because: it's fully reproducible (a flaky judge makes "does the eval pass" unanswerable); it's auditable (`keywords.py` is a plain-English list a reviewer can read to see exactly why a call was flagged); it has zero cost/latency/network dependency; and the labeled dev set is small and pattern-shaped enough that rules tuned against it generalize reasonably (numbers below). The raw transcript is always the source of truth — snippets that reach Jira/Slack are verbatim quotes, never a paraphrase, regardless of which judge produced the turn span.

`LLMJudge` is fully built and unit-tested as a real, equal alternative (`pipeline/llm_judge.py`), off by default. Even there, priority is *not* delegated to the model: it reuses the same deterministic `estimate_priority()` the heuristic judge uses, so "never inflate priority from a customer's own dramatic framing" is a judge-independent guarantee rather than something that needs re-prompting-for and re-verifying per judge.

AI (GitHub Copilot, agentic) wrote essentially all of this code under my direction — full disclosure below.

## The hardest engineering problem (not the hardest prompt)

Building the eval harness surfaced a real, generalizable bug in the segmentation logic, in two parts:

1. **call-008**: one typo report was being split into two low-content candidates. Root cause, found by reading the raw transcript turn-by-turn: the topic-block segmenter treated *any* turn matching a discourse marker ("anything else", "while I have you") as a new-topic fence — including the **internal rep's own wrap-up question**, not just a customer introducing a new topic. Fix: only external-speaker turns can open a new block. Verified with the full unit suite (no regressions) and the eval (precision 0.56 → 0.58 from this fix alone).
2. **call-011**: a separate, genuine gap in proximity clustering (8 turns, one past the merge threshold). I tried the obvious global fix — widen `_CLUSTER_MAX_GAP` from 6 to 8 — and it worked for call-011, but the eval caught a *worse* regression: call-010's Azure AD bug then wrongly merged into the unrelated PROJ-064 (Okta) tracked issue, an explicit hard requirement. **I reverted the change** and left call-011's split as a documented, understood limitation rather than trading one false positive for a worse one. The human-review gate is the correct backstop for exactly this case — demonstrated live in `solution/demo/`.

The engineering lesson, not a prompting one: a promising-looking global parameter fix has to be measured against a fixed regression harness before being trusted, and being willing to reject your own fix is part of the job.

## Idempotency, safe re-runs, and partial failure

Every candidate gets a stable key, `f"{call_id}#{primary_turn_index}#{signal_type}"` (`state_store.candidate_key`) — anchored to *content*, not judge wording, so it survives a future non-deterministic judge shifting a window boundary by a turn. The ledger (`solution/state/pipeline_state.json`) is the *only* source of "have I already dealt with this" truth: the Jira/Slack stubs are deliberately naive and don't de-duplicate themselves (by their own docstrings), so re-running the pipeline can never re-file or re-notify anything already recorded. Every state transition is an atomic temp-file-then-`os.replace` rewrite, so a crash mid-batch leaves everything-before-it durably intact, not corrupted.

Both `run_review` and `run_apply` wrap each transcript/decision in its own `try/except`: one bad transcript or one bad decision is logged (`call_failed` / `apply_failed`) and skipped, the rest of the batch still completes. On Windows, `os.replace` intermittently raised a transient `PermissionError` under rapid repeated writes (AV/indexer briefly holding a handle) — found empirically on a full 140-call run, fixed with a short bounded retry rather than letting a transient OS race look like a pipeline failure. Verified idempotency directly, not just in unit tests: running the full 140-transcript corpus twice back-to-back reports 219 candidates found on the fresh run and **0 newly queued, everything "already processed"** on the immediate re-run.

## What the eval catches, what would slip through, and reliability across repeated runs

`solution/eval/run_eval.py` replays the **real** `orchestrator.run_review()` (not a reimplementation) against calls 1–15 vs. `data/dev_labels.json`, so the eval and production can never drift apart. Current numbers: **precision = 0.93, recall = 1.00, F1 = 0.97** (TP=14, FP=1, FN=0) on the confident tier (`file-new`/`corroborate`); recall covers *all* labels regardless of tier. Pass/fail definition: precision ≥ 0.85 and recall ≥ 0.85, **and** all 8 named hard cases pass (independent reports of one bug merging; genuinely distinct bugs that share vocabulary staying apart; Bug-vs-Feature classification; already-shipped suppression; prompt-injection resistance; internal-only calls producing zero tickets; priority not inflating from customer drama), **and** `--repeat N` produces an identical decision fingerprint across runs.

What would slip through: the one documented call-011-style clustering-gap case above; keyword-homonym misses inherent to a rule-based judge; and, by design, some `file-new-low` noise reaching human review rather than being silently dropped — that tier is deliberately a wide net, so the review gate, not the judge, is its real precision backstop. Reliability across repeated runs: the heuristic judge is deterministic, so `--repeat 5` always produces an identical fingerprint (verified). Swap in a probabilistic judge (`LLMJudge`, temperature 0 but not bit-guaranteed) and the *same* harness immediately shows instability as a diverged fingerprint — that's the intended mechanism for measuring a model judge's flake rate (e.g. nightly `--repeat 5–10`, alert on divergence).

## How I validated it actually works

170 unit tests (pure, fast, stdlib `unittest`, no real network/filesystem/clock) across every module. The eval above, against real labeled data. The full 140-transcript corpus run twice back-to-back to confirm idempotency empirically, not just in isolated unit tests. And a real end-to-end pass through the human gate: I reviewed and decided a representative slice of the actual review queue (approve a `file-new`, approve a `corroborate`, reject a `file-new-low`) and ran `apply` for real, then inspected the resulting Jira/Slack stub payloads — curated in `solution/demo/` since `solution/state/` and `stubs/outbox/*.jsonl` are gitignored, run-specific artifacts.

## AI-tool disclosure

Tool: **GitHub Copilot, agentic mode** (Claude Sonnet-class model), for this entire solution — pipeline code, tests, eval harness, and this write-up.

**Seams — wrote vs. delegated:** I set every design decision (heuristic-first judge with an `LLMJudge` alternative behind one interface, two-level segmentation, ledger-based idempotency, the tiered confident/low-confidence eval metric, the human-gate file formats) and directed the build step by step; the agent authored the actual code and tests against those decisions. Nothing was accepted un-verified — every change was checked against the unit suite, the eval, or a real end-to-end run before moving on.

**A concrete rejected case:** the `_CLUSTER_MAX_GAP` 6→8 experiment above. The agent proposed and implemented it as a fix for call-011; it looked reasonable in isolation and passed a quick read-through, but measurably regressed a named hard case once run against the eval (call-010 wrongly merging into PROJ-064). I rejected it and reverted, keeping the narrower, correctly-scoped fix plus an honestly documented limitation instead.

**Where AI got it wrong initially:** the original topic-block segmenter (also agent-written, earlier in the build) had the call-008 speaker-blindness bug through 156 passing unit tests — those tests checked segmentation in isolation with contrived examples, not against a real, labeled, end-to-end call. Only a real eval against real transcripts surfaced it. The lesson I'm taking forward: a large green unit-test suite is necessary but not sufficient; it doesn't substitute for an eval against real data.

## What I'd do with another day, and what I deliberately left out

Left out: a click-through review UI over `review_queue.md`/`review_decisions.json` — markdown + JSON is fast enough for this scope, but a real reviewer would want one, since "keep the review fast" was an explicit design goal. `LLMJudge` is built and unit-tested but has no live-network test against a real API by design (no network in unit tests) and hasn't been run against the eval yet.

With another day: (1) run `LLMJudge` through the same eval harness side-by-side with the heuristic judge for a real, apples-to-apples precision/recall comparison; (2) replace the global `_CLUSTER_MAX_GAP` with a more surgical, per-call post-hoc merge pass that compares nearby candidates' content directly, closing the call-011-style gap without risking the call-010-style regression; (3) hand-spot-check a slice of the 125-call holdout to catch error classes the 15-call dev set doesn't represent; (4) the review UI above.
