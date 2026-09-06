# Looper Bridge Control Protocol

## Purpose

Use this reference when a loop needs more than a numeric bridge metric, when an
attempt may call another b3ehive skill, or when side effects and operator
control must be audited.

Assume the strongest available LLM is already being used. Do not add heavy
semantic scaffolding by default. Let the model handle relevance, fuzzy scope,
strategy writing, bridge writing, failure explanation, and handoff synthesis.
Looper owns resources, leases, concurrency, side effects, evidence, reward
classification, ROI, pause/resume, operator signals, nested spend attribution,
multi-grain looper logs, and master-only acceptance.

## Bridge Levels

`BridgeMetric` remains valid, but it is only one kind of bridge signal. General
loops may attach to `BridgeSurface` records.

Allowed `bridge_level` values:

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

Definitions:

- `context`: current session understanding, constraints, and local working
  state.
- `handoff`: cross-session continuation files, summaries, next actions, claim
  state, and transfer notes.
- `memory`: durable facts, long-term notes, stable operating knowledge, or
  recurring looper_log clusters.
- `artifact`: code, docs, tests, configs, generated outputs, skill files, and
  reports.
- `blueprint`: authoritative plan, checklist, DAG, manifest, target contract,
  or todo surface.
- `strategy`: route, priority, wedge, acceptance criteria, kill criteria,
  commercial route, or operational bridge.
- `metric`: quantitative measurement, benchmark, test count, conversion,
  revenue, completion rate, or other numeric target.
- `identity`: very slow-changing long-horizon thesis, values, or non-negotiable
  constraints.

Rules:

- Bridge level is descriptive; it does not create a new workflow.
- A loop may attach to multiple bridge surfaces.
- A bridge surface may use qualitative or quantitative evidence.
- Durable feedback is a bridge level, not a separate public subsystem.
- Identity-level changes require explicit master approval.

## BridgeSurface

Minimum fields:

```yaml
surface_id: strategy_to_weekly_action
bridge_level: strategy
owner_loop: LOOP-STRATEGY-VALIDATION
source_refs:
  - final.md
  - donelist.md
  - bridge.md
target_refs:
  - bridge.md
  - progress.md
movement_goal: convert a long-term direction into an asset-backed validation route
evidence_policy:
  required:
    - asset_anchor
    - user_or_use_case
    - validation_metric
    - failure_signal
privacy_class: generic_committable
```

Store committed generic documentation under:

```text
Docs/looper/BRIDGE_SURFACES.md
```

Store runtime or private surfaces under:

```text
.b3ehive/looper/bridge_surfaces.yaml
```

## BridgeSignal

`BridgeSignal` declares what evidence can prove useful movement.

Example:

```yaml
signal_id: route_has_failure_signal
surface_id: strategy_to_weekly_action
signal_type: qualitative
required_evidence:
  - user_or_use_case
  - validation_metric
  - kill_criteria
reward_weight: 3
failure_signal: route remains abstract or cannot be tested within four weeks
```

Signal types:

```text
quantitative
qualitative
binary_gate
document_delta
artifact_delta
validator_result
external_event
human_acceptance
```

Rules:

- A BridgeSignal defines evidence; it does not mark completion.
- Existing BridgeMetric objects map to `signal_type=quantitative`.
- A signal can contribute to reward classification only after evidence exists.

## BridgeDelta

`BridgeDelta` records before -> after movement on a bridge surface.

Example:

```json
{
  "delta_id": "DELTA-0007",
  "loop_id": "LOOP-STRATEGY-VALIDATION",
  "surface_id": "strategy_to_weekly_action",
  "bridge_level": "strategy",
  "before_ref": "bridge.md@old_hash",
  "after_ref": "bridge.md@new_hash",
  "changed_fields": ["90_day_output", "next_week_action", "kill_criteria"],
  "evidence_refs": [".b3ehive/looper/evidence/ATTEMPT-0042.json"],
  "master_status": "pending"
}
```

Rules:

- BridgeDelta is not automatically reward.
- RewardSignal classifies whether the delta has value.
- Master lane must accept or reject candidate deltas.
- No bridge delta can bypass `[ ] -> [_] -> [x]`.

Reward mapping:

- Primary reward: accepted artifact, metric target progress, validated route,
  paid/user signal, completed benchmark, or accepted operational improvement.
- Secondary reward: validator added, failure cause classified, scope narrowed,
  reusable workflow captured, bridge route clarified, or actionable handoff.
- Instrument reward: accepted improvement to a skill, scaffold, validator,
  route policy, or tool adapter after looper_log clustering and master gate.
