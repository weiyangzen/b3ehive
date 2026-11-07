# Looper Schemas

On-demand schemas and enumerations. Each schema appears once in the suite.
Sections were moved from v1 `SKILL.md`, `bridge-control.md`, and
`b3ehive-bridge-contract.md`. The LooperLog schema is the friction-note schema.

## LoopSpec

`LoopSpec` is the static definition of a loop. Store committed generic specs
under a neutral docs path such as:

```text
Docs/looper/LOOP_SPEC.md
```

Runtime-expanded private specs may live under ignored paths:

```text
.b3ehive/looper/loops.yaml
.cron/looper/loops.local.yaml
```

Minimum fields:

```yaml
loop_id: LOOP-REPO-MAINTENANCE-REPAIR
attach_to:
  bridge_surface_ids:
    - repo_maintenance_to_accepted_patch
  bridge_metric_ids:
    - build_test_fix_report_completed_count
  dag_node_ids:
    - ITEM-012
purpose: repair failing implementation attempts until validators pass or ROI stops justifying spend
trigger:
  any:
    - metric_below_target: build_test_fix_report_completed_count
    - gate_failed: unit_test
    - evidence_stale_days: 7
preconditions:
  validator_exists: true
  resource_envelope_available: true
  owned_paths_declared: true
  no_active_conflict: true
resource_envelope_ref: ENV-REPO-MAINTENANCE-WEEKLY
max_parallel_attempts: 3
owned_paths:
  - src/**
forbidden_paths:
  - .cron/**
  - .ops/**
validators:
  cheap:
    - command: "<lint or focused test command>"
  expensive:
    - command: "<full validation command>"
reward_model:
  primary_rewards:
    - accepted_patch
    - metric_target_progress
  secondary_rewards:
    - validator_added
    - failure_cause_classified
  negative_rewards:
    - non_reproducible_output
    - cost_without_new_evidence
pause_resume:
  pause_when:
    - no_reward_budget_exhausted
    - no_reward_attempt_limit_reached
    - validator_missing
  resume_when:
    - explicit_resource_refund
    - new_validator_added
    - new_evidence_arrived
    - bridge_target_changed
```

## Resources And Leases

`ResourceEnvelope` is the total budget granted to a loop for a period.

Track at least:

```json
{
  "envelope_id": "ENV-REPO-MAINTENANCE-WEEKLY",
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "status": "active",
  "budget": {
    "usd": 30,
    "tokens": 3000000,
    "wall_clock_minutes": 720,
    "human_review_minutes": 90,
    "attempts": 20,
    "disk_gb": 8
  },
  "spent": {
    "usd": 0,
    "tokens": 0,
    "wall_clock_minutes": 0,
    "human_review_minutes": 0,
    "attempts": 0,
    "disk_gb": 0
  }
}
```

`ResourceLease` is the short-lived budget granted to one daemon activation or
attempt worker. No lease means no attempt.

Minimum fields:

```json
{
  "lease_id": "LEASE-0001",
  "loop_id": "LOOP-REPO-MAINTENANCE-REPAIR",
  "attempt_id": "ATTEMPT-0001",
  "ttl_minutes": 60,
  "max_usd": 3,
  "max_tokens": 250000,
  "max_wall_clock_minutes": 60,
  "max_diff_kib": 256,
  "workspace": ".cron/looper/workspaces/slot-01",
  "status": "leased"
}
```

Leases must have TTL, heartbeat, owner, workspace, and reclaim behavior. Expired
leases, dead daemon owners, and missing heartbeat files must be released before
new workers are spawned.

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

## EstimatorPolicy

Use AI estimation for local parameters. Keep hard caps only for AI capability
boundaries, external safety, and acceptance invariants.

AI may estimate:

```text
proposal_count
choose_count
review_depth
coverage_or_precision_mode
worker_grouping
batch_size
split_threshold
route_class
model_class
validator_strength
retry_count
lease_size
context_compression_level
next_nested_skill
pause_or_lower_route_decision
looper_log_grain
```

Hard caps remain hard:

```text
worker_cannot_write_x
master_only_acceptance
source_manifest_required
context_recall_boundary
resource_envelope_total_budget
side_effect_gate_required
max_diff_kib
max_log_mb
max_cron_root_gb
network_or_spend_approval
identity_level_write_approval
```

Minimum record:

