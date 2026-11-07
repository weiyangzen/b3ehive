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

- One admitted worker generation equals one task-local tmux
  server/socket/session, one interactive Codex process tree, one writable
  CODEX_HOME, one thread, and one submitted goal. Persistent logical/service
  records own such transports only through an explicit one-to-one worker mapping
  in the frozen repository specification.
- `codex app-server`, controller-managed app-server JSON-RPC, shared daemons,
  `codex exec`, shared tmux, shared writable Codex state, and no-tmux Codex are
  hard failures with no fallback.
- Minimal CODEX_HOME bootstrap excludes project trust history, plugins,
  marketplaces, MCP configuration, and prior state registries.
- Paste one short `/goal` with a claim-specific final token; require that token
  in joined composer text before the one allowed submit key.
- Acquire atomic turn and outbound-request leases before the submit key; one
  execution may have at most one outstanding request.
- Only exact tmux/PID/start-time/cwd/route/thread/goal identity is live.
- Delayed registry writes may preserve `goal_submitted` only while exact process
  identity remains healthy and before a configured hard deadline.
- Validate-only prints the resolved transport and route policy but launches
  nothing.
- Bounded terminal result stops the exact transport. A persistent worker keeps
  the same active goal across maintenance cycles until explicit stop or proved
  failure; every continuation remains attributed and capped. A replacement uses
  a fresh generation only after the old generation is retired.
- A wait between persistent maintenance cycles is not liveness failure. Verify
  the resident goal and transport independently of running turns; do not issue
  model requests merely to make an idle worker appear busy.
- Nested agents are forbidden unless repository policy explicitly enables them.
  An enabled child has its own identity and independently consumes execution,
  transport, turn, request-rate, in-flight, and outstanding-request capacity.

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

## Gantt Projection Gate

- Blueprint `<dir>/<name>_Blueprint.<ext>` maps exactly to
  `<dir>/<name>_Gantt.<ext>`; only the terminal token changes and the complete
  prefix is preserved. Other stems append `_Gantt` and freeze the result.
- The companion is a generated read-only Kanban projection with no mutable
  checkboxes and is never parsed as authoritative state.
- A renderable Gantt view and monitoring index cover every checklist ID exactly
  once and expose dependency, owner, and durable runtime state.
- Source/specification digests and generation time prove freshness; each tick
  atomically replaces the projection after its final state merge.
- Recorded timestamps or explicitly configured estimates are used; items with
  unknown timing remain visibly unscheduled and receive no fabricated dates.
- Missing, misnamed, stale, duplicate-ID, incomplete, or pre-tick projections
  fail validation and completion cleanup.

## Handoff Gate

- Harvest checksum-valid result and patch before stale liveness pruning.
- Preserve immutable handoff independently of task process lifetime.
- Finished bounded claims release live capacity immediately. Persistent claims
  release it only on explicit stop, retirement, or proved liveness failure.
- Repair is a separately admitted bounded execution linked to the same logical
  item and immutable handoff. A repository-authorized thread resume still
  requires a new request lease and terminalizes after its bounded result.
- Retry budgets are keyed by stable claim/baseline/failure identity.

## Admission Gate

- Logical/service records, agent executions, starting lanes, live transports,
  authenticated goals, running turns, request starts, in-flight requests,
  integrations, and validators have separate limits.
- Admission checks host and external headroom plus path conflicts.
- The requested cap is never exceeded; reservations are never reported as live.
- Launch fanout is a per-wave limit, not a hidden overall concurrency cap.
- Given `N` eligible worker claims, all limits admitting `N`, and
  fixture workers that remain active, one admission pump reaches exactly `N`
  authenticated lanes. A persistent pool returns to exactly `N` after proved
  worker death and never exposes `N+1`.
- Request rate and in-flight gates independently prevent request `R+1`; cron,
  watchdog, resume, and provider continuation cannot bypass them.
- Request storms and unauthorized continuations open an audited fail-closed
  breaker that ordinary scheduling cannot reset.
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

