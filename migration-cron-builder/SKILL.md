---
name: migration-cron-builder
description: Build or repair a migration cron for a repository that converts Claude Code agents, skills, hooks, rules, docs, templates, and settings into Codex-ready one-to-one artifacts under Docs/migrated using an authoritative checklist, daily todos, isolated worker clones, validation gates, 5-way gpt-5.4 xhigh execution, and cleanup-on-complete. Use when a Claude-first repo should be migrated into Codex-compatible assets continuously or when such a migration cron needs repair.
---

# Migration Cron Builder

## Overview

Build a repository-local migration pipeline that scans Claude-first assets, writes an authoritative migration checklist, runs bounded Codex workers in isolated clones, validates one migrated artifact at a time, syncs validated outputs into `Docs/migrated/`, tracks progress, and removes its own cron entries on completion.

## Workflow

1. Inspect the repository and freeze the migration scope.
2. Restrict scope to Claude-native assets unless the user expands it.
   Default scope: `.claude/agents/**`, `.claude/skills/**`, `.claude/hooks/**`, `.claude/rules/**`, `.claude/settings.json`, `.claude/docs/**`, and Claude-only project template directories.
3. Add private runtime state under `.cron/` and repo-local helpers under `.ops/`.
4. Create the required pieces:
   - migration checklist generator
   - daily todo generator
   - migration execution/status helper
   - migration guard
   - cron installer
   - cron cleanup script
5. Make `Docs/migrated/` the only migration output root.
6. Keep migration one-to-one.
   Every source artifact must map to exactly one migrated Codex artifact.
7. Use isolated worker clones for parallel execution.
8. Validate every migrated artifact by type before copying it back into the authoritative repo.
9. Defer repeat validation failures within each shard so fresh items keep flowing.
10. Run the guard manually before installing cron.
11. Install cron only after checklist generation, todo generation, status reporting, and one manual worker pass all succeed.
12. Remove only this migration cron when all checklist items are complete.

## Output Contract

Use these default mappings unless the repository needs a different target layout:
- agents: `.claude/agents/*.md` -> `Docs/migrated/agents/*.md`
- skills: `.claude/skills/*/SKILL.md` -> `Docs/migrated/skills/*/SKILL.md`
- hooks: `.claude/hooks/*.sh` -> `Docs/migrated/tools/hooks/*.sh`
- rules: `.claude/rules/*.md` -> `Docs/migrated/tools/rules/*.md`
- settings: `.claude/settings.json` -> `Docs/migrated/tools/settings.json`
- docs: `.claude/docs/**` -> `Docs/migrated/docs/**` unless the source is a Claude-only template
- Claude doc templates: `.claude/docs/templates/**` and `.claude/docs/*template*` -> `Docs/migrated/project-templates/claude-docs/**`
- repo template structure: Claude-only project template directories (for example `CCGS Skill Testing Framework/templates/**`) -> `Docs/migrated/project-templates/<slug>/**`

## Validation Rules

Type-specific validation should be strict enough to block junk outputs:
- agent markdown: frontmatter + explicit Codex traceability + required workflow sections
- skill markdown: Codex skill frontmatter + required sections
- hook shell: shebang + `set -euo pipefail` + `bash -n`
- rule markdown: preserved scope metadata when relevant + Codex adaptation section
- doc markdown: explicit Codex traceability + purpose/usage/migration sections
- template artifacts: explicit Codex traceability + preserved reusable structure
- settings JSON: valid JSON with Codex runtime fields

## Runtime Rules

- Default concurrency: `5`
- Default model: `gpt-5.4`
- Default reasoning effort: `xhigh`
- Scheduler should only spawn one worker per slot when its pid is not alive.
- Workers must write only one output artifact per run.
- Workers must not edit source Claude files.
- Scheduler progress should be queryable via a machine-readable status command.

## Cleanup Gate

Only clean up when:
- authoritative migration checklist has zero unchecked items
- current todo shows zero unfinished items
- no worker pid file points to a live process
- cleanup script successfully removes the migration cron entries