- Weak evidence: plausible insight, better hypothesis, or cleaner handoff with
  no accepted movement yet.
- Negative reward: non-reproducible output, unsupported claim, abstract summary
  only, or cost without movement.
- No reward: no new evidence, no state change, no useful bridge movement.

## SideEffectGate

Use a minimal side-effect boundary. Do not gate every semantic action. Gate only
operations that can create external damage, hidden cost, privacy risk, or
unauditable state.

Gate types:

```text
protected_path
dangerous_command
large_diff
secret_exposure
push_or_publish
delete_or_destructive_write
network_or_spend
authoritative_blueprint_write
identity_level_write
```

Example:

```yaml
gate_id: protected_authoritative_surface
gate_type: protected_path
applies_to:
  - final.md
  - bridge.md
  - Docs/**/Blueprint*.md
  - package.json
  - scripts/install_skills.sh
risk_class: authoritative_state
default_action: require_master_ack
allowed_actors:
  - master_lane
  - approved_operator_signal
```

Default rules:

- Normal file reads do not need a gate.
- Normal local edits inside owned paths do not need a gate.
- Worker outputs may create candidates or `[_]` evidence.
- Workers may not mutate protected authoritative surfaces unless explicitly
  leased.
- Workers may not push, publish, delete broad paths, spend money, or write
  identity-level files without gate approval.
- Master lane owns final integration.

Minimum `SideEffectDecision` record:

```json
{
  "decision_id": "SIDE-0003",
  "attempt_id": "ATTEMPT-0011",
  "gate_id": "protected_authoritative_surface",
  "operation": "write",
  "path": "bridge.md",
  "risk_class": "authoritative_state",
  "decision": "allowed_with_master_ack",
  "reason": "strategy bridge surface update requested by loop spec",
  "evidence_ref": ".b3ehive/looper/evidence/ATTEMPT-0011.json"
}
```

## OperatorSignal

Use `OperatorSignal` for direct operator or master-lane control over running
loops, live attempts, and nested runs.

Example:

```json
{
  "signal_id": "OP-0009",
  "created_at": "2026-06-19T12:00:00Z",
  "target_type": "loop",
  "target_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "action": "drain",
  "reason": "prepare for master integration",
  "effective_after": "current_attempts_finish",
  "requires_master_ack": true,
  "status": "pending"
}
```

Allowed actions:

```text
cancel
drain
pause_after_current
resume
replan
force_sync
freeze_scope
unfreeze_scope
escalate_to_master
retire_loop
split_loop
change_resource_envelope
change_bridge_target
```

Rules:

- Pending operator signals must be processed before new leases.
- `cancel`, `drain`, and `pause_after_current` block new lease allocation.
- `resume` must not bypass no-reward pause requirements.
- Operator signal handling must be written to the evidence ledger.

## NestedRunLedger And ParentLeaseRef

All nested b3ehive runs started inside a loop attempt must inherit the parent
resource lease unless explicitly granted a child lease.

Example `ParentLeaseRef`:

```json
{
  "parent_loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "parent_attempt_id": "ATTEMPT-0014",
  "parent_lease_id": "LEASE-0014",
  "nested_run_id": "COMPETE-REPAIR-0002",
  "skill": "compete-cron-builder",
  "budget": {
    "max_tokens": 120000,
    "max_wall_clock_minutes": 20,
    "max_diff_kib": 64
  }
}
```

Example `NestedRunLedger` row:

```json
{
  "nested_run_id": "LEARN-SUBSET-0004",
  "parent_lease_id": "LEASE-0014",
  "skill": "learn-cron-builder",
  "purpose": "understand failing scheduler subset before repair",
  "started_at": "2026-06-19T12:15:00Z",
  "finished_at": "2026-06-19T12:29:00Z",
  "spent": {
    "tokens": 82000,
    "wall_clock_minutes": 14,
    "disk_gb_hours": 0.2
  },
  "outputs": [
    "Docs/learn/subsets/scheduler/source_manifest.tsv",
    "Docs/learn/subsets/scheduler/summary.md"
  ],
  "reward_candidate": "failure_cause_classified",
  "looper_log_refs": ["LLOG-0004"],
  "master_status": "pending"
}
```

Rules:

- Nested runs cannot write `[x]`.
- Nested runs cannot escape the parent lease budget.
- Nested runs produce reward candidates, not accepted reward.
- Parent attempt owns final reward accounting.
- No-reward accounting includes nested run cost.
- Paused loops cannot start nested runs.
- Nested runs should create looper_log refs when they expose route, depth,
  validator, scaffold, tool, or cost/reward feedback about the instrument set.

