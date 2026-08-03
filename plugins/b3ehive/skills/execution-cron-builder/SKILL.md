---
name: execution-cron-builder
description: Build or repair repository-agnostic, blueprint-driven execution crons with isolated task roots, durable handoff, validation gates, and cleanup-on-complete. When Codex is selected, every claim must use one independent interactive Codex TUI process in its own task-local tmux server with a private CODEX_HOME and exactly one authenticated `/goal`; Codex app-server, `codex exec`, shared daemons, and no-tmux workers are forbidden. Use for continuous blueprint execution or for repairing execution-controller boundaries, transport, concurrency, integration, or cleanup.
---

# Execution Cron Builder

Build the controller from the current repository's evidence. Do not reuse a
generated controller or policy snapshot from another project.

## Non-Negotiable Invariants

1. Exactly one repository file is the authoritative blueprint and checklist.
2. Checklist state is `[ ]` not done, `[_]` worker self-tested, or `[x]` Master
   accepted. Workers never edit authoritative checkboxes and never write `[x]`.
3. Every claim owns an isolated task root and immutable claim identity.
4. Codex transport is exactly task-local tmux + interactive Codex TUI + one
   authenticated active `/goal` + private writable `CODEX_HOME`.
5. Codex app-server, app-server JSON-RPC, `codex exec`, shared Codex daemons,
   shared tmux servers, shared writable Codex state, and no-tmux Codex workers
   are hard failures. There is no fallback.
6. Worker output is provisional until the canonical Master integrates it and
   reruns the target repository's acceptance gates.
7. Cleanup is allowed only after all required work and handoffs are resolved.

## Portability Hard Gate

This skill is a generator, not a source of target-project constants. Before
writing code, inspect the target repository and freeze a repository-local
execution specification containing:

- canonical repository root and authoritative blueprint path
- checklist parser and stable item-id rules
- real dependency edges and any explicit layer semantics
- task/runtime root and owned-path policy
- worker result and Master acceptance schemas
- repository-provided validation profiles and artifact policy
- completion surfaces that must be reconciled
- selected agent platform and route policy
- logical, startup, running-turn, integration, and validator limits
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
merge into or push from the canonical checkout. Persistent repair reuses the
same task root and claim identity.

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

For exactly one goal per claim:

1. Start the TUI and handle only currently active first-run/trust prompts.
2. Detect the real idle composer, not a selector or stale scrollback glyph.
3. Paste `/goal <objective>` through a task-local tmux buffer.
4. Append a claim-specific completion token to the short objective and poll
   `capture-pane -p -J` until that final token is visible in the active composer.
   PTY input is ordered, so the final token proves the preceding `/goal` text
   arrived. Paste completion and key delivery are not assumed synchronous under
   load. A timeout retires the launch; it never submits partial input.
5. Submit once. Never spray duplicate Enter keys or resend `/goal` blindly.
6. Authenticate thread, active goal, route, cwd, and task-local registry.

### Startup State Machine

Use durable states such as:

```text
reserved -> materialized -> tmux_started -> goal_pasted -> goal_submitted
         -> live -> handoff_ready -> finished
```

Only `live` consumes authenticated live capacity. A `goal_submitted` lane whose
exact tmux/PID identity remains alive may stay `starting` until a configurable
hard deadline and be promoted by a later tick when registry writes appear. Do
not kill/relaunch a healthy TUI merely because authentication is slow. Release
or repair dead/mismatched lanes with bounded retries.

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

Broad process-name counts are telemetry, never liveness proof. When a durable
result is harvested, stop that claim's tmux server immediately. Cleanup must
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
record is a reservation, not completion proof. Finished/handoff claims do not
consume live capacity and must not retain an idle TUI.

Rework uses the same task, thread, and active goal as an ordinary follow-up
turn. It never starts a second `/goal`.

## Concurrency And Admission

Do not impose a universal worker count. Freeze separate configurable limits:

- logical claim cap
- startup reservation cap and launch fanout/wave size
- authenticated running-turn cap
- integration cap
- CPU and accelerator validator leases
- exact-path conflict budget

The operator's requested count is a hard ceiling, not permission to overload
the host. Admission accounts for CPU/load, available memory, swap pressure,
process/PID headroom, disk budget, startup backlog, external rate limits,
validator leases, and write conflicts. Never launch lane `N+1`.

The launch fanout limits one startup wave; it must not silently become the
overall concurrency target. When `N` dependency-ready, conflict-safe claims
exist and every configured cap and measured headroom admits `N`, repeated
bounded waves must converge to `N` authenticated live lanes. Every unfilled
slot must have a persisted binding reason rather than a generic "capacity"
label. Count lanes that finish during ramp-up as completed throughput, not as a
launch failure.

Within one scheduler invocation, run a bounded admission pump outside the
global lease: launch one wave, reconcile startup authentication, recompute
availability, and immediately launch the next wave. Do not wait for the next
cron cadence while admissible slots remain. Stop only at the effective target,
the invocation time budget, or a concrete binding condition; persist which one.

Report logical claims, starting lanes, authenticated live lanes, running turns,
finished handoffs, conflict-blocked work, resource-blocked work, and integration
backlog separately. Do not report reservations or OS process counts as live
`/goal` concurrency.

## Scheduler Tick

Keep scheduler ownership short and resumable:

1. Acquire one repository-local scheduler lease.
2. Validate the frozen execution specification and transport surfaces.
3. Harvest durable handoffs before any stale-claim pruning.
4. Reconcile dead, mismatched, interrupted, finished, and accepted claims.
5. Validate blueprint/DAG truth and regenerate status.
6. Integrate a bounded conflict-safe dependency-ready batch.
7. Reserve a bounded claim set atomically.
8. Release the global lease before slow preparation, TUI startup, network work,
   model turns, tests, or integration validation.
9. Pump bounded launch waves outside the lease until admitted capacity is full,
   the tick budget expires, or a concrete block is persisted; record every
   transition and never wait on cron cadence merely to launch the next wave.
10. Reacquire briefly to merge outcomes, refresh status, and schedule cleanup.

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
reconciliation.

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
- only fully authenticated claims count as live
- delayed `goal_submitted` authentication promotes without duplicate launch
- dead/mismatched startup is released after its bounded deadline
- harvest occurs before prune and finished TUI servers are stopped
- scheduler locks are not inherited by workers
- caps and host admission prevent `N+1`
- with `N` eligible fixture claims, all limits admitting `N`, and mock TUIs that
  remain live, one admission pump reaches exactly `N` authenticated lanes
- every intentional underfill has a specific persisted dependency, conflict,
  startup, host-resource, external-limit, route, or validator reason
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
