# Execution Controller Pattern

Use this reference to turn the skill contracts into repository-local code. All
names and paths below are placeholders.

## 1. Frozen Specification

Persist one versioned specification before installation. It should name the
authoritative blueprint, its exact same-prefix Gantt companion, parser,
dependency source, runtime root, platform, route policy, task policy, result
schema, validators, completion surfaces, caps, budgets, and cron marker. Hash
the specification into claims and state so a policy migration cannot silently
reinterpret old work.

Validate portability by generating against at least two fixture repositories
whose names, languages, blueprint locations, item IDs, validators, and route
settings differ. Neither generated tree may contain constants from the other.

## 2. Durable State

Keep atomic, lock-protected ledgers for:

- claims and launch attempts
- immutable harvested handoffs
- integration/repair queue
- released claims and retired process identities
- route/admission decisions
- outbound request leases, provider request/response identities, and breaker
  transitions
- scheduler cursor and cleanup record

Every identity includes a schema version, claim ID, run ID, task root, status,
timestamps, and specification digest. Codex identities also include tmux socket,
session, pane PID/start time, private CODEX_HOME, thread ID, and goal ID. Request
identity additionally binds execution ID, lease token/epoch, submission receipt,
provider request/response ID when observable, and terminal disposition.

## 3. Tick Phases

Use short transactions:

1. lock and validate specification
2. harvest results and stop finished transports
3. reconcile claims and recover promotable startups
4. validate checklist and DAG
5. reserve bounded integration and launch work
6. persist state and release the global lock
7. perform slow integration/preparation/launch work
8. lock briefly to merge outcomes and atomically write status and Gantt

No long TUI wait, model turn, network call, build, test, or benchmark runs under
the global scheduler lease.

## 4. Codex Startup

For one claim:

1. Create the task root, independent work files, immutable claim card, and
   minimal private CODEX_HOME.
2. Start one tmux server with one interactive Codex TUI process tree.
3. Record pane PID and `/proc` start time before sending input.
4. Handle active first-run/trust screens once.
5. Detect the real idle composer.
6. Paste one short `/goal` ending in a claim-specific completion token; poll
   joined composer text until that final token is visible, or fail without
   submitting partial input.
7. Acquire atomic turn and request leases, submit once, and persist
   `goal_submitted` plus the submission receipt.
8. Read the private thread/goal registries and verify route, cwd, objective, and
   active status before persisting authenticated transport state.
9. Harvest a bounded terminal result, terminalize the goal, and stop the exact
   tmux server. A subsequent provider-created turn without another controller
   request lease is an unauthorized continuation and trips the breaker.

If registration is delayed but tmux/PID identity remains exact, preserve the
starting lane until its hard deadline. A later tick promotes it. If identity is
lost, route is wrong, the objective mismatches, or the deadline expires, retire
that task safely and record the failure. Never switch transports.

## 5. Admission

Compute separate availability values:

```text
logical_available = claim_cap - active_claims
startup_available = starting_cap - starting_claims
transport_available = live_transport_cap - live_transports
running_available = running_turn_cap - proved_running_turns
rate_available = request_start_cap - request_starts_in_window
inflight_available = inflight_request_cap - inflight_requests
execution_available = execution_cap - admitted_executions
```

Then reduce admission by host headroom, conflict leases, dependency readiness,
external limits, and validator capacity. Values and formulas are repository
configuration, not skill constants. Record every binding reason.

Treat launch fanout as a per-wave pressure limit, not a hidden global cap. With
`N` eligible bounded execution claims, all caps and measured headroom admitting
`N`, and workers that remain active, one scheduler invocation may pump repeated
waves and converge to exactly `N` authenticated execution lanes without waiting
for another cron tick. Persistent logical or service records never enter this
target merely because they exist. A lower steady state is valid only when each
missing execution slot has a concrete persisted admission or startup reason.
Separately count lanes that finish while the scheduler is still ramping up.
Nested agents do not disappear behind the parent lane: reject them unless the
frozen specification enables them, and when enabled count every child as an
independent execution, transport, turn, request start, in-flight request, and
outstanding-request owner under the same global limits.

Use this shape outside the global scheduler lease:

```text
until effective_target is full:
  reconcile authenticated, finished, and failed startups
  recompute execution target - live - starting and every transport/request limiter
  if no slots remain, persist the exact binding limiter and stop
  launch min(available slots, launch fanout) new task-local lanes
  wait only for bounded startup events or the invocation deadline
```

The loop must have a time budget and a no-progress guard. Reaching either is an
explicit underfill reason, not permission to report reservations as live.

Run a fail-closed breaker over request starts per rolling interval, in-flight
requests/connections, provider errors, host pressure, and unauthorized
continuations. An open breaker admits no new Enter key, follow-up, resume, or
fresh launch. Reset requires the repository's explicit audited operator policy;
ordinary cron/watchdog ticks cannot close it.

## 6. Handoff And Integration

Workers write only inside task ownership. A valid result is copied with its
patch into immutable queue storage before liveness pruning. The queue entry
records baseline, checksum, changed paths, dependencies, conflicts, validation
hints, retry class, and current state.

Master selects dependency-ready, conflict-safe entries, applies them to the
preserved canonical checkout, runs repository-provided gates, and updates
checklist/status/Gantt surfaces. Batch only according to configured limits.
Failed entries move aside for bounded repair so they do not pin the queue head.

## 7. Process Cleanup

Stop the task-local tmux server first. Then inspect recorded process identity,
cwd, and task-local environment for surviving descendants. Terminate only
processes attributable to controller-owned task roots. Recheck after one
scheduler interval to prove no cron source recreated them.

## 8. Observability

For blueprint `<dir>/<name>_Blueprint.<ext>`, atomically generate
`<dir>/<name>_Gantt.<ext>` as a read-only Kanban projection. Preserve the
complete prefix and replace only the terminal `Blueprint` token. If the stem
does not end in `Blueprint`, append `_Gantt` to the complete stem and freeze the
result. Include a renderable Gantt view and a monitoring index with the
repository-relative blueprint path, specification and source digests,
generation timestamp, and every stable checklist ID exactly once. Derive
checkbox, dependency, owner, and runtime state from authoritative files and
ledgers; never read state back from the Gantt.

Use only recorded timestamps or explicitly configured estimates. Keep work
without trustworthy timing visible as unscheduled instead of fabricating a
calendar. A tick is not successful if the companion is absent, misnamed,
non-renderable, digest-stale, missing an item, or still reflects pre-tick state.
The final completed Gantt remains a completion surface when controller runtime
is removed.

Report independently:

- checklist counts
- logical claims and persistent service records
- bounded agent execution claims, starting lanes, and live transports
- authenticated goals and currently running turns
- request starts per rolling interval, in-flight/outstanding requests,
  unauthorized continuations, and breaker state
- harvested/finished handoffs
- dependency, conflict, resource, and route blocks
- integration and repair backlog
- last successful progress and cleanup status

Never call a claim live based only on its ledger status or process name.
