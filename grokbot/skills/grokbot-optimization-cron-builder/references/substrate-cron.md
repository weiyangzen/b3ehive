# Cron And tmux Substrate

Read this file when a run uses cron, tmux, or an external agent runner. It holds
the shared runner abstraction and the disk and log guards. Every default here is
a safety cap and stays environment-overridable.

## Choosing A Substrate

- `in-session`: subagents or a workflow tool inside one agent session. Use for
  work that finishes within one session.
- `cron+tmux`: a repository-local guard on a schedule with tmux workers. Use for
  multi-hour or multi-day work.
- `flow`: an external flow runner that drives coding agents. Use when an item
  needs a relay, review, or lanes loop that the runner already implements.

Log the choice as a `DECIDE` line with the expected duration and cost.

## Agent Runner

This is the grokbot build. Generated cron code supports one agent runtime:
`claude --dangerously-skip-permissions`. Every worker, reviewer, verifier,
voter, repair generation, nested run, and in-session subagent uses it.

- `B3EHIVE_AGENT_PLATFORM` is fixed to `claude`. Any other value, `auto`
  included, fails closed with its value.
- `B3EHIVE_AGENT_RUNNER`, when set, must start with
  `claude -p --dangerously-skip-permissions`; otherwise the guard fails closed
  and launches nothing.
- A missing `claude` binary writes state `user_action_required` and launches
  nothing. There is no fallback runtime.
- Each worker generation owns one `claude` process tree, one task root, and one
  workspace. `--add-dir` names that workspace only, never the canonical
  checkout or `$HOME`.
- Nested agents run only when the specification admits them; each child is an
  independent `claude --dangerously-skip-permissions` execution under the same
  global caps.

Command template:

```bash
claude -p --dangerously-skip-permissions \
  --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"
```

Run the command with `$WORKER_REPO` as its working directory, inside the
worker's tmux session when the substrate is `cron+tmux`.

Validate-only output must print `platform=claude`,
`runtime=claude --dangerously-skip-permissions`, and the resolved runner.

## Guard Tick Budget

- Maintain `.cron/*state`, logs, progress, heartbeat, last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; when the Data/root volume has less free space,
    run cleanup and refuse to start new workers;
  - default `DANGER_FREE_GB=15`; below this threshold, write state
    `blocked_disk_space`, run lightweight cleanup, and exit immediately;
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for
    keepalive/scheduler logs; retain only the tail after a file exceeds its cap;
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files
    under the cron root;
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live
    `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories;
  - default `MAX_CRON_ROOT_GB=30`; refuse new worker spawn when the cron root
    remains above this threshold after cleanup;
  - preserve every workspace whose path is referenced by a live selected
    agent-runner process, `tmux`, shell, or lock/pid file;
  - record cleanup decisions in a bounded janitor log, never an unbounded cron log.
- Support parallel `tmux` workers.
- Give each worker a disjoint, section-owned write scope.
- Reconcile worker outputs into the authoritative blueprint.
- Refresh today's todo after each successful merge.
- Classify empty or off-topic outputs as failure.
- Clean up cron when every item is `[x]`.

## Cron Space Guard

Every generated cron must include a repo-local janitor script, such as
`.cron/scripts/cron_space_guard.sh`. The guard calls it from the
top of the guard, before any `tmux` or agent-runner launch.

Minimum behavior:
- Derive the cron root from the script path, independent of the caller's current
  directory.
- Cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, a temp
  file, and atomic `mv`.
- Rotate or truncate scheduler redirection targets such as `keepalive.log`
  before appending output.
- Clean old logs and stale workspaces before checking the cron-root budget.
- Verify live worker paths with self-match-safe process checks before deleting
  any automation repo or workspace.
- Return a distinct nonzero code for "budget exceeded"; exit without marking
  progress.
- Keep every default overrideable through environment variables.

## Cleanup

- Remove only this controller's exact cron line.
- Stop guard and worker `tmux` sessions.
- With cleanup-on-complete enabled, remove repo-local `.cron/` and `.ops/`
  artifacts created only for this run.
- Keep the authoritative blueprint and completed research docs.
