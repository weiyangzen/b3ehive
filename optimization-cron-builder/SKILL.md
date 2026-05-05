---
name: optimization-cron-builder
description: Build or repair a design-idea-guided optimization cron for a repository. Use when the user provides a design philosophy and wants a Stage_*_AR_Blueprint.md with <=100 checklist items, per-item SOTA optimization research docs under Docs/researches/Stage_*_AR/, parallel tmux workers, codex exec batches, and cleanup-on-complete.
---

# Optimization Cron Builder

## Overview

Build a repository-local optimization pipeline that does not implement product code directly. Instead, it continuously scans one stage blueprint through a user-supplied design philosophy, derives a bounded AR checklist, writes per-item optimization research docs, tracks progress, runs parallel `tmux` workers with `codex exec`, and removes its own cron setup when the AR blueprint is complete.

`AR` means `Architecture Refinement` here, but the pattern works for any stage-specific optimization blueprint.

## Workflow

1. Inspect the target repository and find the single authoritative blueprint source for the stage.
2. Capture the user-supplied design philosophy in one short stable sentence.
3. Generate one authoritative `Docs/Stage_*_AR_Blueprint.md` with:
   - a bounded checklist count
   - exactly one item per optimization topic
   - no more than 100 items
   - grouped sections that can be owned by parallel workers
4. Define the completion gate for every `[ ]` item:
   the item may be checked only when a corresponding doc exists under `Docs/researches/Stage_*_AR/` and that doc is:
   - fully about that item
   - aligned to the design philosophy
   - based on stable SOTA or mature frontier practice
   - translated into concrete recommendations for the repository
5. Add private `.ops/` and `.cron/` helpers locally and hide them from git where appropriate.
6. Create the required pieces:
   - AR blueprint tools
   - daily todo generator
   - optimization guard
   - worker runner
   - install script
   - cleanup script
7. Run the guard once in `VALIDATE_ONLY=1`.
8. Install cron only after validate-only succeeds.
9. Start parallel `tmux` workers with disjoint section ownership.
10. Reconcile section snapshots back into the authoritative AR blueprint and refresh today's todo after each worker batch.
11. When all AR items are complete, remove cron entries, stop tmux sessions, and clean repo-local cron helpers if cleanup is requested.

## Required Components

### AR Blueprint

Requirements:
- Use exactly one authoritative AR blueprint file.
- Keep total checklist items `<= 100`.
- Choose a research grain that is specific enough for one item to map to one optimization doc.
- Put stable repository-relative output paths into checklist items whenever useful.
- Group checklist items into worker-ownable sections.

### Per-Item Research Output

Requirements:
- Output root: `Docs/researches/Stage_*_AR/`
- One doc per checklist item.
- Every doc must stay inside its own topic boundary.
- Every doc must explicitly filter recommendations through the user design philosophy.
- Prefer stable SOTA over novelty theater.
- Prefer decisions that reduce complexity, cognitive load, and future rework.

### Optimization Guard

Requirements:
- Maintain `.cron/*state`, logs, progress, heartbeat, last-message files.
- Support parallel `tmux` workers.
- Assign workers by section ownership, not overlapping write scopes.
- Reconcile worker section snapshots back into the main AR blueprint.
- Refresh today's todo after each successful merge.
- Treat empty or off-topic docs as failure, not progress.
- Clean up cron when all AR items are checked.

### Cleanup

Requirements:
- Remove only this repo's optimization cron line.
- Stop guard and worker `tmux` sessions.
- Remove repo-local `.cron/` and `.ops/` artifacts created only for the optimization run when cleanup-on-complete is enabled.
- Keep the authoritative blueprint and completed research docs.

## Batch Rules

- Prefer exactly 5 workers when the blueprint can be partitioned cleanly into 5 sections.
- Each worker owns one section only.
- Workers may update only:
  - their owned section in the clone-local AR blueprint
  - their owned output directory under `Docs/researches/Stage_*_AR/`
- The main repo authoritative blueprint is updated only by the guard merge step.
- Keep prompts explicit about design philosophy, completion rules, and owned output scope.

## Validation

Always do these checks before declaring the optimization cron ready:
- `bash -n` on all created shell scripts
- one authoritative AR blueprint generation pass
- one daily todo generation pass
- one `VALIDATE_ONLY=1` guard run
- `crontab -l` verification after install
- `tmux ls` verification after worker launch
- non-empty output verification for completed items

## Repair Rules

When the AR blueprint is wrong:
- stop workers first
- regenerate the blueprint from the same design philosophy and source scope
- preserve existing `[x]` marks only when the corresponding research docs still exist and remain non-empty
- regenerate today's todo before resuming

When workers produce docs that are broad but not item-pure:
- do not mark the item complete
- split the checklist item or narrow the doc title and scope
- rerun only the affected section

## Local References

Read these only when needed:
- `references/optimization-pattern.md`
- `references/repair-playbook.md`