```yaml
estimator_decision:
  estimate_id: EST-0001
  task_ref: ITEM-123
  skill: compete-cron-builder
  input_signals:
    question_type: coverage
    validator_strength: medium
    risk_class: security
    source_size_kib: 380
    budget_workers: 8
  estimated_parameters:
    proposal_count: 8
    choose_count: all_valid
    route_class: high_reasoning_coverage
  hard_caps:
    max_tokens: 800000
    max_diff_kib: 256
    worker_can_write_x: false
  rationale:
    - coverage task needs union of valid findings
    - security risk needs low false-negative rate
  fallback:
    on_validator_failure: escalate_route
    on_no_reward: pause_or_split
```

If a value is hardcoded, classify it as one of:

```text
ai_boundary
safety_cap
external_reality_cap
compatibility_cap
operator_override
```

Reject unclassified "worked before" constants as core policy.

## Unified RouteDecision

A route is the full work path, not just a model or provider.

Route decisions may choose:

```text
skill_path
nested_skill_calls
runner_or_provider
model_class
reasoning_effort
worker_count
proposal_count
choose_count
validator_strength
context_strategy
cost_tier
fallback_route
human_review_requirement
side_effect_class
looper_log_capture
```

Minimum record:

```yaml
route_decision:
  route_id: ROUTE-0001
  parent_ref: ITEM-123
  selected_skill_path:
    - learn-cron-builder
    - compete-cron-builder
    - execution-cron-builder
  route_class: high_reasoning_coverage
  model_class: frontier_reasoning
  runner: B3EHIVE_AGENT_RUNNER or platform default
  validator_strength: strong
  context_strategy:
    digest: merged_64k
    recall: source_manifest_rows
  side_effect_class: candidate_only
  why_not_cheaper:
    - security coverage needs low false-negative rate
  why_not_more_expensive:
    - validators are strong enough after coverage union
  fallback_route:
    - lower_route_after_secondary_reward
    - pause_on_no_reward
```

Route decisions should be sticky within one lease. Changing route without new
evidence is route oscillation.

## SkillRegistry And NestedSkillCall

Every skill may know the compact capability card of the other skills:

```text
compete = proposals, coverage union, repair search, vote/synthesis
execution = DAG execution, worker/master, git/worktree, validation, checkpoint
learn = source manifest, subset, one-to-one learning, transform, translate
optimization = design refinement, simplification, AR research
looper = resource feedback, ROI, side-effect, operator signal, multi-grain feedback bridge
```

Capability awareness is small. Do not load all five full skill texts unless a
route selects them.

Nested calls require:

```text
NestedSkillCall
RouteDecision
ParentLeaseRef
side_effect_class
max_depth_remaining
max_total_nested_runs
EvidenceRef
ROI update after completion
looper_log when the call exposes instrument feedback
[ ]/[_]/[x] master state
```

Minimum request:

```yaml
nested_skill_call:
  call_id: CALL-0001
  parent_skill: looper-cron-builder
  child_skill: compete-cron-builder
  parent_ref: LOOP-123
  parent_lease_ref: LEASE-123
  route_decision_ref: ROUTE-0001
  purpose: repair search after repeated validator failure
  side_effect_class: candidate_only
  max_depth_remaining: 2
  allowed_outputs:
    - proposal
    - candidate_patch
    - validation_hint
  forbidden_outputs:
    - authoritative_x
    - direct_push
    - unleased_spend
  master_state: "[ ]"
```

Nested result:

```yaml
nested_skill_result:
  call_id: CALL-0001
  master_state: "[_]"
  evidence_refs:
    - EVID-001
    - candidate/run_a/result.md
    - verification.md
  reward_candidates:
    - failure_cause_classified
  spent:
    tokens: 120000
    wall_clock_minutes: 18
  looper_log_refs:
    - LLOG-0001
  next_route_recommendation:
    - execution-cron-builder
```

Rules:

```text
max_depth default <= 3
max_total_nested_runs default <= 8
child side_effect_class cannot exceed parent side_effect_class
paused, drained, cancelled, or budgetless parent blocks child
same route plus no reward cannot repeat
caller owns why
callee owns how
master owns acceptance
```

Risks to lint:

```text
infinite_recursion
acceptance_bypass
evidence_laundering
context_bloat
side_effect_escalation
roi_degeneration
route_oscillation
skill_boundary_confusion
```

## EvidenceLint

Prefer lintable evidence rules over one huge global schema.

Minimum question set:

```text
Can this evidence support [_]?
Can this evidence support [x]?
Can the master review it without reading a full transcript?
Does it point to source rows, diffs, commands, validators, side effects, or external facts?
Does it include looper_log refs when the run exposed instrument feedback?
```

Minimum evidence row:

