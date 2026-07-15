---
name: looper-cron-builder
description: Build or repair a resource-aware, reward-aware, ROI-tracked bridge controller for a DAG-driven repository. Use when blueprint nodes, bridge surfaces, bridge metrics, product validation goals, benchmark lanes, monitoring signals, repeated validation failures, nested b3ehive skill attempts, or operator-controlled feedback loops need bounded attempts, explicit resource leases, side-effect gates, compact evidence ledgers, no-reward pause rules, and re-funded resume under a master acceptance gate.
---

# Looper Cron Builder

## Controller Contract

Build a repository-local looper cron that monitors explicit bridge surfaces,
bridge metrics, and DAG nodes; allocates bounded resource leases; launches loop
daemon attempts; records compact evidence and reward signals; computes ROI;
pauses resource-consuming loops with no reward; and resumes them only after
explicit re-funding plus a strategy change.

Every Looper installation must define each object or deliberately omit it:

```text
LoopSpec
BridgeSurface
BridgeSignal
BridgeDelta
BridgeMetric
LoopInstance
ResourceEnvelope
ResourceLease
AttemptWorker
SideEffectGate
OperatorSignal
NestedRunLedger
EvidenceLedger
LooperLog
TargetObject
InstrumentObject
RewardSignal
ROILedger
PauseResumePolicy
```

Their operating relationship is:

```text
DAG = dependency order, still acyclic
Bridge surface = level of state the loop is trying to move
Bridge signal = evidence that can prove useful movement
Bridge delta = before -> after movement on a bridge surface
Loop daemon = conditional feedback actor around a node, surface, or metric
Resource broker = budget, lease, pause, and resume authority
Side-effect gate = boundary around risky writes, spend, publish, or deletion
Evidence ledger = compact fact index for audit and master acceptance
Looper log = multi-grain feedback evidence for target work and operating instruments
Reward ledger = classification that a bridge delta or artifact produced value
Master lane = only actor allowed to accept final completion
```

Keep the DAG acyclic. Attach loop specs beside DAG nodes, bridge surfaces, or
bridge metrics. The master lane closes checklist items after validation passes.

Treat the selected agent route as the highest-capability route already
available. It handles relevance, fuzzy scope, strategy writing,
bridge writing, failure explanation, and handoff synthesis. Heavy semantic
scaffolding stays outside the default controller. A project may add it through a
project-specific validator or side-effect gate. Looper owns resources, leases,
concurrency, side effects, evidence, reward classification, ROI, pause/resume,
operator signals, nested spend attribution, and master-only acceptance.

Every run with target or instrument feedback may record `LooperLog`
feedback for both operating lanes:

```text
ObjectLoop: move the TargetObject toward accepted state [x].
InstrumentLoop: record whether the InstrumentObject helped, blocked,
over-spent, under-validated, or created friction.
```

The instrument loop may emit `looper_log` evidence `[_]` and backlog `[ ]`.
Accepted skill, tool, or policy mutation requires EvidenceLint, ROI,
ParetoGate, rollback, and master `[x]`.

## Privacy And Generalization

Generated looper specs, docs, prompts, ledgers, and examples stay
project-neutral. An explicit user request for a private, local-only artifact
permits private content only in that artifact.

The following data stays out of public or committed Looper artifacts:

- private repository names
- customer names
- local absolute paths
- personal evidence directories
- internal product codenames
- private strategy document paths
- raw user conversations or account identifiers
- vendor secrets, API keys, or billing identifiers

Use generic labels such as `product_beta`, `repo_maintenance`,
`benchmark_lane`, `claim_audit`, `customer_workflow`, `growth_experiment`, and
`ops_review`. Private names required for local execution stay in `.cron/`,
`.ops/`, `.b3ehive/looper/*.local.*`, or another ignored surface.

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

## Bridge Control

Use bridge surfaces to describe what level of state the loop is moving:

```text
bridge_level =
  context | handoff | memory | artifact | blueprint | strategy | metric | identity
```

`BridgeMetric` is one valid `BridgeSignal` kind. Use `BridgeSurface`,
`BridgeSignal`, and `BridgeDelta` for qualitative, document-based, strategic,
handoff-based, or other movement broader than one metric.

Rules:

- Feedback and durable operating facts are bridge surfaces, not a separate
  public subsystem.
