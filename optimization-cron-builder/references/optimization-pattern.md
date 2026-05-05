# Optimization Cron Pattern

## Core idea

This pattern continuously improves a repository's design quality against a declared philosophy, rather than implementing product code directly.

Example philosophies:

- extremely lightweight, elegant, novice-friendly
- enterprise-safe, auditable, boring-by-default
- maximal extensibility with minimal coupling

## Best-practice shape

1. Read one authoritative stage blueprint.
2. Derive one bounded AR blueprint with `<=100` items.
3. Partition the AR blueprint into section-owned worker lanes.
4. Run parallel `tmux` workers with `codex exec`.
5. Require one focused research doc per checklist item.
6. Merge section snapshots back into the main blueprint.
7. Remove cron when all items are complete.

## Completion rule

An AR item is complete only when:

- the corresponding research doc exists
- it is non-empty
- it is scoped only to that item
- it reflects stable SOTA or mature frontier practice
- it explicitly translates recommendations back into the current repository

## Typical runtime files

- `.cron/*guard.state`
- `.cron/*guard.log`
- `.cron/*guard.heartbeat`
- `.cron/*slot*.state`
- `.cron/*slot*.prompt.txt`
- `.cron/*slot*.last_message.txt`

## Common failure modes

- item grain too coarse, producing vague docs
- workers overlapping the same section
- docs marked complete even though they ignore the design philosophy
- cron artifacts left behind after completion
