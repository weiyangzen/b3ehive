---
name: execution-cron-builder
description: Build or repair a blueprint-driven execution cron for a repository using one authoritative blueprint, a daily todo snapshot, an isolated automation clone, bounded agent-runner batches for Codex, Claude Code, opencode, OpenClaw, or Hermes, validation gates, checkpoint commits, and cleanup-on-complete. Use when a repo should continuously implement a blueprint, when an execution cron needs to be added to a new repository, or when an existing blueprint-execution cron needs boundary/gate fixes.
---

# Execution Cron Builder

## Controller Contract

Build a scheduled, repository-local controller around exactly one authoritative blueprint file and its execution checklist. Isolated `tmux` workers claim DAG-ordered implementation items up to the user's concurrency cap and submit self-tested evidence. The main session integrates, validates, checkpoints, and closes items in dependency order. Real implementation evidence, strict layer order, code-first commits, and the cleanup hard gate govern acceptance.

## Shared b3ehive Contract

For route selection, estimator decisions, nested calls, evidence handoff,
looper_log capture, ROI, and self-evolution behavior, follow the suite contract
in `../looper-cron-builder/references/b3ehive-bridge-contract.md`.

Local obligations:

- Execution advances the target object through the DAG. Worker output is `[_]`;
  only the master/integration lane writes `[x]`.
- Nontrivial automatic choices of batch size, worker count, split threshold,
  validator, route, or nested skill should leave `EstimatorPolicy` and
  `RouteDecision` evidence.
- Emit `looper_log` when execution exposes repeated validator failure, DAG
  split friction, worker prompt/root mismatch, integration bottleneck, stale
  scaffolding, hook/guard overreach, route waste, or tool integration friction.
- Each `looper_log` must identify the `TargetObject` being implemented or
  integrated and the `InstrumentObject` that produced the signal: DAG split,
  worker batch, validator, guard, route, scaffold, tool, or skill composition.
- Looper logs provide evidence and backlog for the instrument set. They do not
  block normal worker refill unless the issue is a hard safety gate.
- A looper-log-derived change to execution policy, guards, scaffolds, or skill
  text requires EvidenceLint, ROI, ParetoGate, rollback, and master `[x]`.

## Dual-Cursor Checklist State Protocol

All execution checklists and generated todos must use exactly these three states:

- `[ ]` means not done: unclaimed, not yet implemented, or still requiring a worker.
- `[_]` means worker self-tested: worker output exists and the worker's local
  validation passed, but the main/master integration lane has not accepted,
  merged, and revalidated it yet.
- `[x]` means master accepted: the main/master lane integrated the output into
  the authoritative checkout, reran the required gates, reconciled completion
  surfaces, and accepted the item as complete.

The checkbox mark is the cursor state. The worker cursor advances `[ ] -> [_]`.
The master cursor advances `[_] -> [x]`. Workers must never write `[x]`; the
scheduler treats `[_]` as unfinished.

Protocol:

- Checklist parsers must recognize `[ ]`, `[_]`, and `[x]`; any other checkbox
  state is invalid.
- Generated blueprints, todos, ledgers, progress tables, summaries, and status
  commands preserve this exact state vocabulary. Extra fields may add detail;
  the checkbox remains the source of truth. They must not invent labels such as
  `done`, `pending`, `landed`, or `validated` as replacement completion states.
- Bootstrap generators initialize new items as `[ ]`.
- Regenerators preserve existing `[ ]`, `[_]`, and `[x]` marks by item id and
  may only downgrade a mark when a guard has explicit evidence that the current
  mark is invalid.
- Worker prompts must instruct workers to mark only their assigned items as
  `[_]` after implementation and self-test evidence exists.
- Worker completion evidence must include changed paths, validation commands,
  validation output summary, and branch/worktree/commit reference when
  applicable.
- Daily todos must report counts for `not_done`, `worker_self_tested`, and
  `master_accepted`.
- Worker claim frontiers are computed from `[ ]` items only.
- Main-session integration frontiers are computed from `[_]` items whose
  dependencies are `[x]` and whose path conflicts are resolved.
- Live worker capacity is consumed by live claims only, not by `[_]` finished
  items waiting for master integration.
- Dependency closure treats `[ ]` and `[_]` as unfinished. A dependent item can
  be master-accepted only after all dependencies are `[x]`.