- Identity-level movement requires explicit master approval.
- A `BridgeDelta` records before -> after movement; it is not automatically
  reward.
- Reward classification and master acceptance happen after evidence exists.
- `LooperLog` records feedback at `micro`, `skill`, `composition`, `scaffold`,
  `tool`, or `task` grain. It is evidence/backlog, not accepted change.

Read `references/bridge-control.md` when a loop uses non-metric bridge
surfaces, side-effect gates, operator signals, nested skill attempts, or compact
evidence ledgers.

Read `references/b3ehive-bridge-contract.md` when a loop coordinates multiple
b3ehive skills, needs `EstimatorPolicy`, `RouteDecision`, `EvidenceLint`,
`NestedSkillCall`, `LooperLog`, ROI, ParetoGate, or coding-tool interface
rules.

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

## SideEffectGate

Use minimal side-effect gates for risky operations only:

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

Normal file reads, ordinary reasoning, and harmless local writes inside owned
paths do not need default gates. Workers may create candidates or `[_]`
evidence, but protected surfaces, broad deletion, publishing, spending, and
identity-level writes require explicit gate decisions.

## OperatorSignal

Support operator or master-lane control signals:

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

Pending operator signals must be processed before new leases. `cancel`,
`drain`, and `pause_after_current` block new lease allocation until resolved.

## Nested Runs

Nested b3ehive runs inside a loop attempt must inherit the parent resource
lease unless explicitly granted a child lease:

```text
looper attempt
  -> compete repair search
  -> learn subset understanding
  -> execution child patch
  -> optimization strategy refresh
```

Nested runs cannot write `[x]`, cannot escape the parent lease budget, and
cannot claim accepted reward directly. They produce provisional outputs and
reward candidates. Parent attempt accounting includes nested run cost.

Nested runs should also attach `looper_log` refs when they expose reusable
feedback about route choice, missing validators, scaffold friction, tool
integration, nested depth, or cost/reward mismatch.

## EvidenceLedger

Use compact evidence records rather than full-transcript adjudication. Each
evidence record should name the loop, attempt, lease, input contract, owned
paths, changed files, commands run, validation result, bridge delta refs,
side-effect decisions, nested run refs, reward candidates, and master decision.

## LooperLog

Use looper logs for multi-grain feedback evidence. A log can attach to the
smallest feedback ring whose closure belongs to later review or the master lane,
or to the whole task episode.

Each loop attempt with target or instrument feedback has two observation lanes:

```text
TargetObject = the task, DAG item, artifact, repo change, report, benchmark, or product signal being moved
InstrumentObject = the skill, skill composition, scaffold, validator, route, ledger, script, or tool used to move it
```

Normal execution may change the `TargetObject` within the task boundary. The
`InstrumentObject` may only receive `looper_log` evidence and future backlog
until a separate improvement lifecycle passes EvidenceLint, ROI, ParetoGate,
rollback, and master `[x]`.

Grains:

```text
micro
skill
composition
scaffold
tool
task
```

Minimum fields:

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

State semantics:

```text
[ ] improvement is only a future backlog candidate
[_] looper_log exists with evidence, but no accepted policy/tool/skill change yet
[x] master accepted and applied a real improvement
```

Many `[_]` logs should be batched later by periodic looper review. Recurring
patterns may route to compete, optimization, execution patching, or master
review. Accepted instrument changes still require EvidenceLint, ROI,
ParetoGate, rollback, and master `[x]`.

Runtime rule:

```text
Do the work.
Observe the instruments used to do the work.
Record instrument feedback as looper_log.
Defer instrument mutation to a separate accepted improvement lifecycle.
```

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

## Pause And Resume

Each loop must maintain a no-reward accumulator. Primary reward clears it,
secondary reward reduces it, weak evidence reduces it at most modestly, and
negative reward continues accumulation.

Paused loops must not resume automatically. `paused_no_reward` can return to
`eligible` only when a clear resume event exists:

- explicit resource refund by operator
- new evidence arrived
- new validator added
- bridge target changed
- dependency unblocked
- human approval supplied

Resume must also change strategy. Same loop, same strategy, and no reward is
forbidden.

## Concurrency Model

Looper adds a third cursor to b3ehive's existing worker/master pattern:

```text
DAG Claim Cursor:
  fills normal worker lanes from [ ] DAG items.

Loop Attempt Cursor:
  fills loop daemon lanes from eligible loops with active resource envelopes.

Master Integration Cursor:
  validates [_] outputs and looper candidates in DAG dependency order.
```

