---
name: execution-cron-builder
description: Build or repair repository-agnostic, blueprint-driven execution crons with same-name Gantt Kanban monitoring, isolated agent workers, durable handoff, validation gates, explicit worker lifecycle, request accounting, and cleanup. When Codex is selected, each admitted worker generation uses one independent interactive Codex TUI process in its own task-local tmux server with a private CODEX_HOME and exactly one submitted `/goal`; the repository blueprint chooses bounded terminal executions or a persistent goal pool whose dead workers are replenished to an exact target. Codex app-server, `codex exec`, shared daemons, and no-tmux workers are forbidden. Use for continuous blueprint execution or for repairing execution-controller boundaries, transport, concurrency, replenishment, request storms, integration, monitoring, or cleanup.
---

# Execution Cron Builder

Build the controller from the current repository's evidence. Do not reuse a
generated controller or policy snapshot from another project.

## Non-Negotiable Invariants

1. Exactly one repository file is the authoritative blueprint and checklist.
2. Checklist state is `[ ]` not done, `[_]` worker self-tested, or `[x]` Master
   accepted. Workers never edit authoritative checkboxes and never write `[x]`.
3. Every claim owns an isolated task root and immutable claim identity.
4. Codex transport for every admitted worker generation is exactly
   task-local tmux + interactive Codex TUI + one submitted and authenticated
   `/goal` + private writable `CODEX_HOME`. The frozen repository specification
   explicitly selects `bounded` or `persistent_pool`; logical/service identity
   implies a live goal only when that specification defines a one-to-one
   persistent worker mapping.
5. Codex app-server, app-server JSON-RPC, `codex exec`, shared Codex daemons,
   shared tmux servers, shared writable Codex state, and no-tmux Codex workers
   are hard failures. There is no fallback.
6. Goal authentication, a running model turn, an outbound request start, and
   an in-flight API request are distinct states with distinct counters. Every
   submission requires an atomic request lease before Enter; no scheduler,
   watchdog, cron, or goal continuation may bypass it.
7. Lifecycle is not inferred. In `bounded` mode a result/handoff terminalizes
   the goal and transport. In `persistent_pool` mode the authenticated goal is
   the long-running worker: it remains live until explicit stop or liveness
   failure, and the controller replaces a dead generation without exceeding the
   desired or hard worker cap. Authorized goal continuation is counted work,
   never an untracked request or an excuse to create an extra worker.
8. A parent execution does not hide child-agent or subagent concurrency. Unless
   the repository-local specification explicitly admits nested agents, they are
   forbidden. If admitted, every child has an independent execution identity,
   transport, turn, request lease, outstanding-request slot, terminal result,
   and full accounting under the same global caps; a child is never "free"
   capacity behind one worker count.
9. Worker output is provisional until the canonical Master integrates it and
   reruns the target repository's acceptance gates.
10. Cleanup is allowed only after all required work and handoffs are resolved.

## Portability Hard Gate

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

## Repository Discovery

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

## Blueprint Protocol

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

## Task Isolation

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

## Codex Transport

Generated controllers must freeze and test these equivalent values:

```text
WORKER_TRANSPORT=tmux_codex_tui
WORKER_GOAL_COMMAND=/goal
APP_SERVER_WORKERS=forbidden
CODEX_PROCESS_ISOLATION=one_process_tree_per_claim
CODEX_STATE_ISOLATION=one_writable_home_per_claim
WORKER_LIFECYCLE=repository_specified
PERSISTENT_SERVICE_TUI=repository_specified
AUTOMATIC_GOAL_CONTINUATION=repository_specified_and_counted
MAX_OUTSTANDING_REQUESTS_PER_EXECUTION=1
```

### Launch Shape

Construct argv as an array. Apply model, reasoning, provider, and service-tier
arguments only when explicitly selected by repository/operator policy;
otherwise let installed Codex configuration choose and record the resolved
route after startup.

```bash
codex_argv=(codex -C "$WORK_ROOT" -c features.goals=true --no-alt-screen)
[[ -n "${CODEX_MODEL:-}" ]] && codex_argv+=(-m "$CODEX_MODEL")
[[ -n "${CODEX_REASONING_EFFORT:-}" ]] && \
  codex_argv+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
[[ -n "${CODEX_SERVICE_TIER:-}" ]] && \
  codex_argv+=(-c "service_tier=$CODEX_SERVICE_TIER")

tmux -S "$TASK_ROOT/tmux.sock" -f /dev/null new-session -d \
  -s "$SESSION" -c "$WORK_ROOT" \
  env -u CODEX_CI -u CODEX_THREAD_ID -u CODEX_REMOTE_PAYLOAD \
  CODEX_HOME="$TASK_ROOT/codex-home" \
  "${codex_argv[@]}"
```

Each claim receives its own tmux server/socket/session and ordinary interactive
Codex OS process tree. Do not host multiple claims in windows or panes of one
server. Do not import Codex into the controller, multiplex claims through a
service, or reuse another claim's wrapper/native process.

Bootstrap each `CODEX_HOME` with only required credentials and minimal
route/provider configuration. Do not copy project trust history, plugins,
marketplaces, MCP servers, prior threads, goals, logs, or SQLite registries.