```json
{
  "evidence_id": "EVID-0001",
  "source_ref": "SRC-01234 or ITEM-123",
  "attempt_ref": "ATTEMPT-456",
  "lease_ref": "LEASE-456",
  "route_ref": "ROUTE-0001",
  "estimator_ref": "EST-0001",
  "changed_files": ["path/a"],
  "commands_run": ["npm test"],
  "validation_result": "passed",
  "side_effect_decisions": ["SIDE-001"],
  "bridge_delta_refs": ["DELTA-001"],
  "looper_log_refs": ["LLOG-001"],
  "reward_candidates": ["validator_added"],
  "master_state": "[_]"
}
```

No `[x]` without the relevant EvidenceLint pass.

## LooperLog Multi-Grain Object/Instrument Feedback

`LooperLog` records feedback evidence for both `TargetObject` movement and
`InstrumentObject` quality. It is not a chat summary, not a public skill, not
automatic self-modification, and not an accepted policy change.

Grains:

```text
micro        validator failure, route miss, evidence gap, side-effect hesitation
skill        one skill invocation produced friction or useful evidence
composition  nested skill calls exposed route/resource/contract issues
scaffold     scripts, validators, prompts, hooks, manifests, ledgers need adjustment
tool         coding-tool integration, B3IR, CLI/plugin behavior needs adjustment
task         whole user task outcome/cost/reward feedback
```

Formal control model:

```text
For every execution episode E:
  E has a TargetObject O: user task, DAG item, artifact, report, or repo change.
  E has an InstrumentObject I: skills, scaffolds, validators, scripts, routes, ledgers, and tools.

  ObjectLoop:
    move O toward accepted state [x].
    record target feedback: output quality, validation result, bridge movement, reward, cost.

  InstrumentLoop:
    observe whether I helped, blocked, over-spent, under-validated, or created friction.
    record instrument feedback: route quality, skill fit, scaffold fit, validator strength, tool friction, ledger sufficiency.
    emit looper_log evidence for possible improvement of I.

  Constraint:
    the instrument loop may emit evidence [_] and backlog [ ],
    but it may not mutate accepted instrument policy without EvidenceLint, ROI,
    ParetoGate, rollback, and master [x].
```

Authority separation:

```text
normal execution may change TargetObject within the task boundary
runtime may only log evidence about InstrumentObject
accepted InstrumentObject change needs its own [ ] -> [_] -> [x] lifecycle
```

Object contracts:

```text
TargetObject
  kind: task | dag_item | artifact | repo_change | report | benchmark | product_signal
  desired_movement: what accepted progress would mean
  evidence_policy: what proves movement happened

InstrumentObject
  kind: skill | skill_composition | scaffold | validator | route | ledger | script | tool | coding_interface
  role: how it was supposed to help the TargetObject move
  observed_effect: helped | neutral | blocked | wasted | under-validated | over-complicated
  change_authority: evidence_only | backlog_candidate | accepted_patch
```

Minimum log:

```yaml
looper_log:
  log_id: LLOG-0001
  grain: micro | skill | composition | scaffold | tool | task
  task_ref: TASK-123
  target_object:
    kind: dag_item | artifact | repo_change | report | route_decision | validator | skill | scaffold | tool
    ref: ITEM-123
    desired_movement: accepted patch with passing validators
    evidence_policy:
      - diff_ref
      - validator_output_ref
      - master_decision_ref
  instrument_set:
    skills:
      - learn-cron-builder
      - compete-cron-builder
    scaffolds:
      - source_manifest
      - evidence_lint
      - route_ledger
    tools:
      - local_cli
      - validator_runner
  instrument_object:
    kind: skill_composition
    ref: learn+compete
    intended_role: understand subset and compare repair options
    observed_effect: helped | neutral | blocked | wasted | under-validated | over-complicated
    change_authority: evidence_only
  route_refs:
    - ROUTE-001
  estimator_refs:
    - EST-001
  evidence_refs:
    - EVID-001
  outcome:
    master_state: "[_]"
    reward_class: primary | secondary | weak | negative | none
  target_feedback:
    movement: []
    remaining_risk: []
  instrument_feedback:
    helped:
      - source manifest prevented context drift
    harmed:
      - nested call depth was unnecessary
    missing:
      - route justification lint was absent
  improvement_suggestions:
    - add EvidenceLint for route justification
  suggested_owner:
    skill: looper-cron-builder
    surface: route_policy | estimator_policy | evidence_lint | nested_call_policy | side_effect_gate | scaffold | tool_plugin
  future_backlog_state: "[ ]"
```

State semantics:

```text
[ ] improvement is only a future backlog candidate
[_] looper_log exists with evidence, but no accepted policy/tool/skill change yet
[x] master accepted and applied a real improvement
```