Required scheduler order:

1. Read authoritative blueprint, bridge surfaces, bridge signals, loop ledgers,
   and resource ledgers.
2. Process pending operator signals.
3. Release expired leases and dead daemons.
4. Cheaply refresh finished attempt state.
5. Refill normal DAG workers first so core implementation does not starve.
6. Rank eligible loops by bridge priority, ROI, reward recency, and urgency.
7. Allocate leases through the resource broker.
8. Start or wake loop daemons.
9. Defer heavy ROI reports until after worker refill or behind an explicit
   refresh flag.
10. Let the master lane integrate validated candidates in DAG order.

High-concurrency rules:

- Finished attempts do not consume live worker capacity.
- Heavy integration or ROI scans must not block worker refill.
- Dependent loop outputs remain provisional until dependencies are `[x]`.
- Path-overlapping attempts must run in isolated workspaces.
- Resource broker, not individual daemons, controls global concurrency.
- Master lane resolves conflicts and writes accepted `[x]` marks.

## Checklist State Protocol

Looper must preserve b3ehive's checkbox grammar when attached to checklist
items:

- `[ ]` means not done and still claimable.
- `[_]` means worker self-tested or looper candidate exists, but master has not
  accepted it.
- `[x]` means master accepted after validation and integration.

Attempt workers and looper daemons may only create candidates or advance
assigned work to `[_]`. They must never write `[x]`.

Cleanup is forbidden while any attached item remains `[ ]` or `[_]`, while any
loop has live leases, while attempts are unaccounted, while nested runs are
unfinished, or while a pause/resume/operator decision is pending.

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

## Agent Platform Compatibility

Generated looper cron code must support Codex, Claude Code, opencode, OpenClaw,
and Hermes through a single agent-runner abstraction. If
`B3EHIVE_AGENT_RUNNER` is set, use it as the authoritative command template and
print the resolved runner in validate-only output. Do not silently replace a
requested model, service tier, permission mode, variant, profile, agent,
toolset, or preloaded skill list.

## Output Discipline And Anti-Slop Contract

- Begin with the requested loop spec, evidence, decision, or action.
- Give each sentence one checkable fact, rule, decision, consequence, or action.
- Omit process narration, generic disclaimers, filler, restatements, and closing
  recaps.
- Use positive direct statements when truth conditions permit. Preserve
  technical negation for permissions, safety gates, failure behavior,
  pause/resume, privacy, and acceptance.
- Preserve exact object names, field names, schema, enum values, paths, states,
  numeric limits, gate conditions, and cursor order.
- Omit unsupported connective assertions among artifacts, metrics, rewards,
  ROI, decisions, or actions. Handle material uncertainty under the next rule.
- When unresolved uncertainty changes correctness, safety, legality, a gate
  decision, or the available action, state the exact unknown, condition, and
  consequence.
- Include a boundary only when it changes correctness, safety, legality, or the
  available action; name the exact constraint and permitted path.
- Keep the body within 10% above or below a user-supplied length target. With no
  length target, return the shortest complete output that satisfies every
  required schema and gate.
- Verification output contains only the result, its evidence, and its
  operational consequence.
- Before delivery, silently check filler, repeated qualifications, empty
  placeholders, privacy leaks, schema drift, enum drift, path drift, state
  drift, numeric drift, cursor order, reward and ROI accounting, pause and
  resume gates, permissions, and cleanup gates.

## Workflow

1. Inspect the repository and identify the intended bridge surfaces, bridge
   metrics, DAG nodes, validators, and resource boundaries.
2. Confirm the loop is project-neutral if it will be committed. Move private
   names and local paths into ignored local config.
3. Create or update `Docs/looper/LOOP_SPEC.md`,
   `Docs/looper/BRIDGE_SURFACES.md`, and `Docs/looper/BRIDGE_METRICS.md` with
   sanitized examples.
4. Add private runtime ledgers under `.b3ehive/looper/` and `.cron/looper/`,
   then hide them from git.
5. Create the required pieces:
   - loop spec validator
   - bridge surface/signal reader
   - resource broker
   - lease allocator
   - side-effect gate evaluator
   - operator signal reader
   - looper guard
   - daemon runner
   - nested run ledger
   - compact evidence ledger
   - multi-grain looper_log ledger
   - reward/ROI accountant
   - pause/resume ledger
   - cron space/log guard
   - installer and cleanup scripts
