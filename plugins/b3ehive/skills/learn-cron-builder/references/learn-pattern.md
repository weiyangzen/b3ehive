# Learn Cron Pattern

## Workflow

1. Inspect the repository and identify the learning intent.
2. Resolve `learn_mode`: `understand`, `transform`, or `translate`.
3. Resolve explicit or fuzzy subset, if requested.
4. Freeze `source_manifest.tsv`.
5. Freeze target contract and route policy.
6. Generate `learn_checklist.md`.
7. Generate `todos_YYYYMMDD.md`.
8. Run validate-only.
9. Run one manual guard tick.
10. Install cron only after checklist, todo, guard, route, and disk/log checks pass.
11. Let workers produce `[_]` outputs only.
12. Let master validate and promote `[_] -> [x]`.
13. Clean up only after zero `[ ]`, zero `[_]`, and all coverage/contract gates pass.

Generated crons should create private runtime state under `.cron/` and local
helpers under `.ops/`. Use isolated worker clones for parallel target writes
unless the run is read-only plus generated-output-only and the repository is
clean.

## Modes

### Understand

Code to human learning notes.

Required per-file content:

```text
source_path
source_hash
purpose
exports / entry points
control flow
state and data model
dependencies
side effects
validation/test signals
risks
unknowns
how to remake or modify this file safely
```

### Transform

Code to code or source contract to target artifact.

Examples:

- Python module -> Rust crate
- JavaScript SDK -> TypeScript SDK
- REST API -> typed SDK
- JSON schema v1 -> schema v2
- legacy config -> new config
- Codex/Claude/opencode/OpenClaw/Hermes asset conversion

Required contract files:

```text
Docs/learn/target_contract.md
Docs/learn/mapping_policy.tsv
Docs/learn/validation_policy.md
Docs/learn/traceability_index.tsv
```

Required contract fields:

```text
source contract
target contract
source scope
output root
mapping policy
validation policy
traceability policy
rollback policy
completion gate
```

Allowed mapping modes:

```text
one_to_one
one_to_many
many_to_one
generated_support
```

Workers must not mutate source artifacts. If in-place transformation is
required, stage it in an isolated clone and let the master lane merge validated
outputs.

Common transform surfaces:

- AI tool assets across Codex, Claude Code, Cursor, Grok Build, opencode,
  OpenClaw, and Hermes.
- Programming language or SDK transformations.
- API, schema, runtime, configuration, or adapter transformations.
- Generated support artifacts such as indexes, manifests, compatibility shims,
  and rollback notes.

### Translate

Human language to human language.

Validators:

- source section coverage
- heading/anchor preservation
- link preservation
- code block preservation
- table preservation
- glossary consistency
- technical meaning change ledger

## Dual Cursor

```text
[ ] = not learned / not transformed / not translated
[_] = worker self-tested output exists, master has not accepted
[x] = master accepted after validation and reconciliation
```

Workers cannot write `[x]`. Cleanup cannot run with `[ ]` or `[_]`.

## Runtime Requirements

Generated learn crons must preserve the old runner and resource controls:

- Use a configurable agent runner instead of hard-coding one CLI.
- Support `B3EHIVE_AGENT_PLATFORM=codex|claude|cursor|grok|opencode|openclaw|hermes|auto`.
- Treat `B3EHIVE_AGENT_RUNNER` as authoritative when it is set.
- Run `.cron/scripts/cron_space_guard.sh` or an equivalent helper before worker
  spawn.
- Keep log and workspace budgets environment-overridable, including
  `MIN_FREE_GB`, `DANGER_FREE_GB`, `MAX_LOG_MB`, `MAX_KEEPALIVE_MB`,
  `LOG_RETENTION_DAYS`, `WORKSPACE_TTL_HOURS`, and `MAX_CRON_ROOT_GB`.
- Never delete live worker workspaces referenced by process state, pid files,
  locks, selected agent-runner processes, shells, or tmux sessions.
- When key pools are used, treat unique key count as a capacity input and log
  worker slot plus key index on auth, quota, or rate-limit failures.
- Keep claim and master queues separate: live workers consume capacity;
  finished `[_]` outputs waiting for master validation do not.
- Refresh worker output manifests at the start of each guard tick, including
  drain/no-new-claim mode.

## Looper Embedding

When a looper attempt invokes learn for subset understanding, transformation,
translation, or bridge-surface learning:

- require an active parent `ResourceLease`
- write a `ParentLeaseRef`
- record the run in the looper `NestedRunLedger`
- keep all outputs provisional until master acceptance
- never write `[x]` from the nested learn run
- roll token, wall-clock, human-review, disk, and output costs into parent
  no-reward accounting
- stop immediately if the parent loop is paused, drained, cancelled, or lacks
  budget

## Repair Rules

When a run is already in motion and progress state is wrong:

1. Stop or drain workers first.
2. Regenerate the checklist from the locked source manifest and target contract.
3. Preserve stable `[ ]`, `[_]`, and `[x]` marks by source item id.
4. Reconcile `[_]` only from worker outputs plus self-test evidence.
5. Reconcile `[x]` only from master-accepted artifacts that pass coverage and
   validation gates.
6. Regenerate today's todo and status output before resuming claims.
7. If the checklist is empty or corrupted, fix the generator to use atomic
   writes, rebuild from source manifest, and copy to any expected alias.

## Mode Coverage

Code understanding maps to:

```text
learn_mode=understand
```

Source transformation and human-language translation map to:

```text
learn_mode=transform
learn_mode=translate
```

Do not create additional public wrappers for these modes.