- Cleanup is forbidden while any `[ ]` or `[_]` item remains.
- Progress math must report three counts separately and may derive
  `unfinished = count([ ]) + count([_])`; `[_]` must never be collapsed into
  `[x]` for percentages, cleanup, or release gates.
- If an item remains `[_]` across repeated master validation attempts, create a
  repair child item as `[ ]`, keep the parent `[_]`, and record the failed gate.
- If a worker incorrectly writes `[x]`, the guard must downgrade it to `[_]`
  unless master validation evidence for that item already exists in the
  authoritative checkout.
- If master validation fails after integrating a worker output, the authoritative
  item stays `[_]`, the failed gate is recorded, and any follow-up repair item
  starts as `[ ]`.

## Workflow

1. Inspect the repository, identify the single blueprint requirement file, and freeze its execution boundary. Exactly one file serves as the requirement source.
2. Add an authoritative checklist to a prose-first blueprint. Seed new items as `[ ]`; preserve existing `[_]` and `[x]` marks by item id.
3. Create the checklist/bootstrap generator, daily todo generator, execution guard, cron installer, and cleanup script. Keep `.ops/` and `.cron/` private.
4. Create or sync the isolated automation repos and seed any intentionally local blueprint.
5. Run `VALIDATE_ONLY=1` once before enabling cron. This dry gate validates configuration, DAG shape, sync state, and budgets, then exits before worker claims or process launch. Never use validate-only for an execution tick whose purpose is to fill worker lanes.
6. Install cron after the automation repo, checklist bootstrap, blueprint seeding, todo generation, and validate-only gate pass.
7. Run each tick through the guard protocol below: sync, prune claims, generate the DAG, refill workers, integrate landed output, validate, checkpoint, reconcile completion surfaces, and clean up when every hard signal passes.

## Agent Platform Compatibility

Generated execution cron code must support Codex, Claude Code, opencode,
OpenClaw, and Hermes through a single agent-runner abstraction.

Default platform selection:
- `B3EHIVE_AGENT_PLATFORM=codex` uses `codex exec`.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=opencode` uses `opencode run`.
- `B3EHIVE_AGENT_PLATFORM=openclaw` uses `openclaw agent`.
- `B3EHIVE_AGENT_PLATFORM=hermes` uses `hermes chat`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose Codex when `codex` is available,
  otherwise Claude Code when `claude` is available, otherwise opencode when
  `opencode` is available, otherwise OpenClaw when `openclaw` is available,
  otherwise Hermes when `hermes` is available.

Default command templates:

```bash
# Codex
codex exec --cd "$WORKER_REPO" --model "${CODEX_MODEL:-gpt-5.3-codex}" \
  -c model_reasoning_effort="${CODEX_REASONING_EFFORT:-xhigh}" \
  < "$PROMPT_FILE" > "$OUTPUT_FILE"

# Claude Code
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"

# opencode
opencode run --dir "$WORKER_REPO" ${OPENCODE_MODEL:+--model "$OPENCODE_MODEL"} \
  ${OPENCODE_VARIANT:+--variant "$OPENCODE_VARIANT"} \
  ${OPENCODE_AGENT:+--agent "$OPENCODE_AGENT"} \
  < "$PROMPT_FILE" > "$OUTPUT_FILE"

# OpenClaw
openclaw ${OPENCLAW_PROFILE:+--profile "$OPENCLAW_PROFILE"} agent --local \
  ${OPENCLAW_AGENT:+--agent "$OPENCLAW_AGENT"} \
  ${OPENCLAW_THINKING:+--thinking "$OPENCLAW_THINKING"} \
  --message "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"

# Hermes
hermes chat ${HERMES_MODEL:+--model "$HERMES_MODEL"} \
  --toolsets "${HERMES_TOOLSETS:-skills,terminal}" \
  ${HERMES_SKILLS:+-s "$HERMES_SKILLS"} \
  -q "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"
