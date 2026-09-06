---
name: learn-cron-builder
description: Build or repair a source-to-target learning cron for code understanding, subset learning, code-to-code transformation, API/schema/runtime/tool transformation, or human-language translation. Use when a repo needs code-to-human learning notes, strict one-to-one source file plus source-tree output coverage, explicit or fuzzy subset learning, code-to-code transformation, documentation translation, route-policy selection, dual-cursor checklists, master-only acceptance, or cleanup after all learning artifacts are validated.
---

# Learn Cron Builder

Convert a frozen source scope into validated learning or transformation
artifacts through a repository-local pipeline. The working frame is
`understand it until make it`.

## Modes And Flow

| Mode | Direction | Output |
|---|---|---|
| `learn_mode=understand` | code -> human language | One-to-one learning notes and source-tree understanding artifacts. |
| `learn_mode=transform` | code -> code | Code-to-code, API/schema/runtime transformation, SDK generation, adapter generation, or tool-asset conversion artifacts. |
| `learn_mode=translate` | human language -> human language | Documentation language conversion and localization artifacts. |

Every mode follows:

```text
source scope -> subset policy -> source manifest -> target contract
-> worker output [_] -> master validation [x] -> cleanup
```

## Output Discipline And Anti-Slop Contract

- Start with the requested artifact, manifest fact, mapping, route decision,
  validation result, or source fact.
- Give each sentence one concrete requirement, mapping, decision, action,
  result, evidence item, or consequence. Omit process narration, opening
  meta-commentary, generic disclaimers, filler, restatements, and closing recaps.
- Report verification only through its result, evidence, and consequence.
- Omit relationship or causal claims unsupported by manifest, source, or
  validator evidence. Handle material uncertainty under the next rule; leave no
  speculative transition, inferred mapping, or placeholder.
- When unresolved uncertainty changes correctness, safety, legality, mapping,
  or the available action, state the exact unknown, condition, and consequence.
- Include a boundary only when it changes correctness, safety, legality, or the
  available action; name the exact constraint and permitted path.
- Use direct, positive statements when truth conditions permit. Preserve
  technical negation for scope exclusions, permissions, safety gates, failure
  behavior, traceability, and acceptance rules.
- Keep the body within 10% above or below an explicit target length. Without a
  target, use the shortest complete form that preserves the artifacts,
  mappings, evidence, decisions, and consequences.
- Before delivery, silently inspect the text character by character for filler,
  duplicated safeguards, unsupported claims, vague predicates, stale
  placeholders, fabricated mappings, coverage gaps, missing sections, and
  length. Preserve the exact spelling of state marks, schema keys, commands,
  paths, enums, thresholds, mode names, and validator-dependent strings.

## Shared b3ehive Contract

Follow `../looper-cron-builder/references/b3ehive-bridge-contract.md` for route
selection, estimator decisions, nested calls, evidence handoff, `looper_log`
capture, ROI, and self-evolution.

Local obligations:

- `source_manifest.tsv` and one-to-one file plus folder coverage are hard caps,
  not estimator choices.
- Every nontrivial automatic subset, route, batch, split, transform, or
  translate choice should leave `EstimatorPolicy` and `RouteDecision` evidence.
- Workers produce only `[_]` artifacts. Master validation alone writes `[x]`.
- Coverage gaps, fuzzy-subset ambiguity, manifest friction, route over- or
  under-spend, translation-route mismatch, transform-traceability friction,
  scaffold weakness, or tool-integration friction produces a `looper_log`.
- Each `looper_log` must identify the understood, transformed, or translated
  `TargetObject` and the signal-producing `InstrumentObject`: subset policy,
  manifest, route, traceability scaffold, validator, tool, or skill composition.
- A looper-log-derived change to coverage, route, transform, or translation
  policy requires EvidenceLint, ROI, ParetoGate, rollback, and master `[x]`.

## Acceptance State

- Generate and lock `source_manifest.tsv` before worker claims.
- Use `[ ]`, `[_]`, and `[x]` as the only checkbox states.
- Workers may only advance `[ ] -> [_]`.
- The master lane is the only actor that may advance `[_] -> [x]`.
- Cleanup treats `[ ]` and `[_]` as unfinished.
- Completion requires zero `[ ]`, zero `[_]`, and passing coverage indices.