6. Run `VALIDATE_ONLY=1` before installing cron. Validate spec shape, privacy
   rules, bridge shape, resource envelopes, leases, validators, and disk
   budgets.
7. Run one manual loop tick with a tiny resource envelope.
8. Verify attempts can create candidates or `[_]` evidence only.
9. Verify the master lane is the only actor that can accept `[x]`.
10. Install cron only after validate-only, one manual tick, budget guard, and
    privacy scan pass.
11. Pause loops automatically when no-reward thresholds are hit.
12. Resume paused loops only with explicit refund and required strategy change.
13. Clean up only when no live leases, no pending attempts, no unfinished
    nested runs, no unfinished attached checklist items, and no pending
    pause/resume/operator decisions remain.

## Validation

Before declaring a Looper ready:

- validate YAML/JSON syntax for loop specs, bridge surfaces, bridge signals,
  metrics, envelopes, leases, and ledgers
- verify every loop has at least one bridge surface, bridge metric, or DAG node
  attachment
- verify every BridgeSurface has `bridge_level` and `evidence_policy`
- verify every BridgeSignal has `signal_type` and `failure_signal`
- verify every BridgeDelta has `before_ref` and `after_ref`
- verify every loop has a validator or an explicit monitoring evidence source
- verify every attempt requires a resource lease
- verify every nested run has `ParentLeaseRef`
- verify nested run spend rolls into parent lease accounting
- verify pending operator signals are processed before new leases
- verify protected side effects have gate decisions
- verify reward candidates point to compact evidence records
- verify looper_log entries exist when attempts produce target or instrument
  feedback at micro, skill, composition, scaffold, tool, or task grain
- verify looper_log entries include TargetObject/target_feedback and
  InstrumentObject/instrument_feedback when either side produced evidence that
  affects a decision, gate, reward, or backlog item
- verify no-reward accumulator thresholds exist
- verify ROI ledger fields exist
- verify paused loops cannot resume without refund and strategy change
- verify worker prompts cannot write `[x]`
- verify master integration gate is documented
- run the cron space guard once
- run `bash -n` on generated shell helpers
- run a privacy scan for local absolute paths and private names before
  committing

## Common Failure Modes

- adding feedback edges directly to the DAG and creating cycles
- treating `BridgeMetric` as the only bridge type
- recording bridge movement without before/after refs
- counting bridge deltas as reward before master classification
- starting attempts without resource leases
- letting nested compete, learn, execution, or optimization runs escape parent
  lease accounting
- letting paused loops start nested runs
- allowing workers to mutate protected authoritative surfaces
- treating operator cancel or drain as best-effort instead of authoritative
  loop state
- using full transcript review when compact evidence would suffice
- treating no-reward attempts as harmless retries
- resuming a paused loop with the same strategy and fresh budget only
- measuring token spend but not human review time or disk/log pressure
- counting narrative summaries as reward without evidence
- treating looper_log as accepted policy/tool/skill change
- mutating an InstrumentObject during the same runtime attempt that first
  observed the instrument feedback
- allowing daemon workers to write `[x]`
- letting heavy ROI reporting block worker refill
- committing private metric names, local paths, or customer identifiers

## Project-Specific Extensions

Core Looper machinery excludes:

- plan-understanding quizzes
- draft relevance checkers
- read validators
- full transcript compliance judges
- dense prompt-template validators
- hook chains around every operation
- separate long-term feedback subsystem
- separate looper-log public skill
- new public bridge or feedback skill

An explicit project requirement may add one of these as a project-specific
validator or side-effect gate under an existing loop. It stays outside core
Looper machinery.

## References

Read only the relevant reference:

- `references/looper-pattern.md` for the full pattern and runtime examples.
- `references/bridge-control.md` for BridgeSurface, BridgeSignal, BridgeDelta,
  SideEffectGate, OperatorSignal, NestedRunLedger, ParentLeaseRef, and
  EvidenceLedger.
- `references/b3ehive-bridge-contract.md` for shared state, EstimatorPolicy,
  RouteDecision, NestedSkillCall, EvidenceLint, LooperLog, ROI, ParetoGate,
  B3IR, anti-bloat, and prompt/hook boundary rules.
- `references/privacy-checklist.md` for publication hygiene.
