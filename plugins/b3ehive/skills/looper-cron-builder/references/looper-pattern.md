# Looper Cron Pattern

## Pattern Scope

This reference is intentionally project-neutral. Keep examples generic and never
name private repositories, local absolute paths, customer workspaces, or
operator-specific evidence directories in committed skill docs.

## Best-Practice Pattern

1. Keep the authoritative DAG acyclic.
2. Define bridge surfaces and bridge signals. Use bridge metrics when the
   signal is numeric.
3. Attach LoopSpecs to bridge surfaces, bridge metrics, DAG nodes, or all
   three.
4. Allocate a ResourceEnvelope before a loop can become eligible.
5. Allocate a ResourceLease before each daemon activation or attempt worker.
6. Run attempts in isolated workspaces with declared path scopes.
7. Record reward signals and resource cost after every attempt.
8. Compute ROI before issuing the next lease.
9. Pause loops when no-reward resource thresholds are reached.
10. Resume paused loops only after explicit refund and strategy change.
11. Let loop attempts produce candidates or `[_]` evidence only.
12. Let the master lane validate and accept `[x]` in DAG order.

## Three-Cursor Model

Looper adds a loop-attempt cursor to the existing worker/master pattern:

- DAG claim cursor fills normal worker lanes from `[ ]` items.
- Loop attempt cursor fills attempt lanes from eligible loops with resource
  envelopes.
- Master integration cursor validates `[_]` outputs and looper candidates in DAG
  dependency order.

Worker refill should happen before heavy ROI reporting so feedback loops do not
starve the main execution surface.

## Bridge Surface And Metric Examples

Use bridge surfaces for the level of state the loop is trying to move:

```text
context
handoff
memory
artifact
blueprint
strategy
metric
identity
```

Use neutral metric names:

```text
accepted_patch_count
build_test_fix_report_completed_count
benchmark_workloads_completed
end_to_end_cost_explained
beta_installs
paid_commitments
usage_retention_days
claim_evidence_coverage
support_ticket_resolution_rate
workflow_automation_success_count
```

Do not use private product names, customer names, local repo names, or personal
strategy document names in committed surfaces or metrics.

## No-Reward Pause

Every loop should track no-reward spend:

```text
attempts_without_reward
usd_without_reward
tokens_without_reward
wall_clock_without_reward
human_review_without_reward
```

Primary reward clears the accumulator. Secondary reward reduces it. Negative or
empty output continues accumulation. When thresholds are reached, write
`paused_no_reward` and require explicit refund plus strategy change before
resume.

## Runtime Files

Prefer these generic local paths:

```text
.b3ehive/looper/loops.yaml
.b3ehive/looper/bridge_surfaces.yaml
.b3ehive/looper/bridge_signals.yaml
.b3ehive/looper/bridge_metrics.yaml
.b3ehive/looper/bridge_delta_ledger.jsonl
.b3ehive/looper/resource_envelopes.json
.b3ehive/looper/leases.json
.b3ehive/looper/evidence_ledger.jsonl
.b3ehive/looper/operator_signals.jsonl
.b3ehive/looper/side_effect_decisions.jsonl
.b3ehive/looper/nested_run_ledger.jsonl
.b3ehive/looper/reward_ledger.jsonl
.b3ehive/looper/roi_ledger.jsonl
.b3ehive/looper/pause_ledger.jsonl
.cron/looper_guard.state
.cron/looper_guard.log
.cron/looper/workspaces/slot-N/
```

Keep runtime ledgers private unless the user explicitly wants a sanitized report
committed under `Docs/looper/`.

## Common Failure Modes

- loop specs with no metric, validator, or resource envelope
- DAG cycles disguised as feedback loops
- attempts that run without a lease
- continuing after no-reward thresholds
- resuming without a changed strategy
- accepting `[x]` from daemon workers
- ROI ledgers that track spend but not reward
- bridge metrics that are vague slogans instead of measurable signals
- bridge surfaces without evidence policy
- bridge deltas without before/after refs
- nested b3ehive runs without `ParentLeaseRef`
- protected side effects without gate decisions
- operator drain/cancel signals treated as best-effort instead of authoritative
- committed examples that reveal private project names or local paths
