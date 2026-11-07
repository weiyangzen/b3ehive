# Execution Controller Pattern

On-demand detail for `SKILL.md`. Names and paths are placeholders. Sections
marked v1 text were moved verbatim from the v1 SKILL.md.

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

### Portability Hard Gate (v1 text)

This skill is a generator, not a source of target-project constants. Before
writing code, inspect the target repository and freeze a repository-local
execution specification containing:

- canonical repository root and authoritative blueprint path
- deterministic same-prefix Gantt companion path and rendering policy
- checklist parser and stable item-id rules
- real dependency edges and any explicit layer semantics
- task/runtime root and owned-path policy
- worker result and Master acceptance schemas
- repository-provided validation profiles and artifact policy
- completion surfaces that must be reconciled
- selected agent platform and route policy
- worker lifecycle mode (`bounded` or `persistent_pool`), desired live-worker
  target, hard cap, replacement policy, and terminal/stop conditions
- nested-agent policy and, if enabled, parent/child identity and accounting
- logical/service-record, agent-execution, startup, live-transport,
  running-turn, outbound-request-rate, in-flight-request, integration, and
  validator limits
- per-execution outstanding-request limit, cooldown, request-storm circuit
  breaker, and explicit operator reset policy
- scheduler cadence, lease policy, budgets, and exact cron marker

Do not carry over project names, absolute paths, stage numbers, item prefixes,
model/provider names, service tiers, concurrency values, GPU counts, validators,
artifact paths, evidence categories, or completion documents from a previous
repository. Examples in this skill illustrate shapes only. Generated values
must come from current repository evidence or explicit operator input.

If a policy cannot be discovered and guessing could alter source, spend money,
publish data, or delete artifacts, fail closed and name the missing field. For
low-risk housekeeping limits, use conservative environment-overridable defaults
and record that they are defaults rather than repository requirements.

### Repository Discovery (v1 text)

Inspect, at minimum:

- repository instructions, current branch/upstream, and dirty worktree state
- candidate blueprint/checklist files and duplicate requirement sources
- build, test, lint, typecheck, benchmark, and packaging entry points
- ownership boundaries, generated files, large artifacts, and ignored paths
- available CPU, memory, swap, process/PID, disk, and accelerator capacity
- existing cron entries, locks, ledgers, task roots, and worker processes
- configured agent CLI and explicit model/effort/service settings

Never reset, stash, checkout, overwrite, or delete unrelated user changes. A
dirty canonical checkout is an integration condition to preserve, not an excuse
to clone or rewrite the complete repository per worker. Sync/push behavior is
enabled only when the repository policy and operator request require it.

## 2. Blueprint Protocol And Same-Name Gantt Kanban Monitoring (v1 text)

Use one authoritative checklist with stable IDs:

- `[ ]`: unclaimed, implementation needed, or repair needed
- `[_]`: durable worker handoff exists, Master acceptance remains
- `[x]`: Master integrated the result and passed required gates

The controller or canonical Master may write `[_]` only after harvesting a
checksum-valid worker handoff. Only the canonical Master writes `[x]`. Treat
`[ ]` and `[_]` as unfinished for dependency closure and cleanup.

Generate a current todo/status surface from that checklist. It should expose:

- separate counts for `[ ]`, `[_]`, and `[x]`
- unresolved DAG nodes and justified `depends_on` edges
- claim, startup, live, handoff, integration, repair, and blocked states
- claim owner and repository-relative owned paths
- implementation, validation-preparation, and integration frontiers
- logical and admitted saturation plus the reason for any underfill

Generate a mandatory same-name Gantt companion to monitor that Kanban. The
same-name rule preserves the directory, extension, and complete prefix before a
terminal `Blueprint` filename token, replacing only that token with `Gantt`:
`<dir>/<name>_Blueprint.<ext>` maps to `<dir>/<name>_Gantt.<ext>`. For example,
`Stage_3_AR_Blueprint.md` maps to `Stage_3_AR_Gantt.md`; never collapse it to
`Stage_3_Gantt.md` or rename it to `Stage_3_AR_Blueprint.gantt.md`. If the
authoritative filename does not end in `Blueprint`, append `_Gantt` to its
complete stem and freeze that path in the specification. The companion is a
generated read-only projection, never a second checklist or authority, and
must contain no mutable checkboxes.

The Gantt must include a renderable Gantt view plus source-relative identity,
specification/source digests, and generation time. Its monitoring index must
represent every stable checklist ID exactly once and derive checkbox state,
dependencies, claim/owner, and startup/live/handoff/integration/repair/blocked
state from the authoritative checklist and durable ledgers. Use only recorded
timestamps or estimates explicitly present in repository/operator policy;
place items without trustworthy timing in a visible unscheduled section rather
than inventing dates or omitting them. Write the companion atomically after
state reconciliation and before the scheduler tick returns. A missing,
misnamed, stale-digest, duplicate-ID, or incomplete companion is a validation
failure. The Gantt may be the current todo/status surface only when it exposes
all fields required above; do not create competing generated authorities.