```

If `B3EHIVE_AGENT_RUNNER` is set, it is the authoritative template. Validate-only
output must print the resolved platform, model/effort/variant/profile settings,
permission/service-tier/agent setting, and command template without leaking
secrets.

Explicit runtime settings are authoritative: `B3EHIVE_AGENT_PLATFORM`,
`B3EHIVE_AGENT_RUNNER`, `CODEX_MODEL`, `CODEX_REASONING_EFFORT`,
`CODEX_SERVICE_TIER`, `CLAUDE_MODEL`, `CLAUDE_EFFORT`,
`CLAUDE_PERMISSION_MODE`, `OPENCODE_MODEL`, `OPENCODE_VARIANT`,
`OPENCODE_AGENT`, `OPENCLAW_PROFILE`, `OPENCLAW_AGENT`,
`OPENCLAW_THINKING`, `HERMES_MODEL`, `HERMES_TOOLSETS`, and `HERMES_SKILLS`.
Each new worker uses the selected platform's requested or latest high-capability
model and effort. When no platform-specific runtime option is set, the cron may
choose a repo default and must print the chosen value in guard output.

## Required Components

### Blueprint / Todo Surface

Requirements:
- Use exactly one file as the blueprint requirement source.
- Put the authoritative execution checklist in that same blueprint.
- If the blueprint starts as prose, generate an execution checklist section into the blueprint and seed it with all `[ ]` marks before the first cron tick.
- Generate a daily `todos_YYYYMMDD.md` from that authoritative checklist section.
- Daily todos must include the current DAG of unfinished checklist items:
  - one node per `[ ]` or `[_]` unfinished item
  - dependency ids for every node
  - checkbox state (`[ ]`, `[_]`, or `[x]`)
  - worker claim state and integration-ready/blocked state
  - claim owner, if any
  - owned path scope
  - worker claim frontier, main-session integration frontier/queue, and user concurrency saturation status
  - cycle detection result
- Daily todos must show separate counts for `[ ]`, `[_]`, and `[x]`.
- Daily todos display every open item's claim state as `live:<session>`,
  `finished:<session>`, or `unclaimed`, plus the claim ledger path.
- `[_]` items must appear in an integration-ready or integration-blocked section, never in the worker-claim section unless a repair child was generated.
- Successful batches must update the authoritative blueprint and then refresh today's todo.
- Worker successful batches update assigned items to `[_]`; master successful integration batches update accepted items to `[x]`.
- If the repo requires multiple completion surfaces, successful batches must reconcile all of them in the same batch.
- Todo item source references must be stable repository-relative paths (do not leak `.cron/automation_repo*` absolute paths).
- Do not let other docs become accidental requirement sources.

### Automation Repo

Run implementation in isolated clone(s) under `.cron/automation_repo*` when the main repo may be dirty.

Requirements:
- Clone/sync from the repo's authoritative remote.
- Seed the blueprint into the automation repo if it is intentionally gitignored or local-only.
- Keep `.ops/` private via `.git/info/exclude` or equivalent.
- Keep local-only artifacts ignored: typically `.cron/`, `*.log`, `Docs/todos_*.md`, `.venv/`, `tests/`, `spec/`, `target/`, `node_modules/` depending on the repo.
- Keep execution-only docs/log artifacts ignored (`docs/*validation_log*`, research handoff docs, cron-generated ledgers) unless explicitly promoted by a human.
- If local-only artifacts were historically tracked, clean them once with `git rm --cached ...` and keep local files via ignore/exclude rules.
- For multi-worker mode, use separate worker clones such as `.cron/automation_repo`, `.cron/automation_repo_slot2`, and `.cron/automation_repo_slotN` so git index and worktree writes never collide.
- Before each worker batch: `fetch + pull --ff-only` or `fetch + rebase` against the authoritative branch.
- After each worker batch: `rebase/resolve within owned scope -> push`.
- Local authoritative repo must also stay synced (`fetch + merge --ff-only`) so "remote updated but local stale" is impossible by design.
- Newly launched `tmux` agent workers must honor the selected platform configuration; for Codex, preserve the requested service tier in `codex exec`; for Claude Code, preserve the requested `--permission-mode`; for opencode, preserve the requested `--variant` and `--agent`; for OpenClaw, preserve profile, agent, and thinking level; for Hermes, preserve model, toolsets, and preloaded skill list; if unset, use and print the repo default.
- Worker count is saturated from the todo DAG order: never exceed the user's max concurrency, but do not reduce worker count merely because dependencies are unfinished or owned paths overlap.
- Compute `worker_count = user_max_concurrency - live_worker_count`, capped by
  unclaimed open DAG nodes available in topological order.
- The main session may claim work under the active user goal. It should
  preferentially own integration, validation, dependency-gated closure, merge,
  and conflict-unblocking when worker branches or worktrees land.
- Workers must not mark checklist items `[x]`. Their terminal success state is `[_]` plus evidence.
- The main session is the only actor allowed to promote `[_]` to `[x]`.
- Worker prompt root rule:
  - the prompt's `Repository root` must equal the automation clone path where the command is launched
  - a worker launched with `cd .cron/automation_repo_slotN` names that clone as `Repository root`
  - include a line like `Work only inside this worker automation clone: <clone path>`
  - include a line like `Do not edit the scheduler's authoritative checkout directly: <main checkout path>`
  - the main checkout path may appear as that forbidden target; it may serve as
    `Repository root` only when the worker intentionally runs in the main checkout
  - generated todos, evidence paths, and blueprint references inside committed files must remain stable repo-relative paths, not clone absolute paths

### Execution Guard

Requirements:
- Run the disk/log budget guard before installing or repairing cron and at the
  start of every scheduler tick before worker spawn.
- Maintain `.cron/*state`, log, block-count, pending-checkpoint, and last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; if the Data/root volume has less free space, run cleanup and refuse to start new workers
  - default `DANGER_FREE_GB=15`; if below this, write state `blocked_disk_space` and exit immediately after lightweight cleanup
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for keepalive/scheduler logs; keep only the tail when files exceed the cap
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files under the cron root
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories
  - default `MAX_CRON_ROOT_GB=30`; if the cron root remains above this after cleanup, refuse new worker spawn
  - never delete a workspace whose path is referenced by a live selected agent-runner process, `tmux`, shell, or lock/pid file
  - write cleanup decisions to a bounded janitor log, not to an unbounded cron log
- Skip overlap if another selected agent runner is already running in the same worker repo.
- Enforce a single blueprint source.
- Enforce one authoritative execution checklist inside that blueprint.
- Enforce the dual-cursor checkbox protocol: `[ ]` for not done, `[_]` for worker self-tested, `[x]` for master accepted.
- Enforce todo DAG generation for unfinished checklist items before selecting work:
  - parse item ids and dependency metadata from the authoritative checklist or a repo-local dependency map generated from it
  - reject cycles and duplicate ids
  - compute worker-claim order from `[ ]` nodes in DAG topological order and first-open layer/cluster
  - compute the main-session integration frontier from `[_]` nodes by excluding nodes whose dependencies are incomplete, whose prerequisite worker output has not landed, or whose path conflicts are unresolved
  - write both the worker claim frontier and the integration frontier into today's todo before spawning or claiming work
- Select only the first still-open cluster and keep each run bounded.
- Select the first still-open cluster before removing claimed items.
  Worker spawn may claim additional unclaimed `[ ]` nodes from that cluster in DAG/topological order until user-requested concurrency is full, even when earlier nodes are already claimed by live workers.
  Do not choose the first unclaimed cluster; that skips lower-layer ordering and violates strict layer execution. Only the main-session integration lane may decide that a later cluster can close, and only after lower DAG dependencies are complete.
- Keep worker claiming separate from integration readiness.
  The scheduler must fill available worker slots from the ordered DAG claim frontier up to the user concurrency cap, even when those nodes depend on earlier unfinished work or touch overlapping path families.
  Mark such outputs as provisional and let the main session decide merge order, conflict resolution, validation, and closure.
- Implement worker and master ledgers as independent queues.
  The worker claim ledger records item id, original blueprint id, dependency ids,
  session name, slot, workspace path, status, claim time, owned path scopes,
  reservations, and liveness; only `live` reservations reduce available worker lanes.
  `finished` reservations are inputs to the integration queue and must not prevent the scheduler from scanning forward to later unclaimed open DAG nodes.
  Refresh worker self-test manifests into the claim ledger at the start of every guard tick, including drain/no-new-claim mode.
  Drain mode may disable new claims, but it must still promote completed worker self-tests from `live` or `selftest_missing` to `finished` and regenerate the todo so the worker cursor cannot freeze behind stale ledger state.
  Self-test manifest lookup must accept both session-only and item-qualified names, for example `worker_12.json` and `item_id.worker_12.json`.
  The integration queue records landed outputs, diff bytes, changed files, path conflicts, validation hints, and small-diff batch eligibility.
  It scans claimed worker workspaces, reports changed files and diff byte counts,
  detects path conflicts, and classifies combined diffs `<=256KiB` as small-diff
  batch candidates.
  Heavy integration queue scans are master work and must not block worker
  refill; run them after refill, incrementally, or behind an explicit refresh
  flag.
- When high concurrency is requested, parallelize worker preparation safely.
  Select claim items in stable DAG/topological order under one lock, append reservations atomically, then prepare isolated workspaces and start `tmux` sessions with bounded parallelism.
  Use a configurable preparation fan-out so clone/rsync/startup overhead does not make a 90-lane request behave like a serial launcher.
- For file-level fragmented work, enforce small-file merge batching:
  - prefer same-directory grouping
  - total source bytes per batch <=100KB
  - if one file alone exceeds 100KB, run it as a single-file batch (do not skip)
- Enforce strict layer order when the blueprint defines layered work.
  - Allow execution only in the finest still-open layer.
  - If any lower-layer item remains `[ ]` or `[_]`, upper-layer items must stay unchecked.
  - If upper-layer `[x]` is detected while a lower-layer `[ ]` or `[_]` item remains, auto-reset those upper-layer `[x]` items to `[ ]` in the authoritative blueprint, report the correction, regenerate the todo, and continue from the lower layer.
  - Block only when autoclear is disabled or re-validation still fails after autoclear.
- Detect repeated unresolved items: when the same checklist item remains unresolved for repeated ticks (default >=5), split it into child checklist items, sync the blueprint and todo, and notify the human with the split details.
- Parent-child closure rule: if all child checklist items are `[x]`, auto-close parent as `[x]`; if any child is `[ ]`, parent must remain `[ ]`; if any child is `[_]` and none are `[ ]`, parent may become `[_]` but not `[x]`.
- Record milestone progress counts for successful commit/push batches when the repo uses notifications.
- Treat the main session as worker id `main-session` for integration claims, progress, and conflict cleanup.
  The main session may claim integration-ready DAG nodes under the active goal and may claim repair nodes that unblock merge/rebase conflicts from worker worktrees.
  Conflict cleanup must be explicit: identify both sides, preserve user/worker changes where possible, run validation, and checkpoint the consolidation only after the merged tree is coherent. Clear blockers created when worker worktrees or automation branches merge back to `main`.
- On success, checkpoint and push changes, then sync completion back to the main blueprint and today's todo.
- Worker success means `[_]`; master success means `[x]`.
- Treat incomplete completion-surface backfill as a hard failure (for example: stage blueprint updated but overall blueprint or today's todo not updated when required).
- A batch that closes items reconciles every required completion surface in the
  same batch, including `Overall Blueprint + Stage Blueprint + today's todo`
  when those surfaces exist. Code completion with stale completion docs creates
  a repair batch and fails the tick.
- On no-op completion, validate and then stop instead of inventing work.
- Enforce commit-surface filtering before commit:
  - hard-drop `.cron/`, `.ops/`, logs/state artifacts, generated todo files, and model binaries from staged set
  - hard-drop `spec/` and `tests/` from staged set
  - fail commit when `docs_count > code_count` or when `code_count == 0` and `docs_count > 0`
  - if a repo keeps runnable validation packages or executable scripts under `Docs/`, classify those paths as `code/evidence` instead of prose docs for commit hygiene
  - at minimum, treat paths like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` as `code/evidence`
- Enforce sync gate around push:
  - start-of-tick sync check: local authoritative repo must complete `fetch --prune` + `ff-only` sync and HEAD equality verification before any coding
  - pre-commit sync check: local authoritative repo must complete `fetch --prune` plus `ff-only` sync before checkpoint commit
  - post-push sync check: local authoritative repo must fast-forward to and match remote HEAD
  - dirty tracked changes, detached HEAD, non-fast-forward divergence, or network failure block the tick and its success state
  - never swallow sync errors with `|| true` on the success path
  - when blocked by local tracked changes, prefer a bounded `repo force sync` (`stash -u` -> sync -> `stash pop`) before escalating to manual intervention
- Enforce live claim hygiene:
  - claims are reservations, not proof of progress
  - remove claims for completed blueprint items
  - remove claims for open items whose worker pid/process is gone
  - keep claims for open items whose worker process is still live
  - detect active workers with self-match-safe patterns such as `[c]odex exec...`
  - append released claims to an audit ledger with timestamp, original claim time, item id, and worker id
  - run stale-claim pruning before sync and again after sync, so a dirty main checkout cannot trap stale reservations forever
- Enforce safe dirty-sync behavior:
  - if tracked dirty files exist and active workers are still running, write a clear `blocked_sync` state and leave the worktree untouched
  - if tracked dirty files exist and no worker is active, create an audit-named `git stash push -u`, then `fetch --prune` and `merge --ff-only`
  - after syncing, verify local HEAD equals upstream HEAD before spawning workers
  - never auto-apply a stash during the success path; stash-pop conflicts require explicit operator repair
  - repeated sync blocks caused by local tracked changes trigger an audited operator recovery path:
    `stash -u` -> `fetch --prune` plus `pull/rebase or ff-only merge` ->
    `stash pop`; a pop conflict stops automation until explicit resolution and
    one consolidation commit plus push
  - log every force-sync attempt and result
- For multi-worker mode, use a scheduler lock plus worker-specific locks.
- When lock files are managed with `flock`, treat lock-fd inheritance as a first-class failure mode:
  - close the held lock fd, for example with `9>&-`, before `tmux new-session`,
    `tmux new-window`, and `tmux respawn-pane`
  - keep workers on their own state files instead of sharing the scheduler state file
  - if the guard reports repeated "previous run still active" while no real scheduler is active, inspect inherited lock holders (for example `/proc/<pid>/fd/*`) and repair before continuing
  - repair a historical lock leaked into a long-lived `tmux` server by rotating
    the lock-path version or restarting the affected server or session
- Prefer split-lane DAG ownership over worker-side dependency throttling:
  - workers own `[ ]` implementation claims from the first-open layer/cluster in stable DAG/topological order, up to the user concurrency cap
  - the main session owns `[_]` integration closure, validation, dependency gating, and merge/conflict repair by default
  - no worker may claim outside the current ordered DAG claim frontier, but workers may produce provisional output for nodes whose dependencies are not yet integrated
- Add an integration batching lane:
  - maintain a queue of landed worker outputs with item id, dependencies, owned paths, changed files, diff bytes, and validation command hints
  - group non-conflicting landed outputs when the combined diff is <=256KiB
  - apply the group as one coherent integration batch, validate the combined tree once or with the smallest sufficient validator set, then close items in DAG order only after each item's gates pass
  - write `[x]` only for the longest dependency-ordered prefix whose gates pass
  - if a later item in the applied group passes code validation but an earlier dependency is not closable, leave the later item provisional in the todo/queue rather than checking it in the blueprint
  - report both worker saturation and integration throughput so operators can distinguish spawn underfill from master validation bottlenecks
- Worker batches may sync only `[_]` marks and evidence; only the integration
  owner may sync `[x]` marks after integrated validation.

### Cron Space Guard

Every generated execution cron must include a repo-local janitor script, for example `.cron/scripts/cron_space_guard.sh`, and call it from the top of the scheduler before any `tmux` or agent-runner launch.

Minimum behavior:
- determine the cron root from the script path, not from the caller's current directory
- cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, using a temp file plus atomic `mv`
- rotate or truncate scheduler redirection targets such as `keepalive.log` before appending more output
- clean old logs and stale workspaces before checking the cron-root budget
- verify live worker paths with self-match-safe process checks before deleting any automation repo or workspace
- return a distinct nonzero code for "budget exceeded" so the scheduler can exit without treating the tick as completed work
- keep all defaults overrideable via environment variables

### Cleanup Script

Requirements:
- Remove only the target repo's execution cron line.
- Be safe to run repeatedly.
- Leave a cleanup state/log artifact.
- Return success only when cron entry is confirmed removed (not just "script ran").

## Completion Gate

A blueprint item may be checked only when all required gates pass.

Minimum gate set:
- operable entry: the CLI, service, console, or UI entry works in its intended operating mode
- foundation completion: model or algorithm artifacts are downloaded and runnable; mock weights or fake inference paths each fail the gate
- feature implemented: input -> run -> result -> evidence path is real
- feature completion: expose a real API path, run a successful call, and verify output quality matches expected behavior
- algorithm complete: core data/model/scheduling/retrieval logic exists with real inputs/outputs
- validation evidenced: `Validation Log` records commands and results

Bootstrap and reporting rule:
- before the first cron tick, the authoritative blueprint checklist must exist and start with `[ ]` marks
- after each successful worker batch, the authoritative blueprint and today's todo must both reflect `[_]` state with worker evidence
- after each successful master integration batch, the authoritative blueprint and today's todo must both reflect `[x]` state with master validation evidence
- after repeated unresolved ticks for the same `[ ]` item (default >=5), the cron must auto-split that item into child checklist items and report the split explicitly

Cleanup hard-gate rule:
- Cron cleanup must not be triggered by blueprint-only signal.
- Require at least these signals at the same tick: blueprint `[ ]` count=0 + blueprint `[_]` count=0 + latest todo `Unfinished=0` + no active automation agent-runner process + no pending checkpoint files.
- Parsers may accept the legacy display variant `Unfinished = 0`; generators emit
  the canonical `Unfinished=0` form.
- Require current-tick validation to pass before cleanup.
- Set final state to `completed` only after cleanup script succeeds and crontab no longer contains the target guard line.

Do not mark items done for:
- doc-only work
- placeholder handlers
- fake success responses
- mocked model downloads or mocked inference/evaluation paths
- schema without runnable path
- tests without real implementation

Do not commit batch outputs for:
- test-only changes (`spec/`, `tests/`)
- validation logs / research handoff docs generated by cron loops
- todo snapshots and cron state logs

## Batch Design Rules

- Prefer the repository's own layer/order semantics.
- If the blueprint is layered, execute only the finest still-open layer first.
- Never close upper-layer items while lower-layer items remain open.
- Stay inside one cluster per batch.
- For fragmented file checklist items, merge nearby same-directory files into one bounded batch (<=100KB combined) to avoid over-fragmented single-file ticks.
- Stop after 6-8 coherent items at most.
- If the blueprint is already fully checked, validate the current tree and exit cleanly without fabricating more work.
- In multi-worker mode, keep workers claiming from the ordered DAG queue and let integration happen through git rebase/push plus authoritative repo re-sync, not by letting workers close blueprint/todo state directly.
- Scale worker count to the user-requested concurrency cap from the DAG claim frontier. If dependencies or path conflicts exist, workers may still prepare provisional implementation output; the main session must merge, validate, and close those nodes only when the DAG dependency constraints are satisfied.
- For landed worker outputs with no path conflicts and combined diff <=256KiB, prefer batch apply + combined validation over one-worker-at-a-time master validation. Blueprint closure remains dependency ordered and may be a prefix of the applied batch.

## Looper Embed Rules

When embedded in `looper-cron-builder`, execution may run only inside an active
`ResourceLease` with a `ParentLeaseRef`. Nested execution attempts can create
child implementation candidates, repair child items, or validation-focused
patches, but they cannot write `[x]` or escape parent lease budget.

The parent looper attempt owns final reward classification, no-reward
accounting, and ROI. Execution outputs remain provisional until the master lane
integrates them in DAG order and validates the authoritative checkout.

Nested execution should emit `looper_log` refs when implementation attempts
produce instrument evidence: mismatched batch grain, missing validator,
worker/root confusion, integration bottleneck, route mismatch, guard friction,
or scaffold/tool weakness.
The log should separate target feedback from instrument feedback, distinguishing
implementation difficulty from execution-instrument defects.

## Validation

Use the smallest real validation commands the repo supports.

Examples:
- Rust/Tauri repos: `cargo check`, `cargo test`
- Python repos: `uv sync --extra dev`, `uv run pytest -q tests`
- Node repos: `npm`/`pnpm` install plus actual test/build commands

## Output Discipline

- Begin with the requested blueprint, checklist state, implementation result,
  gate decision, evidence, or action.
- Give each sentence one fact, condition, decision, action, result, or constraint.
- State supported claims directly. Omit unsupported connective claims and
  decorative inference.
- When unresolved uncertainty changes correctness, safety, legality, a gate
  decision, or the available action, state the exact unknown, condition, and
  consequence.
- Include a boundary only when it changes correctness, safety, legality, or the
  available action; name the exact constraint and permitted path.
- Report validation as result, evidence, and consequence. Omit process
  diaries, routine check narration, previews, restatements, recaps, and generic
  closing offers.
- Preserve exact paths, commands, identifiers, states, counts, thresholds,
  evidence, user-required sections, and safety gates.
- When the user supplies a target length, keep the delivered output within plus
  or minus 10 percent. With no target, use the shortest complete output
  supported by the artifacts and evidence.
- Before delivery, silently scan prose word by word for stock meta-talk,
  defensive comparison frames, repeated qualifications, vague fillers, empty
  placeholders, and generic recommendation lead-ins. Replace them with facts or
  actions while preserving technical negation and exact strings.

## Local References

Read these only when needed:
- `references/execution-pattern.md` for the pattern and local repo examples
- `references/gate-rules.md` for completion gate and cleanup rules