For `learn_mode=understand`, final artifacts map one-to-one to source files and
preserve the source-tree shape:

```text
src/app/main.ts
  -> Docs/learn/files/src/app/main.ts_learn.md

.github/workflows/ci.yml
  -> Docs/learn/files/.github/workflows/ci.yml_learn.md

src/app/
  -> Docs/learn/src/app/current_folder_learn.md

repo root
  -> Docs/learn/current_folder_learn.md
```

Opaque slug-only final paths are invalid. Group and chunk reports remain
intermediate artifacts.

## Subset Contract

Explicit and fuzzy subsets are first-class inputs.

Explicit subsets include:

```text
src/auth/**
packages/compiler/**
files touched by this branch
language=rust
```

Fuzzy subsets include:

```text
algorithm subset
scheduler core
inference path
payment risk surface
```

Each fuzzy subset produces:

```text
Docs/learn/subsets/<subset_id>/subset_candidates.tsv
Docs/learn/subsets/<subset_id>/subset_decision.md
Docs/learn/subsets/<subset_id>/source_manifest.tsv
```

Workers may read context-only files. Those files produce no final artifact and
do not count toward completion until promotion into the locked source manifest.

## Required Surfaces

Base files:

```text
Docs/learn/source_manifest.tsv
Docs/learn/learn_checklist.md
Docs/learn/todos_YYYYMMDD.md
Docs/learn/file_learn_index.tsv
Docs/learn/folder_learn_index.tsv
Docs/learn/route_decision.md
```

Transform mode also requires:

```text
Docs/learn/target_contract.md
Docs/learn/mapping_policy.tsv
Docs/learn/validation_policy.md
Docs/learn/traceability_index.tsv
```

## Route Policy

Route choice is contractual:

```text
route_policy=auto|high_reasoning|standard|cheap_translation|uncommon_translation|custom
```

Defaults:

- `understand`: high reasoning for complex code; standard for small or simple
  files.
- `transform`: high reasoning for code/API/schema/runtime; standard for
  mechanical tool-asset conversion.
- `translate`: cheap or uncommon translation route by default; escalation is
  limited to high-stakes meaning, code-heavy semantics, glossary conflicts,
  repeated validator failure, or an explicit human request.

Write every route decision to `Docs/learn/route_decision.md`.

## Validation

Before declaring a learn cron ready, verify:

- `source_manifest.tsv` covers exactly the locked source scope.
- Final per-file artifacts map exactly one-to-one to source files.
- Folder artifacts cover every represented folder.
- `[_]` remains unfinished, and workers cannot write `[x]`.
- Subset output excludes out-of-scope files.
- Transform output carries source-target traceability.
- Translate output preserves headings, anchors, links, code blocks, tables,
  glossary decisions, and section parity.
- Runs with instrument feedback contain `looper_log` entries at `micro`,
  `skill`, `composition`, `scaffold`, `tool`, or `task` grain.
- The cron space guard passes.
- Generated shell helpers pass `bash -n`.

## Looper Handoff

When embedded in `looper-cron-builder`, learn may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Learn output remains provisional until
the looper or owning master lane accepts it.

Nested learn runs cannot write `[x]`, escape the parent lease budget, or
classify final reward. They produce reward candidates only. Token, wall-clock,
human-review, disk, and output costs roll into the parent looper attempt before reward
and ROI accounting. Paused loops cannot start nested learn runs.

Nested learn should emit `looper_log` refs when subset choice, manifest shape,
one-to-one coverage, route, transform traceability, translation parity, or
generated tooling yields reusable instrument feedback. The log should separate
target feedback from instrument feedback so review can distinguish source-subset
difficulty from learn-pipeline configuration.

## References

Read only the relevant reference:

- `references/coverage-contract.md`: strict 1:1 file tree, grouping, chunking,
  folder synthesis, and subset coverage.
- `references/route-policy.md`: mode-specific route selection and escalation.
- `references/learn-pattern.md`: full workflow, components, and behavior
  coverage.