Reject duplicate IDs, missing dependencies, cycles, unsupported checkbox marks,
and synthetic dependency chains inferred only from document order. If the
blueprint defines genuine layers, close lower dependencies before higher ones;
do not turn presentation order into a global barrier.

## 3. Task Isolation (v1 text)

Give every claim a unique root such as:

```text
<runtime-root>/tasks/<claim-id>/<run-id>/
  work/
  codex-home/          # Codex only
  tmux.sock            # Codex only
  claim.json
  result.json
```

Materialize only declared writable paths and individually justified read-only
bootstrap files, preserving repository-relative names and independent inodes.
Never place secrets in the task workspace. Do not copy, clone, rsync, reflink,
hardlink, archive, or mount the complete repository per claim. Reject legacy
full-repository worker templates and task-by-repository snapshot layouts.

A task may use a small local Git baseline containing only its allowed files.
Workers produce repository-relative patches/bundles and checksums; they do not
merge into or push from the canonical checkout. A bounded repair uses a fresh
execution/run root and terminal goal. A persistent worker replacement keeps the
stable logical claim but creates a fresh generation, task identity, process,
private state, and exactly one new `/goal`; it never overlaps the retired
generation after liveness is resolved.

Validate before launch and harvest:

- the task root belongs to exactly one claim
- every file is declared and has an independent inode
- controller-owned claim metadata is unchanged
- forbidden runtime paths and full-checkout sentinel combinations are absent
- changed paths remain inside exact ownership

## 4. Claims And Handoff (v1 text)

The immutable claim card records:

- claim/run/item IDs, mode, dependencies, baseline, and deadline
- exact writable paths and read-only bootstrap files
- concise deliverable and repository-specific validation commands
- allowed/forbidden artifacts and result schema
- task root, authoritative checkout as a forbidden write target, and retry budget

The result manifest records truthful per-item changed paths, patch checksum,
commands and outcomes, artifact references, and `status=self_tested`. Require
only evidence applicable to the current item. Do not invent universal evidence
categories or mark inapplicable gates passed.

Harvest before pruning. Copy a valid result and patch into immutable
controller-owned queue storage keyed by claim, baseline, and checksum. A claim
record is a reservation, not liveness proof. Finished bounded handoffs release
their TUI. Persistent workers may emit periodic results without becoming
terminal; the generation remains live only under the exact liveness contract.
Rework is a new bounded execution unless the persistent worker's frozen
objective explicitly includes that maintenance cycle. Replacement always uses
a new generation and exactly one new `/goal` after the old generation is
retired.

### Handoff And Integration

Workers write only inside task ownership. A valid result is copied with its
patch into immutable queue storage before liveness pruning. The queue entry
records baseline, checksum, changed paths, dependencies, conflicts, validation
hints, retry class, and current state.

Master selects dependency-ready, conflict-safe entries, applies them to the
preserved canonical checkout, runs repository-provided gates, and updates
checklist/status/Gantt surfaces. Batch only according to configured limits.
Failed entries move aside for bounded repair so they do not pin the queue head.

## 5. Durable State

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

## 6. Concurrency And Admission (v1 text)

Do not impose a universal worker count. Freeze separate configurable limits:

- logical claim cap
- persistent service-record cap, when the repository has long-running work
- admitted agent-execution cap
- startup reservation cap and launch fanout/wave size
- live TUI transport cap
- authenticated running-turn cap
- outbound model/API request starts per rolling interval
- in-flight model/API request cap
- exactly one outstanding request per agent execution
- integration cap
- CPU and accelerator validator leases
- exact-path conflict budget

The operator's requested worker count is both the desired live target and hard
ceiling when the specification says so. It is not permission to exceed host or
provider caps. Admission accounts for
CPU/load, available memory, swap pressure, process/PID headroom, disk budget,
startup backlog, provider rate limits, current request starts, in-flight
requests, validator leases, and write conflicts. Never launch lane `N+1` or
submit request `R+1`.

The launch fanout limits one startup wave; it must not silently become the
overall concurrency target. When `N` dependency-ready, conflict-safe claims
exist and every configured cap and measured headroom admits `N`, repeated
bounded waves converge to the configured agent-execution target. A logical or
service count becomes that target only through an explicit one-to-one persistent
worker mapping in the frozen specification. Every unfilled slot
must have a persisted binding reason rather than a generic "capacity" label.
Count lanes that finish during ramp-up as completed throughput, not as a launch
failure.

