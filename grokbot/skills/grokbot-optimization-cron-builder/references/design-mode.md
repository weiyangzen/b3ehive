# Design Mode

On-demand detail for design-mode optimization. Moved from v1 `SKILL.md`,
`optimization-pattern.md`, and `repair-playbook.md`.

## Core Idea

This pattern continuously improves a repository's design quality against a declared philosophy, rather than implementing product code directly.

Example philosophies:

- extremely lightweight, elegant, novice-friendly
- enterprise-safe, auditable, boring-by-default
- maximal extensibility with minimal coupling

## AR Blueprint

- Use exactly one authoritative AR blueprint file.
- Keep total checklist items `<= 100`.
- Set the research grain so one item maps to one optimization doc.
- Put stable repository-relative output paths in checklist items when useful.
- Group checklist items into worker-ownable sections.

## Per-Item Research Output

- Output root: `Docs/researches/Stage_*_AR/`
- One doc per checklist item.
- Keep every doc inside its topic boundary.
- Filter every recommendation through the user design philosophy.
- Prioritize stable SOTA or mature frontier practice over unvalidated novelty.
- Favor decisions that reduce complexity, cognitive load, and future rework.

## Completion Rule

An AR item is complete only when:

- the corresponding research doc exists
- it is non-empty
- it is scoped only to that item
- it reflects stable SOTA or mature frontier practice
- it explicitly translates recommendations back into the current repository

## Batch Rules

- Decide the worker count from the sections. v1 preferred 5 workers when the
  blueprint partitioned cleanly into 5 sections.
- Each worker owns one section only.
- Workers may update only:
  - their owned section in the clone-local AR blueprint
  - their owned output directory under `Docs/researches/Stage_*_AR/`
- Only the guard merge step updates the main repo's authoritative blueprint.
- State the design philosophy, completion rules, and owned output scope in every
  worker prompt.

## Repair Rules

For an incorrect AR blueprint:

1. Stop workers.
2. Regenerate the blueprint from the same design philosophy and source scope.
3. Preserve existing `[x]` marks only when the corresponding research docs
   still exist and remain non-empty.
4. Regenerate today's todo before resuming.

For a broad, non-item-pure worker doc:

1. Keep the item incomplete.
2. Split the checklist item or narrow the doc title and scope.
3. Rerun only the affected section.

## When A Section Stalls

Check:
- whether the section has too many heterogeneous items
- whether the prompt allows the worker to write outside its owned scope
- whether output docs are too broad and therefore blocked from completion

If needed:
- split the section
- reduce per-run item count
- rerun only the affected worker lane

## Common Failure Modes

- item grain too coarse, producing vague docs
- workers overlapping the same section
- docs marked complete even though they ignore the design philosophy
- cron artifacts left behind after completion
- unbounded worker logs or stale workspaces consuming local disk
