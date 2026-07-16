# b3ehive Codex Plugin

[中文说明](README.zh-CN.md)

b3ehive packages five Codex skills for bounded multi-agent work: proposal
competition, blueprint execution, source learning, architecture optimization,
and resource-aware feedback loops. The bundled `SKILL.md` directories under
`skills/` define its behavior. The package adds no MCP server, app, or hook.

## Skills

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

## How To Choose A Skill

| Need | Use | What it produces |
|---|---|---|
| Compare possible routes before committing to one | `compete-cron-builder` | Candidate proposals, selected plan, coverage union, repair queue, or execution handoff |
| Execute a confirmed blueprint in a repository | `execution-cron-builder` | DAG checklist, daily todo, worker batches, validation gates, checkpoints, cleanup |
| Understand, transform, or translate a source scope | `learn-cron-builder` | Source manifest, coverage contract, learning notes, transformed code, or translated docs |
| Turn a design philosophy into architecture refinement work | `optimization-cron-builder` | `Stage_*_AR_Blueprint.md` and per-item optimization research docs |
| Add bounded feedback, resource control, reward, and ROI tracking | `looper-cron-builder` | Loop specs, resource leases, evidence ledgers, reward/ROI records, pause/resume control |

Each skill may be an entry point. Select it from the task state:

- If the route is unclear, start with `compete-cron-builder`.
- If the source is unclear, start with `learn-cron-builder`.
- If the architecture direction is clear but needs refinement work, start with
  `optimization-cron-builder`.
- If the blueprint is already confirmed, start with `execution-cron-builder`.
- If repeated attempts, metrics, budgets, or human feedback must be controlled,
  add `looper-cron-builder` around the work.

## Trigger Conditions And Boundaries

### `compete-cron-builder`

Select this skill for:

- `n` workers, `m` proposals, and `choose k`.
- A three-way challenge under `run_a`, `run_b`, and `run_c`.
- Best-one selection, top-k synthesis, coverage union, risk union, or repair
  queue.
- Multiple independent proposals before writing a feature blueprint.
- An evidence-bearing handoff into `execution-cron-builder` or
  `looper-cron-builder`.

Prompt examples:

```text
Use compete-cron-builder to compare implementation routes for this feature and synthesize a blueprint.
Use compete-cron-builder with three proposals and choose the safest plan.
Use compete-cron-builder to run a coverage sweep for risks in this API.
```

Outputs include proposals, findings, selected plans, and handoff metadata.
Candidate workers cannot mark execution checklist items `[x]`. Final acceptance
belongs to the execution or looper master lane.

### `execution-cron-builder`

Select this skill when one authoritative blueprint defines implementation:

- A repository-local execution cron for one blueprint.
- A dependency DAG for open checklist items.
- Worker/master split lanes, where workers produce `[_]` and the master lane
  accepts `[x]`.
- Validation gates, checkpoint commits, cleanup-on-complete, and bounded
  worker batches.
- Repair of an existing blueprint-execution cron whose gates or boundaries are
  wrong.

Prompt examples:

```text
Use execution-cron-builder for this repo and this confirmed blueprint.
Use execution-cron-builder to build a DAG todo and validation gate for this spec.
Use execution-cron-builder to repair the existing execution cron boundaries.
```

This skill implements a confirmed blueprint. It reads exactly one authoritative
requirement source before generating todos or worker prompts.

### `learn-cron-builder`

Select this skill for a bounded source scope that needs:

- Code-to-human learning notes.
- Strict one-to-one source file plus source-tree coverage.
- Explicit or fuzzy subset learning.
- Code-to-code transformation, API/schema/runtime/tool conversion, SDK
  generation, or adapter generation.
- Human-language documentation translation.
- A `source_manifest.tsv`, route policy, coverage contract, and master-only
  acceptance.

Prompt examples:

```text
Use learn-cron-builder to understand this package into one-to-one learning notes.
Use learn-cron-builder in transform mode for this API schema migration.
Use learn-cron-builder to translate these docs with source coverage validation.
```

