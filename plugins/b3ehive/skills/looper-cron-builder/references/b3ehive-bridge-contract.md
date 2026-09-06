# b3ehive Bridge Contract

Use this reference when any b3ehive skill needs shared state, estimator, route,
evidence, nested-call, looper_log, ROI, self-evolution, or coding-tool interface
rules.

This is a suite-level contract. It does not create a sixth public skill.

## State Constitution

Only these marks express authoritative acceptance:

```text
[ ]  unresolved and still open
[_]  evidence or candidate exists, master has not accepted
[x]  master accepted after validation and reconciliation
```

All other words are runtime telemetry or evidence labels, not completion states:

```text
pending eligible paused cancelled finalized retired accepted validated landed
complete finished blocked
```

They may appear as `runtime_status`, `operator_signal`, `reason`, or
`master_note`, but they must not replace `[ ]`, `[_]`, or `[x]` on
authoritative surfaces.

Core object meanings:

```text
AuthoritativeState = [ ] | [_] | [x]
RuntimeState = implementation telemetry; cannot close work by itself
EvidenceState = facts that may support [_] or [x]
OperatorSignal = input event; not a completion state
SideEffectDecision = gate result; not a completion state
BridgeDelta = before/after movement; not a completion state
RewardSignal = value classification; not a completion state
LooperLog = multi-grain feedback evidence; not a completion state
```

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

## B3IR And Interface Modes

`B3IR` is a future coding-tool intermediate representation. It is not required
for normal skill use, but generated tools may use it.

Mode projections:

```text
mode_1_voice_ramble -> candidate extraction only
mode_2_natural_language -> current readable default
mode_3_classical_compressed -> optional doctrine display
mode_4_symbolic_formal -> lintable and partially verifiable contract
```

No mode may create a separate truth source. Mode 4 should formalize structural
invariants first:

```text
state transitions
worker cannot write [x]
master-only acceptance
DAG acyclicity
source manifest coverage
route and estimator decision existence
nested call requires parent lease
child side-effect class <= parent side-effect class
EvidenceLint pass before [x]
looper_log required for instrument feedback
```

## Anti-Bloat Output Rule

Default output should state facts, evidence, decisions, and next actions.

Do not add affective filler, motivational prose, or human-pleasing style rules
to core skills. Tone/style belongs to explicit copywriting, UX, localization,
or downstream interface tasks.

## Prompt And Hook Boundary

Core b3ehive defines contracts. Project or coding-tool engineering may generate
prompt blocks, shell hooks, validators, CI checks, editor plugins, or provider
glue from those contracts.

Do not promote a project-specific prompt block or hook into core unless it:

```text
represents a reusable invariant
cannot be expressed by existing contracts
reduces total complexity
has evidence across multiple projects
passes ParetoGate
```
