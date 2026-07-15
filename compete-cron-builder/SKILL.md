---
name: compete-cron-builder
description: Run or embed a bounded proposal competition for coding, research, planning, coverage, repair, blueprint, SEO, audit, or execution-choice tasks. Use when a task needs n workers, m proposals, choose k, all-valid coverage union, three-way challenge output under run_a/run_b/run_c, verifier checks, peer review, revision, vote selection, repair synthesis, or execution/looper handoff.
---

# Compete Cron Builder

Turn one local question into a bounded proposal competition.

## Competition Contract

```text
n workers
m proposals, optional or auto
choose k, optional or auto
or union all valid findings
```

Inputs:

| Field | Values or meaning |
|---|---|
| `task` | Question or work request. |
| `budget_workers` | Human-provided worker/resource budget. |
| `proposal_count` | Explicit count or `auto`. |
| `choose_count` | Explicit count, `auto`, or `all_valid`. |
| `question_type` | `auto`, `precision`, `coverage`, `audit`, `blueprint`, `seo`, `execution_choice`, or `repair`. |
| `competition_shape` | `auto`, `three_way_challenge`, `parallel_proposals`, `coverage_sweep`, `repair_search`, or `top_k_synthesis`. |
| `selection_mode` | `auto`, `best_one`, `top_k`, `coverage_union`, `risk_union`, `vote_then_tiebreak`, or `repair_queue`. |
| `artifact_layout` | `native` or `old_three_way`. |

Possible outputs are candidates, selected plans, repair assignments, coverage
findings, validation hints, and handoff metadata. Candidate outputs are `[_]`
evidence only; they never write `[x]`. The execution or looper master lane alone
accepts final completion as `[x]`.

## Output Discipline And Anti-Slop Contract

- Start with the requested artifact, finding set, selection, decision, or fact.
- Give each sentence one concrete requirement, observation, decision, action,
  result, evidence item, or consequence. Omit process narration, opening
  meta-commentary, generic disclaimers, filler, restatements, and closing recaps.
- Report verification only through its result, evidence, and consequence.
- Omit unsupported relationship or causal claims. Handle material uncertainty
  under the next rule; leave no speculative transition or placeholder.
- When unresolved uncertainty changes correctness, safety, legality, selection,
  or the available action, state the exact unknown, condition, and consequence.
- Include a boundary only when it changes correctness, safety, legality, or the
  available action; name the exact constraint and permitted path.
- Use direct, positive statements when truth conditions permit. Preserve
  technical negation for exclusions, permissions, safety gates, failure
  behavior, and acceptance rules.
- Keep the body within 10% above or below an explicit target length. Without a
  target, use the shortest complete form that preserves the artifacts,
  evidence, decisions, and consequences.
- Before delivery, silently inspect the text character by character for filler,
  duplicated safeguards, unsupported claims, vague predicates, stale
  placeholders, fabricated evidence, missing sections, and length. Preserve
  the exact spelling of state marks, schema keys, commands, paths, enums,
  thresholds, stage names, and validator-dependent strings.

## Shared b3ehive Contract

Follow `../looper-cron-builder/references/b3ehive-bridge-contract.md` for nested
calls, route selection, auto m/k decisions, evidence handoff, `looper_log`
capture, ROI, and self-evolution.

Local obligations:

- Every nontrivial automatic `proposal_count`, `choose_count`, shape, selection,
  or route choice should leave an `EstimatorPolicy` or `RouteDecision` record.
- Coverage and audit runs use all-valid/risk union unless a stronger local
  route decision selects another policy.
- Route cost, a missing validator, mis-sized m/k, candidate overlap, scaffold
  friction, or tool integration friction produces a `looper_log` at `skill`,
  `composition`, `scaffold`, `tool`, or `task` grain.
- Each `looper_log` must identify the decided or covered `TargetObject` and the
  `InstrumentObject` that produced the signal: competition shape, route,
  validator, scaffold, tool, or skill composition.
- A looper-log-derived compete policy change requires EvidenceLint, ROI,
  ParetoGate, rollback, and master `[x]`.

## Commands

Run the fully covered old three-agent workflow with compete terminology:

```bash
python3 scripts/compete_cron_builder.py \
  --task "Improve this module and test the result" \
  --output ./competition-runs/manual-test \
  --budget-workers 3 \
  --competition-shape three_way_challenge \
  --artifact-layout old_three_way \
  --runner mock \
  --max-output-mb 20 \
  --min-free-gb 0
```

Run a coverage competition:

```bash
python3 scripts/compete_cron_builder.py \
  --task "Find security and validation risks in this API surface" \
  --output ./competition-runs/security-sweep \
  --budget-workers 6 \
  --question-type coverage \
  --selection-mode coverage_union \
  --choose-count all-valid \
  --runner mock
```

Use `--runner command --command '<agent command template>'` for a live agent
runner. Template variables available to `--command`:

- `{agent_id}`: candidate id, such as `run_a` or `proposal_001`
- `{run_id}`: the same stable candidate id
- `{candidate_id}`: the same stable candidate id
- `{stage}`: workflow stage
- `{prompt_file}`: generated prompt file
- `{output_file}`: stdout capture path
- `{competition_id}`: manifest run id
- `{question_type}`: resolved question type
- `{selection_mode}`: resolved selection mode

## Three-Way Challenge

`competition_shape=three_way_challenge` resolves to:

```text
candidate_ids = run_a, run_b, run_c
selected_count = 1
selection_mode = vote_then_tiebreak
tie_break = stable_candidate_id
```

Stages:

1. `proposal`: three candidates produce first results.
2. `initial_verification`: the verifier checks candidate outputs.
3. `peer_review_round_1`: each candidate critiques the other two.
4. `revision_round_1`: each candidate revises its own result.
5. `peer_review_round_2`: each candidate critiques revised peers and votes.
6. `repair_synthesis`: each candidate writes final repair assignments.

`artifact_layout=old_three_way` preserves:

```text
<output>/
  run_a/implementation/
  run_b/implementation/
  run_c/implementation/
  verification.md
  best_run.txt
  final_repairs.md
  summary.md
```

Each candidate directory contains:

- `result.md`
- `verification.md`
- `critique_round_1.md`
- `update_round_1.md`
- `critique_round_2.md`
- `final_repair.md`

Native manifests and JSON summaries may supplement these artifacts. Under
`old_three_way`, they do not replace them.

## m/k Policy

When the user supplies only worker budget `n`, resolve proposal and selection
counts from question type:

- `precision`: `m=min(n,4)`, `k=1` or `2`; choose the best candidate or a
  fallback pair.
- `coverage`: bound `m` by budget, set `k=all_valid`, and merge valid findings.
- `audit`: bound `m` by budget, set `k=all_valid`, and rank risks by severity.
- `blueprint`: `m=min(n,5)`, `k=2` or `3`; synthesize a blueprint patch.
- `seo`: synthesis for strategy, union for coverage, and repair for execution.
- `execution_choice`: `m=min(n,3)`, `k=1`; choose one local implementation path.
- `repair`: `m=min(n,4)`; choose a primary repair and fallback.
- `three_way_challenge`: `m=3`, `k=1`; vote, then apply the stable tie-break.

## Execution Handoff

When embedded in `execution-cron-builder`, compete preserves the single
authoritative blueprint source and an acyclic DAG. Workers and compete
candidates may produce only proposals or `[_]` evidence. Compete must never
write `[x]`; the master alone promotes `[_] -> [x]`. After master deduplication,
repair and coverage outputs enter the
blueprint as `[ ]` child items.

Valid handoff actions:

- `create_child_items`
- `enqueue_integration_hint`
- `write_blueprint_patch_proposal`
- `write_validation_hint`
- `write_repair_assignment`
- `request_master_review`

## Looper Handoff

When embedded in `looper-cron-builder`, compete may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Token, wall-clock, human-review, disk,
and diff costs count against the parent lease. Candidate output remains
provisional until the master accepts it in DAG order.

Record a compete-heavy loop with no primary or secondary reward in the
no-reward accumulator. A paused loop requires an explicit resource refund and a
strategy change before resuming.

Nested compete runs cannot write `[x]`, escape the parent lease budget, or
classify final reward. They produce reward candidates only; the parent looper
attempt owns reward classification and ROI accounting.

Nested competition emits `looper_log` refs for reusable instrument signals,
including excessive proposal overlap, question-type mismatch, unnecessary
model route, missing validator, and inefficient repair-queue shape. Separate
target feedback from instrument feedback so review can distinguish task
difficulty from competition configuration.

## Runtime Rules

- Run parallel candidates with all-settled behavior.
- The competition continues when at least one candidate succeeds.
- Zero valid candidates stops the run and writes a failure summary.
- Bound captured output with `--max-output-mb`.
- Run the cron space guard before cron-launched competitions.
- Do not let parallel candidates mutate the same authoritative source tree.
- Prefer patches, plans, diffs, findings, or artifacts under candidate output
  directories.
- Resolve ties deterministically by stable candidate id.

## Reference

Read `references/competition-pattern.md` when adapting compete to another
runtime, embedding it in execution cron, or wiring it to looper attempts.
