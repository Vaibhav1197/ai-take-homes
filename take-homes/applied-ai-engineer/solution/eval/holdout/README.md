# Frozen source-first assessment

This assessment addresses the missing evidence about behavior outside calls 001-015. It is **not the evaluator's private labels, an independent human audit, or proof that all 125 holdout calls are correct**. GitHub Copilot read and annotated these calls in the same session that implemented the assessment harness. Sample predictions were not inspected during annotation; earlier exposure cannot be conclusively excluded.

## Protocol fixed before scoring

- Freeze the current pipeline files, configuration and all 140 input transcripts before labeling. No extraction, suppression, deduplication or priority changes are made for this assessment.
- Exclude calls 001-015, the five earlier development audits (020/040/080/100/140), and previously inspected call-051. Rank the remaining 119 call IDs by SHA256 of `june-tapes-prospective-assessment-v1:call_id` and take 24, independently of outcomes. Do not replace difficult calls.
- Read each selected transcript in full, including late corrections. Record a decision for every call, with exact external source quotes, reasoning and expected issue identities. An empty expected list is a reviewed negative, never a default for an unread call.
- Seal the annotations, manifest and evaluator hashes before the first scored run. The seal detects later edits; it is a local integrity checkpoint, not independent attestation.
- Run the real pipeline over **all 140 calls in fresh temporary state** for each repetition, retaining real cross-call deduplication context. Score only the frozen 24. Never approve or apply outputs.
- Every run must process all inputs with zero failures and reach 0.85 all-queue precision, 0.85 recall and 0.85 no-issue-call accuracy. At least two runs must have identical complete-ledger fingerprints. A zero denominator is reported as unavailable, never a free passing score.

The sample contains **14 expected issues in 13 positive calls and 11 no-issue calls**. Both queued and missed issues can therefore affect the result. The remaining **95 eligible calls are unassessed**, plus excluded call-051 without a formal label. Do not extrapolate sample scores into a correctness claim for the whole corpus.

## Annotation rubric

1. Require a concrete external product symptom or requested missing software capability. Internal suggestions alone, commercial negotiations, content preferences and service work are not product issues.
2. Read the final resolution: retractions, shipped capabilities and customer-only configuration fixes yield no issue. A workaround does not resolve an underlying product defect.
3. Group one root problem and its refinements into one issue. A new capability that remains useful after the defect is fixed can be separate. In call-136, header whitespace rejection and the opaque error are one Bug; non-mutating import validation is a separate Feature. This granularity judgment explicitly needs human confirmation.
4. Match known issues by symptom and scope, not shared vocabulary: Outlook reschedules match PROJ-138; Ping hard locks do not match Okta expiry; goal-notification timing does not match displayed report timestamps.
5. Match one prediction to at most one expectation using maximum bipartite matching. Require action, type, exact tracked target and all case-specific evidence anchors. An untracked issue may legitimately corroborate a pending ticket from an earlier call only if that new parent has the same type and all identity anchors. Duplicate or unrelated queue items are false positives, including `file-new-low`.

The lexical anchors remain an imperfect semantic proxy. Metrics include all-queue and confidence-tier denominators, exact-call accuracy, negative-call accuracy, every extra/missing issue, and descriptive Wilson intervals. Those intervals do not account for correlated issues, annotation errors or excluded cases. The 0.85 gates use point estimates, not confidence-bound certification.

## Reproduce

From the role directory:

```sh
python -m solution.eval.run_holdout evaluate --repeat 2 --output solution/artifacts/holdout.json
```

Exit 0 means the frozen-sample gates pass; exit 1 means a failed gate or invalid/stale assessment. Failures are evidence, not permission to weaken labels or thresholds. The machine-readable report is [holdout.json](../../artifacts/holdout.json).

`prepare` creates a new, nonempty-protected assessment directory; `seal` validates complete source-backed annotations and refuses to overwrite a seal. Do not regenerate the existing manifest or seal to conceal changes. A changed pipeline needs a newly versioned assessment and untouched validation data; scores on inspected failures must be called regression results. Human adjudication should be separately attributed and versioned, retaining the original annotations and disagreements.

## Research basis

- [scikit-learn: common pitfalls and data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage): test data must not inform model choices. Applied here by freezing before annotation and preserving unfavorable results without tuning on them.
- [OpenAI: evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): task-specific representative cases, explicit criteria, logging, continuous evaluation, and calibration against human judgment. Applied here with outcome-independent sampling, negative cases, strict gates, persisted disagreements and explicit agent-label provenance.
- [Original assignment](../../../README.md): evaluate genuine external issues, avoid duplicates and noise, retain human approval, and report expectations beyond the supplied dev labels. It does not supply the private holdout ground truth.