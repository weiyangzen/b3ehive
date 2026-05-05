---
name: research-cron-builder
description: Build or repair a code-research cron for a repository using a generated research checklist, daily todo snapshots, parallel workers, key rotation, checkpoints, and cleanup-on-complete. Use when a repo needs long-running codebase research, progress tracking, cron/tmux worker orchestration, repair of broken research progress tables, or migration of the existing research-cron pattern to a new repository.
---

# Research Cron Builder

## Overview

Build a code-only research pipeline that continuously reads source files, writes per-file or per-directory research docs into `Docs/researches/`, tracks progress in a generated checklist, rotates `kimi` keys, checkpoints progress, and removes its own cron entries when research is complete.

## Workflow

1. Inspect the target repository state before changing anything.
2. Decide the research scope.
   Default: code-only scope. Exclude docs, `Docs/researches/`, dependency caches, runtime directories, and generated artifacts unless the user explicitly wants doc research too.
3. Add private `.ops/` and `.cron/` helpers locally and hide them from git with `.git/info/exclude` or repo-local ignore strategy.
4. Create the four required scripts:
   - `generate_research_blueprint_checklist.sh`
   - `generate_daily_research_todo.sh`
   - `research_guard.sh`
   - `cleanup_research_cron.sh`
5. Generate the checklist once, then verify it contains real pending items.
6. Run the guard manually once before installing cron.
7. Install cron only after the manual run proves the pipeline can claim work and write logs.
8. If progress tables are broken, regenerate the checklist from repository state and reconcile `[x]` marks from existing research documents.
9. On completion, remove cron entries and set the state file to `completed`.

## Required Components

### Checklist Generator

Create `Docs/researches/blueprint_checklist.md` from the repository tree.

Requirements:
- Preserve existing `[x]` marks when regenerating.
- Write atomically via a temp file then `mv`.
- Exclude `.git/`, `.cron/`, `Docs/researches/`, caches, build outputs, and dependency directories.
- Prefer code-only filtering unless the user explicitly wants doc research.
- Represent work as `- [ ] [DIR] path` and `- [ ] [FILE] path`.

### Daily Todo Generator

Create `Docs/researches/todos_YYYYMMDD.md` from the checklist.

Requirements:
- Show snapshot counts: done, pending, pending dirs, pending files.
- List only unchecked items.
- If pending is zero, render a single completed line instead of an empty section.
- Regenerate idempotently.

### Research Guard

The guard owns runtime behavior.

Requirements:
- Maintain `.cron/research_guard.state`, `.cron/research_guard.log`, `.cron/research_guard.block_count`.
- Support `tmux` worker fan-out for parallel research.
- Claim work under a lock so workers do not duplicate batches.
- Rotate `kimi` keys on auth/quota/rate-limit failures.
- Distinguish between `completed`, `idle_waiting`, `exec_failed`, `exec_timeout`, and `running_exec`.
- Reconcile checklist marks from existing non-empty research docs.
- Commit checkpoint progress with `docs(research): ...` messages when appropriate.
- Emit milestone notifications if the repository uses progress alerts.
- Run cleanup when pending items reach zero and cleanup is enabled.

### Cleanup Script

Remove only the target repo's research cron lines.

Requirements:
- Match both the daily todo line and the research guard line.
- Be safe when run multiple times.
- Record a cleanup state/log file under `.cron/`.

## Repair Rules

When a research repo is already in motion and the progress table is wrong:
- Stop workers first.
- Regenerate the checklist from repository state.
- Reconcile `[x]` marks from existing `*_research.md` and `current_folder_research.md` files.
- Regenerate today's todo.
- Resume workers only after counts look sane.

When the checklist file becomes `0 bytes`:
- Fix the generator to use atomic writes.
- Rebuild the checklist immediately.
- Copy the repaired checklist to any alternate progress-table alias the repo expects.

## Validation

Always perform these checks before declaring the cron ready:
- `bash -n` on all `.ops/*.sh`
- manual checklist generation
- manual todo generation
- one manual `research_guard.sh` run
- `crontab -l` verification after install
- log/state verification under `.cron/`

## Best Practices

### Key Pool vs Concurrency

When scaling research concurrency, treat key-pool size as a first-class capacity limit.

Required practice:
- Before increasing `MAX_PARALLEL_RESEARCH`, proactively gather keys from all approved sources and deduplicate them.
- Recommended key sources: `KIMI_KEYS_FILE`, `KIMI_KEYS_EXTRA_FILES`, `KIMI_API_KEYS`, `KIMI_API_KEY`.
- Target `unique_key_count >= MAX_PARALLEL_RESEARCH` whenever possible.
- If keys are fewer than workers, keep worker-slot key sharding enabled and log an explicit warning with both counts.
- If sustained auth/quota/rate-limit failures appear, first expand key pool, then re-balance worker-to-key spread; do not only increase retries.

Implementation guidance:
- Use deterministic worker-slot offsets so workers start from different key indices.
- Persist per-worker key index state to avoid synchronized retries on the same key.
- Keep global fallback rotation for non-worker runs and crash recovery.
- Include `worker_slot` and `key_index` in failure logs so skew is visible during incident review.

## Local References

Read these only when needed:
- `references/research-pattern.md` for the full pattern and repository examples
- `references/repair-playbook.md` for progress-table repair and cleanup rules