- A persistent pool is not complete merely because a cycle returned a result,
  its repair queue is empty, or implementation checkboxes are accepted. Only
  the frozen service stop condition or an explicit operator stop authorizes
  whole-pool cleanup; proved failed generations may still be replaced.
- Explicit stop removes the exact cron marker and all controller-owned workers,
  including task-descended subprocesses, while preserving canonical work.
- Completion cleanup additionally requires no `[ ]`, `[_]`, handoff,
  integration, repair, or pending-checkpoint work.
- Cleanup is idempotent and verifies cron entries, scheduler processes, task
  processes, tmux sockets, locks, and runtime roots are absent.
- Process matching is task-identity scoped and never kills unrelated host Codex
  sessions or services.

## Generated Validation (v1 text)

Every generated or repaired controller must include tests proving:

- persistent cycle results, empty queues, and waits retain the same active goal
  and transport without manufacturing running turns or new model requests
- persistent service cleanup requires its explicit stop condition; accepted
  implementation checkboxes alone never stop the maintenance pool

- validate-only creates no claim, tmux server, or worker process
- Codex argv is interactive and cannot resolve to app-server or `codex exec`
- each simultaneous claim has a distinct task root, tmux socket/session,
  process identity, writable `CODEX_HOME`, thread, and goal
- exactly one complete `/goal` is submitted per claim
- bounded logical/service records create no standing TUI; persistent records
  create exactly the one-to-one worker generations required by the specification
- nested agents are rejected unless explicitly specified; when enabled, every
  child independently consumes all applicable execution/turn/request caps
- submission is impossible without atomic turn and request leases
- each execution has at most one outstanding request
- bounded terminal result stops the exact transport; a persistent result keeps
  the same exact generation live until stop or failure
- bounded post-terminal continuation is rejected, while authorized persistent
  continuation remains attributed and inside request/in-flight caps
- cron/watchdog never resumes non-admitted goals; persistent reconciliation
  replaces only proved dead generations and never creates worker `N+1`
- only fully authenticated claims count as live
- delayed `goal_submitted` authentication promotes without duplicate launch
- dead/mismatched startup is released after its bounded deadline
- harvest occurs before prune and finished TUI servers are stopped
- scheduler locks are not inherited by workers
- caps and host admission prevent `N+1`
- with `N` eligible worker claims, all limits admitting `N`, and
  mock TUIs that remain live, one admission pump reaches exactly `N`
  authenticated lanes; a persistent pool later restores exactly `N` after a
  proved worker death without ever exposing `N+1`
- request-rate and in-flight caps independently prevent request `R+1` even when
  transport and logical caps have room
- request-start storms, connection/in-flight excess, host pressure, and repeated
  unauthorized continuations trip a fail-closed circuit breaker whose reset is
  explicit and audited
- every intentional underfill has a specific persisted dependency, conflict,
  startup, host-resource, external-limit, route, or validator reason
- exact terminal `Blueprint` -> `Gantt` naming preserves the complete prefix
- the Gantt monitoring index covers every checklist ID exactly once, reflects
  state transitions, rejects stale source/specification digests, and never
  invents timing for unscheduled items
- Gantt replacement is atomic and a completed tick cannot leave it stale
- cleanup removes only controller-owned runtime and processes
- two fixture repositories with different names, blueprint paths, languages,
  validators, and route policies produce no cross-project constants

Static validation scans executable launch/config surfaces for forbidden Codex
subcommands and scans generated artifacts for unexplained absolute paths or
known foreign project tokens. Negative prose documenting forbidden transports
is allowed; executable command-shaped occurrences are not.

## Generated Validation (v2.2 additions)

- the rule table returns a decision without writing state or spending budget
- a crash between intent and effect replays the effect only when readback proves
  it absent; an undecidable readback blocks the claim
- each failure kind follows its retry row; budget exhaustion never retries
- a moved source revision blocks admission of new claims
- a receipt fingerprint changes when an untracked file changes
- an item without successor, `wait` with `resume_when`, or `no_followup` is
  reopened by the master