### Goal Handshake

Use a controller-owned immutable claim card. Keep `/goal` short: identify the
claim, deliverable, task root, claim-card path/digest, result path, and hard
boundaries. Put detailed ownership, dependencies, acceptance commands, and
artifact rules in the claim card.

For exactly one goal per worker generation:

1. Start the TUI and handle only currently active first-run/trust prompts.
2. Detect the real idle composer, not a selector or stale scrollback glyph.
3. Paste `/goal <objective>` through a task-local tmux buffer.
4. Append a claim-specific completion token to the short objective and poll
   `capture-pane -p -J` until that final token is visible in the active composer.
   PTY input is ordered, so the final token proves the preceding `/goal` text
   arrived. Paste completion and key delivery are not assumed synchronous under
   load. A timeout retires the launch; it never submits partial input.
5. Atomically acquire both a running-turn lease and an outbound-request lease,
   then submit once. Never spray duplicate Enter keys or resend `/goal`
   blindly. If either lease is unavailable, leave the complete text unsubmitted
   or retire the prepared lane according to repository policy.
6. Authenticate thread, active goal, route, cwd, and task-local registry.
7. Apply the frozen lifecycle. A bounded result terminalizes the exact goal and
   transport. A persistent worker remains active across maintenance cycles;
   normal continuation is authorized only for that generation and counts under
   the same request/in-flight caps. On process/goal death, explicit stop, or
   identity ambiguity, retire that generation before admitting its replacement.

### Startup State Machine

Use lifecycle-specific durable states such as:

```text
reserved -> materialized -> tmux_started -> goal_pasted -> request_leased
         -> goal_submitted -> turn_running -> handoff_ready
         -> goal_terminal -> transport_stopped -> finished

persistent_reserved -> materialized -> tmux_started -> goal_pasted
                    -> request_leased -> goal_submitted -> authenticated_live
authenticated_live -> maintenance_cycle -> authenticated_live
authenticated_live -> dead_or_stopped -> generation_retired
generation_retired -> replacement_reserved
```

`tmux_started` consumes live-transport capacity; `request_leased` consumes
outbound request capacity; `goal_submitted` consumes one outstanding-request
slot; and only a proved `turn_running` consumes running-turn capacity. A
`goal_submitted` lane whose exact tmux/PID identity remains alive may stay
`starting` until a configurable hard deadline and be promoted by a later tick
when registry writes appear. Do not relaunch merely because authentication is
slow. Release or repair dead/mismatched lanes with bounded retries. A provider
event sequence that starts another turn after a bounded result without a new
controller request lease is unauthorized. In persistent mode, continuation is
authorized only while the exact generation and goal are live and the request is
accounted under the frozen caps. A replacement never overlaps a generation that
has not been proved dead, fenced, or explicitly stopped.

### Liveness

Count a Codex lane only when all are true:

- claim route and transport policy are valid
- task-local tmux server and session exist
- pane PID and process start time match the durable claim
- cwd equals the claim work root
- task-local `CODEX_HOME` is unique to the claim
- resolved route satisfies every explicitly frozen route field
- thread ID and active goal ID/status match the task-local registries
- goal objective names the claim

Broad process-name counts are telemetry, never liveness proof. Stop a bounded
claim immediately after its durable result; keep a persistent generation only
while all liveness facts remain true. Cleanup must
also terminate claim-descended subprocesses identified by recorded PID/start
time, task cwd, or task-local environment, without touching unrelated Codex
processes on the host.

## Other Agent Platforms

The controller may expose adapters for Claude Code, opencode, OpenClaw, or
Hermes. Preserve explicit platform settings and validate each adapter's own
identity. `B3EHIVE_AGENT_RUNNER` may define non-Codex runners. For Codex it may
customize TUI argv only; it cannot bypass tmux, interactive `/goal`, independent
process/state, or authentication requirements.

## Claims And Handoff

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

## Concurrency And Admission

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

## Scheduler Tick

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

## Master Integration

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

## Budgets And Cleanup

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

## Generated Validation

Every generated or repaired controller must include tests proving:

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

## References

- Read [references/execution-pattern.md](references/execution-pattern.md) when
  implementing scheduler phases, ledgers, handoff, and concurrency.
- Read [references/gate-rules.md](references/gate-rules.md) when implementing
  generated validation and cleanup gates.
- When composed with b3ehive looper behavior, follow
  `../looper-cron-builder/references/b3ehive-bridge-contract.md` for leases,
  evidence, ROI, and nested-run accounting. A nested execution run requires an
  active parent lease, records its `ParentLeaseRef` in the `NestedRunLedger`,
  and cannot write `[x]`; its output remains provisional for parent/Master
  acceptance. Emit `looper_log`/`LooperLog`
  evidence when execution reveals feedback about an `InstrumentObject` such as
  a route, launcher, validator, scaffold, ledger, or this skill itself; name the
  affected `TargetObject`. Logging feedback does not authorize instrument
  mutation, which still requires the shared EvidenceLint, ROI, ParetoGate,
  rollback, and Master acceptance lifecycle.
