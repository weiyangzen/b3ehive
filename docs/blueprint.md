# Blueprint

[中文](blueprint.zh-CN.md)

For a first execution, read [Getting Started](getting-started.md) and
[Skill Selection and Use](skill-selection.md) first.

A blueprint is the single source of requirements, state, and dependencies for a
run. Guards read it to decide what is open, blocked, and acceptable.

The blueprint is the authority. A Gantt or todo view is a read-only projection.

## Item Grammar

```markdown
- [ ] [ITEM-030] title
  - depends_on: [ITEM-010, board#HW-041]
  - owned_paths: src/hal/, verify/gates/ITEM-030.sh
  - oracle: verify/gates/ITEM-030.sh
  - tier: T1
  - budget: loc<5000
  - canon: [A2, SPEC-12§4.4]
```

| Field | Required | Meaning |
|---|---|---|
| id | yes | stable unique id |
| `oracle` | yes | gate command, or `review:<protocol>` run by a non-author |
| `depends_on` | no | ids this item needs; `other#ID` points into another blueprint and blocks acceptance only |
| `owned_paths` | no | the only paths a worker may change |
| `tier` | no | minimum evidence fidelity for `[x]`; lower evidence stops at `[_]` |
| `budget` | no | size cap; an item estimated above it splits before claim |
| `canon` | no | canon ids that govern the item's design |
| `layer` | no | strict layer gate: lower layers close first |

## States

| Mark | Meaning | Who sets it |
|---|---|---|
| `[ ]` | open or rejected | blueprint author, master |
| `[_]` | submitted with a receipt | controller after harvest |
| `[x]` | accepted after a re-run | master |

Cleanup needs zero `[ ]` and zero `[_]`. Words such as blocked or paused are
telemetry and never replace a mark.

## Rules

- One authority per run; derived todos and the Gantt projection are read-only.
- An item without an oracle gets a parent item that builds it.
- Duplicate ids, missing dependencies, cycles, and unknown marks fail
  validation.
- A parent closes only when every child is `[x]`.
- A guard may split an item stuck across ticks into children.
- An `[I]` canon fact blocks dependent acceptance until a gate confirms it.

## Lifecycle

```text
bootstrap [ ] → claim → submit [_] → master re-run → accept [x] → cleanup
                               └→ reject [ ] with notes → next generation
```

## By Skill

| Skill | Blueprint |
|---|---|
| execution | requirements plus checklist in one Markdown file |
| learn | `learn_checklist.md` derived from a locked `source_manifest.tsv` |
| optimization | `Stage_*_AR_Blueprint.md` (design) or an oracle contract plus hypothesis ledger (measured, normally serial) |
| compete | a decided question type, m, k, and oracle |
| looper | optional external loop specs attached to items, metrics, or surfaces |