Batch improvement flow:

```text
many multi-grain looper_logs [_]
  -> periodic looper review
  -> cluster recurring patterns
  -> compete if tradeoff is unclear
  -> optimization if simplification is needed
  -> execution if patching skill text/scripts
  -> master accepts [x]
```

Runtime rule:

```text
Do the work.
Observe the instruments used to do the work.
Record instrument feedback as looper_log.
Defer instrument mutation to a separate accepted improvement lifecycle.
```

## ParetoGate For Self-Evolution

Self-evolution must improve at least one objective without weakening protected
invariants.

Protected invariants:

```text
five public skills remain the public surface
[ ]/[_]/[x] remains the only authoritative state grammar
workers cannot write [x]
source manifests remain mandatory for learn
side-effect gates remain hard
resource envelope hard caps remain hard
route, estimator, evidence, looper_log, and ROI ledgers remain auditable
prompt/hook forests stay outside core unless promoted by evidence
```

Minimum gate:

```yaml
pareto_gate:
  improves:
    - lower_cost
    - better_coverage
    - stronger_validator
    - less_hardcoding
    - lower_false_completion_risk
    - simpler_skill_text
  must_not_worsen:
    - state_grammar
    - master_only_acceptance
    - evidence_traceability
    - rollback_ability
    - privacy_boundary
    - resource_caps
  measured_by:
    - before_after_lint
    - validator_result
    - no_regression_checklist
```

## ROI As Scheduling Signal

ROI is an early sensing and load-balancing primitive, not only a final report.

Before issuing a new looper lease, update:

```text
expected_reward
resource_cost
bridge_difficulty
no_reward_risk
opportunity_cost
next_decision
```

Allowed decisions:

```text
continue
pause
split
lower_route
raise_route
ask_compete
ask_learn_subset
ask_optimization
retire
request_master_input
```

Normal DAG worker refill still comes before heavy ROI reports.

## Reward And ROI Accounting

Looper must record value after every attempt. A loop that consumes resources but
does not create reward must pause.

Primary rewards directly move the bridge surface or close validated work:

- accepted patch
- replayable execution trajectory
- benchmark workload completed
- product validation signal
- paid or committed conversion signal
- claim audit evidence completed
- operational KPI improved

Secondary rewards create reusable learning or infrastructure:

- validator added
- failure cause classified
- reproduction path recorded
- scope narrowed
- reusable workflow or skill extracted
- bridge route clarified
- actionable handoff produced
- benchmark harness improved
- objection or support taxonomy created

Negative or no-reward outcomes consume resources without usable progress:

- no new evidence
- validator still missing
- output not reproducible
- patch not reviewable
- metric unchanged
- claim still unsupported
- only narrative summary was produced

Every Looper cron must maintain a ROI ledger under an ignored runtime path and
may generate a sanitized committed report. Generated cron code may let users
override weights, but it must not omit resource cost, bridge movement, reward
class, and decision fields.

## Runtime Files

Committed generic docs may live under:

```text
Docs/looper/LOOP_SPEC.md
Docs/looper/BRIDGE_SURFACES.md
Docs/looper/BRIDGE_METRICS.md
Docs/looper/BRIDGE_REPORT.md
Docs/looper/ROI_REPORT.md
```

Private runtime files should be ignored and local:

```text
.b3ehive/looper/loops.yaml
.b3ehive/looper/bridge_surfaces.yaml
.b3ehive/looper/bridge_signals.yaml
.b3ehive/looper/bridge_metrics.yaml
.b3ehive/looper/bridge_delta_ledger.jsonl
.b3ehive/looper/resource_envelopes.json
.b3ehive/looper/leases.json
.b3ehive/looper/evidence_ledger.jsonl
.b3ehive/looper/looper_log.jsonl
.b3ehive/looper/operator_signals.jsonl
.b3ehive/looper/side_effect_decisions.jsonl
.b3ehive/looper/nested_run_ledger.jsonl
.b3ehive/looper/reward_ledger.jsonl
.b3ehive/looper/roi_ledger.jsonl
.b3ehive/looper/pause_ledger.jsonl
.cron/looper_guard.state
.cron/looper_guard.log
.cron/looper/workspaces/slot-N/
.cron/scripts/cron_space_guard.sh
.ops/install_looper_cron.sh
.ops/cleanup_looper_cron.sh
```

The generated cron must add `.b3ehive/looper/*.local.*`, `.cron/`, and `.ops/`
runtime paths to `.git/info/exclude` or an equivalent local ignore strategy
unless the user explicitly wants committed operational scaffolding.

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