Within one scheduler invocation, run a bounded admission pump outside the
global lease: launch one wave, reconcile startup authentication, recompute
availability, and immediately launch the next wave. Do not wait for the next
cron cadence while admissible slots remain. Stop only at the effective target,
the invocation time budget, or a concrete binding condition; persist which one.

Report logical/service records, agent execution claims, starting lanes, live
TUI transports, authenticated goals, running turns, request starts per window,
in-flight requests, outstanding requests, unauthorized continuations, finished
handoffs, blocked work, breaker state, and integration backlog separately. Do
not report reservations, OS processes, sockets, goals, turns, or API requests
as interchangeable concurrency.

### Admission Formulas And Pump

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
`N` eligible worker claims, all caps and measured headroom admitting `N`, and
workers that remain active, one scheduler invocation may pump repeated waves and
converge to exactly `N` authenticated lanes without waiting for another cron
tick. Persistent logical/service records enter this target only when the frozen
specification maps them one-to-one to persistent workers. After proved death,
retire the old generation and refill its slot without exposing `N+1`. A lower
steady state is valid only when each missing slot has a concrete persisted
admission or startup reason.
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

## 7. Scheduler Tick (v1 text)

Keep scheduler ownership short and resumable:

1. Acquire one repository-local scheduler lease.
2. Validate the frozen execution specification and transport surfaces.
3. Harvest durable handoffs before any stale-claim pruning.
4. Reconcile dead, mismatched, interrupted, finished, and accepted claims.
5. Validate blueprint/DAG truth and regenerate status and the same-name Gantt.
6. Integrate a bounded conflict-safe dependency-ready batch.
7. Reserve a bounded claim set atomically.
8. Release the global lease before slow preparation, TUI startup, network work,
   model turns, tests, or integration validation.
9. Pump bounded launch waves outside the lease until the frozen live-worker
   target is full, the tick budget expires, or a concrete block is persisted.
   In persistent mode, replace dead generations promptly without exceeding the
   hard cap; derive demand from logical claims only when the specification
   explicitly maps them one-to-one to persistent workers.
10. Reacquire briefly to merge outcomes, atomically refresh status and the
    same-name Gantt from the merged state, and schedule cleanup.

If using `flock`, close its file descriptor before every tmux launch so workers
cannot inherit and pin the scheduler lock. A cron tick must be safe to retry and
must not require one long process to wait for workers to finish.

## 8. Master Integration (v1 text)

The canonical Master owns patch application, conflict resolution, validation,
checkbox mutation, checkpointing, and optional push. Integrate only when real
dependencies and ownership conflicts permit it. Batching thresholds are
repository-configurable heuristics, not skill-wide constants.

Use the repository's actual acceptance policy. Tests, fixtures, docs, generated
code, binaries, and evidence may be edited or committed when that policy
requires them. Do not impose foreign rules such as "never commit tests",
docs-to-code ratios, fixed batch item counts, fixed diff sizes, or model-specific
evidence gates.

On validation failure, preserve the worker handoff, classify the failure, and
move it to bounded repair without blocking unrelated ready entries. Advance
`[_] -> [x]` only after integrated validation and required completion-surface
reconciliation, including the same-name Gantt projection.

## 9. Budgets And Cleanup (v1 text)

Derive disk/log/process thresholds from repository/operator policy and host
capacity. Defaults must be environment-overridable and visible in validate-only
output. Measure allocated disk blocks, exclude symlinks, bound logs, and remove
only stale roots not referenced by a live claim or durable handoff.

Cleanup is idempotent and repository-scoped. On explicit stop or completion:

- remove only the exact cron marker for this controller
- stop scheduler processes and every task-local tmux server it owns
- terminate surviving task-descended subprocesses without broad host-wide kills
- preserve canonical source and accepted artifacts
- remove controller runtime only after no live references remain
- verify cron entries, scheduler processes, task processes, sockets, locks, and
  runtime roots are absent

Completion cleanup additionally requires zero `[ ]`, zero `[_]`, no pending
handoff/integration/repair entry, all repository gates passing, and every
required status surface reconciled.

In `persistent_pool` mode, a cycle handoff, an empty repair queue, or accepted
implementation checkboxes do not complete the maintenance service. Keep its
authenticated goal and transport resident until the frozen service stop
condition is met or the operator explicitly stops it. Do not use bounded-job
cleanup to terminate a healthy pool between cycles.

### Process Cleanup

Stop the task-local tmux server first. Then inspect recorded process identity,
cwd, and task-local environment for surviving descendants. Terminate only
processes attributable to controller-owned task roots. Recheck after one
scheduler interval to prove no cron source recreated them.

## 10. Observability

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
