# Demo: explicit review decisions and repeat-safe apply

This refreshed demo supersedes the original 183-item snapshot. It uses current pipeline outputs over the real supplied transcripts, but **the three review decisions are agent-authored demonstration choices, not human sign-off**. They must not be applied to the normal runtime queue without review.

## Reproduce

From `take-homes/applied-ai-engineer/`, run:

```sh
python -m solution.eval.run_corpus --demo-decisions solution/demo/review_decisions_excerpt.json --demo-output-dir solution/demo
```

The generator starts with fresh temporary state, runs all 140 calls twice, verifies zero writes while decisions are pending, then applies the explicit [manifest](review_decisions_excerpt.json) to isolated real stub sinks. Finally it applies again and compares entire outboxes. No live API or existing runtime ledger is touched.

| Key | Decision | Reason |
|---|---|---|
| `call-011#41#bug` | Approve new Bug | Apostrophes truncate profile links and cause repeatable 404s for 31 members. |
| `call-004#23#bug` | Approve corroboration | Scheduled-report timezone drift matches PROJ-101; no second ticket. |
| `call-008#57#bug` | Reject standalone filing | The typo is real but deferred to a cosmetic batch; this is a review-policy choice, not a false-positive claim. |

## Reviewer surface

[review_queue_excerpt.md](review_queue_excerpt.md) contains the actual entries with source links, inclusive zero-based turn ranges, target, priority, rationale and verbatim evidence. For example, call-011 includes: "Everything after the apostrophe is gone" and the resulting 404; its source is [call-011](../../transcripts/call-011.md).

Estimated review time: **45-90 seconds per straightforward entry**, longer if the target match is ambiguous. This is a planning estimate, not a measured user study. At 83 queued items the estimate is roughly 62-125 minutes before difficult cases; the 25 low-confidence entries are a real workload warning, not free recall. Confidence values are rule scores/similarities, not calibrated probabilities.

## Observed output

- [jira_outbox_excerpt.jsonl](jira_outbox_excerpt.jsonl): **1** ticket, for call-011.
- [slack_outbox_excerpt.jsonl](slack_outbox_excerpt.jsonl): **2** notifications, one filing and one corroboration.
- The rejected typo and all other pending items produce no writes.
- Second apply: **0** new filings and **0** new notifications; complete outbox contents remain identical.

[full_run.json](../artifacts/full_run.json) records both apply summaries and before/after counts. [EVAL.md](../EVAL.md) explains the regression fixes, sampling limits and remaining checkpoint crash window.