Its outputs are validated learning, transform, or translation artifacts. They
may feed a later blueprint. Product code requires its own implementation and
acceptance lifecycle.

### `optimization-cron-builder`

Select this skill when a design philosophy governs structured architecture
refinement:

- A bounded `Stage_*_AR_Blueprint.md`.
- At most 100 architecture refinement checklist items.
- Per-item research docs under `Docs/researches/Stage_*_AR/`.
- Parallel worker ownership by blueprint section.
- A repo-specific optimization plan filtered through a stated design
  philosophy.

Prompt examples:

```text
Use optimization-cron-builder with this design philosophy: reduce cognitive load and simplify extension points.
Use optimization-cron-builder to derive an AR blueprint for this stage.
Use optimization-cron-builder to research each architecture refinement item before implementation.
```

This skill creates optimization research and an AR blueprint. Product-code
implementation remains outside its default scope and may proceed through
`execution-cron-builder`.

### `looper-cron-builder`

Select this skill for repeated attempts under explicit resource, reward, and
side-effect control:

- Bounded attempts around DAG nodes, bridge surfaces, bridge metrics, product
  validation goals, benchmark lanes, or monitoring signals.
- Resource leases, budgets, compact evidence ledgers, reward signals, ROI
  tracking, and no-reward pause rules.
- Side-effect gates for risky writes, publishing, deletion, spend, or external
  calls.
- Operator-controlled feedback loops and re-funded resume after a paused loop.
- Nested b3ehive skill attempts with attribution and master acceptance.

Prompt examples:

```text
Use looper-cron-builder to control repeated validation attempts around this benchmark lane.
Use looper-cron-builder to add ROI tracking and no-reward pause rules to this workflow.
Use looper-cron-builder around these bridge surfaces and side-effect gates.
```

Looper is a feedback overlay beside DAG nodes or bridge surfaces; the dependency
graph remains acyclic. The master lane accepts final completion after validation
passes.

## Common Workflows

### New Feature With Unclear Route

```text
compete-cron-builder -> execution-cron-builder
```

`compete-cron-builder` generates and compares proposals.
`execution-cron-builder` implements the selected blueprint.

### Existing Codebase You Do Not Understand Yet

```text
learn-cron-builder -> compete-cron-builder -> execution-cron-builder
```

`learn-cron-builder` freezes source coverage and produces validated notes or
transforms. `compete-cron-builder` follows when multiple implementation routes
remain plausible.

### Architecture Improvement

```text
optimization-cron-builder -> execution-cron-builder
```

`optimization-cron-builder` derives the AR blueprint and research docs.
`execution-cron-builder` starts after the AR blueprint becomes the accepted
authoritative implementation source.

### Long-Running Work With Feedback Or Budget Risk

```text
execution-cron-builder + looper-cron-builder
```

`execution-cron-builder` owns the DAG implementation path.
`looper-cron-builder` owns repeated attempts, metric movement, reward/ROI
accounting, side-effect gates, and pause/resume control.

## Shared Concepts

`DAG` means `Directed Acyclic Graph`: a directed dependency graph with no
cycles. In b3ehive, it records task dependency order. Downstream acceptance
requires accepted upstream dependencies.

All five skills share the dual-cursor checklist protocol:

- `[ ]` means not done.
- `[_]` means worker self-tested, awaiting master acceptance.
- `[x]` means master accepted after validation.

Workers may move `[ ] -> [_]`. The master lane is the only actor that may move
`[_] -> [x]`.

## Install

From the repository root:

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

From GitHub:

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new Codex thread after installation so the bundled skills are loaded.

## Source Of Truth

The root skill directories are the source of truth:

```text
compete-cron-builder/
execution-cron-builder/
learn-cron-builder/
optimization-cron-builder/
looper-cron-builder/
```

`plugins/b3ehive/skills/` is the packaged copy. Before release, run the sync
command from the repository root:

```bash
scripts/sync_codex_plugin.sh
```

See [docs/codex-plugin.md](../../docs/codex-plugin.md) for the full install,
maintenance, validation, and release contract.
