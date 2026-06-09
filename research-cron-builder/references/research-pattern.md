# Research Cron Pattern

## Pattern scope

This reference is intentionally project-neutral. Keep examples generic and never
name private repositories, local absolute paths, customer workspaces, or
operator-specific evidence directories in committed skill docs.

## Best-practice pattern

1. Generate a repository-derived checklist.
2. Generate a daily todo from that checklist.
3. Start a guard that:
   - creates parallel `tmux` workers
   - claims DIR/FILE work under lock files
   - runs the cron space guard before worker spawn
   - calls the selected Codex, Claude Code, opencode, OpenClaw, or Hermes agent runner
   - verifies output documents are non-empty
   - reconciles checklist marks from output docs
   - checkpoints progress locally
4. Remove cron on completion.

## Checklist Protocol

Research progress uses exactly three checkbox states, and the mark itself is the
cursor state:

- `[ ]` means not researched. The item is available for a researcher worker
  claim.
- `[_]` means worker-produced. The required source-tree-aligned research
  artifact exists and is waiting for master curator acceptance. Worker self-test
  files, JSON manifests, or separate evidence files are not required.
- `[x]` means master accepted. The master curator verified one-to-one coverage,
  source-path alignment, index rows, substantive content, and required gates.

The researcher/guard lane may move `[ ] -> [_]` by detecting the required
non-empty research documents. The master lane is the only actor that may move
`[_] -> [x]`. Cleanup, folder synthesis, and release gates require zero `[ ]`
and zero `[_]` items. Daily todos must show separate counts for all three states
and compute `unfinished = count([ ]) + count([_])`.

Operational queue states such as `live`, `finished`, `curating`, `ok`, or
`failed` may add detail in ledgers, but they do not replace the checkbox state.
Researcher queues are built from `[ ]` items; curator queues are built from
`[_]` items. Finished `[_]` outputs must not consume live worker capacity.

## Code-only scope rule

Use code-only scope by default for repositories with heavy docs or generated content. Include:
- source files
- config files
- scripts
- tests

Exclude by default:
- docs and markdown
- `Docs/researches/`
- caches
- build output
- dependency trees

## Typical runtime files

- `.cron/research_guard.state`
- `.cron/research_guard.log`
- `.cron/research_guard.block_count`
- `.cron/research_claims/*.claim`
- `.cron/research_guard.provider_key_index` when provider key pools are used
- `.cron/research_guard.progress`
- `.cron/scripts/cron_space_guard.sh`

## Space and log budget

Every research guard tick must run a bounded cleanup helper before launching or respawning workers.

- Use environment-overridable defaults: `MIN_FREE_GB=30`, `DANGER_FREE_GB=15`, `MAX_LOG_MB=20`, `MAX_KEEPALIVE_MB=5`, `LOG_RETENTION_DAYS=3`, `WORKSPACE_TTL_HOURS=48`, `MAX_CRON_ROOT_GB=30`.
- Trim active logs by keeping the tail with `tail -c` and atomic `mv`; avoid unbounded guard or keepalive logs.
- Delete `.log`, `.out`, and `.err` files older than 3 days under the cron root.
- Remove only stale workspaces whose paths are not referenced by the selected
  live agent runner, `tmux`, shell, pid, or lock state.
- If free space or cron-root budget remains unsafe after cleanup, write `blocked_disk_space` and skip worker spawn.

## Typical cron shape

- daily todo generation: once per day shortly after midnight
- guard wake-up: every 5 minutes

## Common failure modes

- provider quota/auth failures causing `exec_failed`
- duplicate work due to missing claim locks
- empty output docs accepted as success
- checklist corruption from non-atomic writes
- completed repos left running because cleanup never fires
- unbounded guard logs, worker logs, or stale workspaces consuming local disk
- workers marking `[x]` directly instead of stopping at `[_]`
- requiring worker self-test JSON before recognizing existing research docs
- treating `[_]` as accepted research for folder synthesis, cleanup, or
  release gates
- losing `[_]` state when regenerating checklist or daily todo files
