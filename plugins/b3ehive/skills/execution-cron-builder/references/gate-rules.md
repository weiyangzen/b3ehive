# Generated Gate Rules

These are controller invariants. Repository acceptance commands and artifact
policies come from the frozen target specification.

## Portability Gate

- No project name, absolute path, item prefix, model route, service tier,
  concurrency number, validator, or evidence directory from another repository.
- No fixed language, framework, build system, remote, or branch assumption.
- No global ban on tests, docs, binaries, or generated files; follow the target
  repository's explicit policy.
- Exercise at least two unlike fixture repositories and scan for cross-fixture
  residue.

## Codex Transport Gate

- One claim equals one task-local tmux server/socket/session, one interactive
  Codex process tree, one writable CODEX_HOME, one thread, and one active goal.
- `codex app-server`, controller-managed app-server JSON-RPC, shared daemons,
  `codex exec`, shared tmux, shared writable Codex state, and no-tmux Codex are
  hard failures with no fallback.
- Minimal CODEX_HOME bootstrap excludes project trust history, plugins,
  marketplaces, MCP configuration, and prior state registries.
- Paste one short `/goal` with a claim-specific final token; require that token
  in joined composer text before the one allowed submit key.
- Only exact tmux/PID/start-time/cwd/route/thread/goal identity is live.
- Delayed registry writes may preserve `goal_submitted` only while exact process
  identity remains healthy and before a configured hard deadline.
- Validate-only prints the resolved transport and route policy but launches
  nothing.

## Task Boundary Gate

- Task files are explicitly declared, repository-relative, and inode-independent.
- Complete repository copies, hardlink trees, unrelated paths, runtime roots,
  credentials, sockets, logs, caches, and controller state are rejected.
- Claim card hash and baseline hash match before launch and harvest.
- Changed paths stay within exact ownership.
- Worker never writes the authoritative blueprint or canonical checkout.

## Checklist Gate

- Parser accepts only `[ ]`, `[_]`, and `[x]`.
- IDs are unique; dependencies exist and are acyclic.
- `[ ] -> [_]` requires durable harvested self-test handoff.
- `[_] -> [x]` requires Master integration, repository validation, and required
  completion-surface reconciliation.
- `[ ]` and `[_]` both block completion cleanup.
- Worker output never directly closes authoritative state.

## Handoff Gate

- Harvest checksum-valid result and patch before stale liveness pruning.
- Preserve immutable handoff independently of task process lifetime.
- Finished claims release live capacity and their TUI immediately.
- Repair reuses the same task/thread/goal unless the claim is explicitly retired.
- Retry budgets are keyed by stable claim/baseline/failure identity.

## Admission Gate

- Logical claims, starting lanes, authenticated goals, running turns,
  integrations, and validators have separate limits.
- Admission checks host and external headroom plus path conflicts.
- The requested cap is never exceeded; reservations are never reported as live.
- Launch fanout is a per-wave limit, not a hidden overall concurrency cap.
- Given `N` eligible claims, all limits admitting `N`, and fixture workers that
  remain active, one admission pump reaches exactly `N` authenticated lanes
  without waiting for another cron tick.
- Binding underfill reasons are visible and persisted.

## Lock Gate

- Global scheduler lock protects only short state transitions.
- Lock file descriptors are closed before tmux/process launch.
- Slow model, network, build, test, benchmark, and integration work runs outside
  the global lock.
- Interrupted phases are recoverable from durable attempt state.

## Master Gate

- Canonical dirty work is preserved; no implicit reset/stash/checkout/revert.
- Master validates the integrated canonical tree with repository-defined gates.
- Conflicts preserve user and worker intent or move the entry to explicit repair.
- Commit and push happen only when required by repository/operator policy.
- No foreign docs/code ratio, batch size, diff size, or domain evidence rule is
  imposed.

## Cleanup Gate

- Explicit stop removes the exact cron marker and all controller-owned workers,
  including task-descended subprocesses, while preserving canonical work.
- Completion cleanup additionally requires no `[ ]`, `[_]`, handoff,
  integration, repair, or pending-checkpoint work.
- Cleanup is idempotent and verifies cron entries, scheduler processes, task
  processes, tmux sockets, locks, and runtime roots are absent.
- Process matching is task-identity scoped and never kills unrelated host Codex
  sessions or services.
