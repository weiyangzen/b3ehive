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
4. Run parallel `tmux` workers with the selected Codex, Claude Code, Cursor, Grok Build, opencode, OpenClaw, or Hermes agent runner.
5. Require one focused research doc per checklist item.
6. Merge section snapshots back into the main blueprint.
7. Run a cron space guard before worker spawn.
8. Remove cron when all items are complete.

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
- `.cron/scripts/cron_space_guard.sh`

## Space and log budget

Every optimization guard tick must run a bounded cleanup helper before launching or respawning workers.

- Use environment-overridable defaults: `MIN_FREE_GB=30`, `DANGER_FREE_GB=15`, `MAX_LOG_MB=20`, `MAX_KEEPALIVE_MB=5`, `LOG_RETENTION_DAYS=3`, `WORKSPACE_TTL_HOURS=48`, `MAX_CRON_ROOT_GB=30`.
- Trim active logs by keeping the tail with `tail -c` and atomic `mv`; avoid unbounded guard or keepalive logs.
- Delete `.log`, `.out`, and `.err` files older than 3 days under the cron root.
- Remove only stale workspaces whose paths are not referenced by the selected
  live agent runner, `tmux`, shell, pid, or lock state.
- If cleanup cannot bring free space and cron-root size back under budget, write `blocked_disk_space` and skip worker spawn.

## Common failure modes

- item grain too coarse, producing vague docs
- workers overlapping the same section
- docs marked complete even though they ignore the design philosophy
- cron artifacts left behind after completion
- unbounded worker logs or stale workspaces consuming local disk

## Looper Embedding

When looper invokes optimization for strategy or blueprint bridge refinement:

- require an active parent `ResourceLease`
- write a `ParentLeaseRef`
- record the run in the looper `NestedRunLedger`
- attach output to a `BridgeSurface` with `bridge_level=strategy` or
  `bridge_level=blueprint`
- keep outputs provisional until master acceptance
- never write `[x]` from the nested optimization run
- roll token, wall-clock, human-review, disk, and output costs into parent
  no-reward accounting
