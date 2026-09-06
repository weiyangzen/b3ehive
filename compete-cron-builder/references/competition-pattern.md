# Compete Cron Pattern

## Scope

Compete runs local proposal competitions. It covers the removed old three-agent
workflow through `three_way_challenge`, but it is not a public continuation of
that old tool name.

## Shapes

```text
three_way_challenge
  run_a/run_b/run_c, verifier, peer reviews, revision, vote, repair synthesis.

parallel_proposals
  N independent candidates, choose best or top-k.

coverage_sweep
  Candidates search for findings. Select all valid findings after dedupe.

repair_search
  Candidates propose repair paths. Select primary repair and fallback.

top_k_synthesis
  Candidates produce diverse plans. Select 2-3 and synthesize.
```

## Selection Modes

```text
best_one
  Choose one candidate by verifier or explicit score.

top_k
  Choose a small set for synthesis.

coverage_union
  Merge all valid findings; do not pick one best report.

risk_union
  Merge findings and rank by severity, likelihood, blast radius, and fix owner.

vote_then_tiebreak
  Parse candidate votes and resolve ties by stable candidate id.

repair_queue
  Emit ordered repair assignments with validation hints and fallback path.
```

## Execution Handoff

Compete outputs are provisional. In execution cron, they may create `[ ]` child
items, validation hints, repair assignments, or integration recommendations.
They may never write `[x]`.

## Looper Handoff

Compete inside looper attempts requires an active `ResourceLease` and a
`ParentLeaseRef`. Cost rolls into the parent lease before another lease is
issued. Candidate outputs are provisional, cannot write `[x]`, and produce
reward candidates only; the parent looper attempt owns reward classification
and no-reward accounting.

## Common Failure Modes

- exposing the removed old tool name as a public preset or wrapper
- writing only native JSON and forgetting `old_three_way` artifact coverage
- selecting one report for coverage work instead of unioning all valid findings
- letting a candidate write `[x]`
- running a looper competition without a lease
- running a looper competition without `ParentLeaseRef`
- letting nested candidate costs escape parent no-reward accounting
- treating `[_]` as complete
- allowing heavy union/ROI work to block normal execution worker refill