## EvidenceLedger

Use compact evidence records, not full transcript adjudication.

Example:

```json
{
  "evidence_id": "EVID-0042",
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "attempt_id": "ATTEMPT-0042",
  "lease_id": "LEASE-0042",
  "input_contract_ref": "Docs/looper/LOOP_SPEC.md#LOOP-REPO-MAINTENANCE-REPAIR",
  "owned_paths": ["src/scheduler/**"],
  "changed_files": ["src/scheduler/run.ts", "tests/scheduler.test.ts"],
  "commands_run": ["npm test -- scheduler"],
  "validation_result": "passed",
  "bridge_delta_refs": ["DELTA-0007"],
  "side_effect_decisions": ["SIDE-0003"],
  "nested_run_refs": ["LEARN-SUBSET-0004"],
  "looper_log_refs": ["LLOG-0004"],
  "reward_candidates": ["accepted_patch", "failure_cause_classified"],
  "master_decision": "pending"
}
```

Rules:

- EvidenceLedger is a fact index, not a full conversation transcript.
- It should stay small enough for master review.
- It must point to raw logs or outputs when needed.
- It must not leak secrets or private paths into committed reports.

## LooperLog

Use `LooperLog` for feedback evidence about both the `TargetObject` and the
`InstrumentObject` used to work on it.

```text
TargetObject = task, DAG item, artifact, repo change, report, benchmark, or product signal being moved
InstrumentObject = skill, skill composition, scaffold, validator, route, ledger, script, or tool used to move it
```

Normal execution may change the `TargetObject` inside the task boundary.
Runtime may only log evidence about the `InstrumentObject`. Accepted
instrument changes need their own `[ ]` -> `[_]` -> `[x]` lifecycle.

Grains:

```text
micro
skill
composition
scaffold
tool
task
```

Minimum row:

```yaml
looper_log:
  log_id: LLOG-0001
  grain: micro | skill | composition | scaffold | tool | task
  target_object:
    kind: dag_item | artifact | repo_change | report | route_decision | validator | skill | scaffold | tool
    ref: ITEM-123
    desired_movement: accepted target movement with evidence
    evidence_policy:
      - evidence_ref
      - validator_output_ref
      - master_decision_ref
  instrument_set:
    skills: []
    scaffolds: []
    tools: []
  instrument_object:
    kind: skill | skill_composition | scaffold | validator | route | ledger | script | tool | coding_interface
    ref: route-or-tool-or-skill-ref
    intended_role: how it should move the target object
    observed_effect: helped | neutral | blocked | wasted | under-validated | over-complicated
    change_authority: evidence_only | backlog_candidate | accepted_patch
  route_refs: []
  estimator_refs: []
  evidence_refs: []
  outcome:
    master_state: "[_]"
    reward_class: primary | secondary | weak | negative | none
  target_feedback:
    movement: []
    remaining_risk: []
  instrument_feedback:
    helped: []
    harmed: []
    missing: []
  improvement_suggestions: []
  future_backlog_state: "[ ]"
```

Rules:

- LooperLog is evidence/backlog, not accepted policy.
- Most looper logs remain `[_]` until a later periodic review clusters them.
- Accepted instrument changes require EvidenceLint, ROI, ParetoGate, rollback,
  and master `[x]`.
- Do not create a separate public skill for this log surface.

## Runtime Files

Add these runtime files when the corresponding controls are used:

```text
.b3ehive/looper/bridge_surfaces.yaml
.b3ehive/looper/bridge_signals.yaml
.b3ehive/looper/bridge_delta_ledger.jsonl
.b3ehive/looper/evidence_ledger.jsonl
.b3ehive/looper/looper_log.jsonl
.b3ehive/looper/operator_signals.jsonl
.b3ehive/looper/side_effect_decisions.jsonl
.b3ehive/looper/nested_run_ledger.jsonl
```

Committed generic docs may add:

```text
Docs/looper/BRIDGE_SURFACES.md
Docs/looper/BRIDGE_REPORT.md
Docs/looper/ROI_REPORT.md
```

## Finalization Contract

Before a loop can mark itself complete or retire successfully, verify:

```text
zero live leases
zero unaccounted attempts
zero pending side-effect decisions
zero unfinished nested runs
all required evidence ledger rows exist
required looper_log rows exist when instrument feedback was observed
bridge deltas are accepted or rejected
reward accounting is complete
ROI decision is recorded
attached checklist items have zero [ ] and zero [_]
master lane accepted final state
```

Do not add default plan quizzes, relevance checkers, dense prompt validators, or
full transcript judges.
