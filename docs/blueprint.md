# Blueprint

[中文](blueprint.zh-CN.md)

> A blueprint is the single authoritative requirement source for a b3ehive workflow.
> It is the hive's executable specification, progress ledger, and dependency map.

---

## 1. What Is A Blueprint?

A blueprint is not a traditional static requirements document. It is a living
specification that carries execution state and directly drives agent work.

### 1.1 Core Traits

| Trait | Meaning |
|---|---|
| **Single authority** | Each skill run should have exactly one blueprint source. Conflicting requirement sources are not allowed. |
| **Embedded checklist** | The blueprint contains `[ ]`, `[_]`, and `[x]` checklist states. The document itself is the progress board. |
| **Embedded dependency DAG** | Checklist items can declare dependencies. Daily todos are derived from this DAG in topological order. |
| **Live updates** | After validated work lands, guards write state back to the blueprint. |
| **Layer gates** | A blueprint can define layers so upper layers cannot close while lower layers remain open. |

### 1.2 Difference From A Traditional Spec

| Dimension | Traditional spec | b3ehive blueprint |
|---|---|---|
| Document shape | Static document for humans | Live document for machines and humans |
| Contents | Requirements and acceptance criteria | Requirements, execution checklist, live progress, dependencies |
| Lifecycle | Written at project start, archived at completion | Updated throughout execution |
| Authority | May be scattered across documents and tickets | Exactly one authoritative source |
| Completion state | Stored in a project tracker | Stored inside the blueprint as `[ ] -> [_] -> [x]` |
| Execution driver | Humans translate the spec into tasks | Workers derive tasks directly from the blueprint |
| Validation | Human review | Automated validation gates such as build, test, and lint |
| Change management | Manual process and document review | Guards can split, reset, and refresh derived work |
| Completeness | Human judgment | Guards check duplicate ids, missing dependencies, and cycles |
| Granularity | Often feature-level | Can be path-level through `owned_paths` |

> **Blueprint = Spec + Task Board + State Store + DAG Engine.**
>
> A traditional spec answers "what should be built." A b3ehive blueprint answers
> "what should be built, what state it is in, what is next, and whether it is
> currently allowed to proceed."

---

## 2. Blueprint Shapes

| Shape | Meaning | Use case |
|---|---|---|
| **Prose-first** | Start with narrative requirements, then extract an execution checklist. | Requirements are still being clarified. |
| **Checklist-first** | Put the checklist at the center from the start. | Requirements are already clear enough to execute. |

For a prose-first blueprint, the first cron tick should create or update the
authoritative execution checklist inside that same file and initialize new items
as `[ ]`.

---

## 3. Checklist Structure

A standard checklist item can include a stable id, dependencies, layer, and
owned paths:

```markdown
- [ ] [ITEM-001] Implement user authentication
  - depends_on: []
  - layer: foundation
  - owned_paths: src/auth/

- [ ] [ITEM-002] Implement JWT token signing
  - depends_on: [ITEM-001]
  - layer: foundation
  - owned_paths: src/auth/jwt.ts

- [ ] [ITEM-003] Implement login API
  - depends_on: [ITEM-001, ITEM-002]
  - layer: api
  - owned_paths: src/api/login.ts
```

| Field | Required | Meaning |
|---|---|---|
| `item_id` | Yes | Stable unique id, such as `ITEM-001`. |
| `depends_on` | No | Other item ids this item depends on. |
| `layer` | No | Layer marker for strict layer gates. |
| `owned_paths` | No | Repository-relative files or directories this item may touch. |

Guards use these fields to build the dependency DAG and reject duplicate ids or
cycles.

---

## 4. Rules

### 4.1 Strict Layer Gate

When a blueprint defines layers:

- New work should happen only in the finest still-open layer.
- If lower-layer `[ ]` items remain open, upper-layer items must stay open.
- If a guard finds an upper-layer `[x]` while lower layers are still open, it
  should reset the violating upper-layer item back to `[ ]` and continue from
  the lower layer.

### 4.2 Parent And Child Items

- A parent item can close only when all child checklist items are `[x]`.
- If any child item is still `[ ]` or `[_]`, the parent must stay unfinished.
- If an item is stuck across repeated ticks, a guard may split it into child
  checklist items.

---

## 5. Blueprint And Daily Todo

The blueprint is the authoritative source. The daily todo is a read-only derived
view:

- It includes unfinished blueprint items: `[ ]` and `[_]`.
- It includes current DAG state: `node_id`, dependencies, claim owner, and
  integration state.
- Paths must be repository-relative and must not expose private automation paths
  such as `.cron/automation_repo*`.
- After a successful batch, guards update the blueprint first and then refresh
  the todo.

---

## 6. Blueprint Shapes By Skill

| Skill | Blueprint shape |
|---|---|
| `execution-cron-builder` | One Markdown file with narrative requirements plus an execution checklist. The cron implements items one by one. |
| `learn-cron-builder` | A `learn_checklist.md` derived from a locked source manifest; supports code-to-human understand, code-to-code transform, and human-language translate. |
| `optimization-cron-builder` | `Stage_*_AR_Blueprint.md`, derived from a design philosophy; each item maps to one research document. |
| `compete-cron-builder` | A local `question_type` and competition surface; can support execution choice, coverage union, repair queue, SEO strategy, or blueprint synthesis. |

---

## 7. Lifecycle

```text
Bootstrap:   Initialize checklist items as [ ]
    ↓
Daily Todo:  Derive today's todo from unfinished blueprint items and DAG state
    ↓
Worker:      Claim work in DAG order, produce code/docs, mark self-tested as [_]
    ↓
Validation:  Master integrates [_] output and runs build/test/lint gates
    ↓
Checkpoint:  If validation passes, move [_] to [x] and update the blueprint
    ↓
Cleanup:     When all items are [x], stop the cron and clean up its helpers
```

---

## 8. Summary

Blueprints are a core b3ehive abstraction. They turn a document that humans read
into a program that agents can execute:

- **State is code**: progress is stored in a versioned file.
- **Requirements drive execution**: the blueprint is the task queue.
- **Constraints become rules**: DAG, layer gates, and parent/child closure are
  enforced by guards instead of memory.

Understanding blueprints is the fastest way to understand how b3ehive works.
