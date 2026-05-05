# Execution Cron Pattern

## Local reference repositories

- `/home/sansha/Github/clawdb/.ops/`
- `/home/sansha/Github/celviz/.ops/`
- `/home/sansha/Github/cvbackbone/.ops/`

## Best-practice pattern

1. Choose one blueprint file.
2. If the blueprint is prose-first, generate an authoritative execution checklist section into that same blueprint.
3. Seed the execution checklist with all `[ ]` marks before the first cron tick.
4. Generate a daily todo from that authoritative checklist section.
5. Use an isolated automation repo when the main repo may be dirty.
6. Run `codex exec --model gpt-5.4 -c model_reasoning_effort="xhigh"` in bounded clusters.
7. Enforce strict layer gate: only work on the finest still-open layer; do not close upper layers while lower layers are open.
8. Validate honestly.
9. Commit/push only real work.
10. Apply commit hygiene before every checkpoint:
   - never commit `.cron/`, logs, generated todos, or tests/spec
   - never commit model binaries; commit reproducible download scripts instead
   - docs cannot outnumber code changes in a batch, and docs-only batch commits are invalid
   - runnable validation packages/scripts stored under `Docs/` count as `code/evidence`, not prose docs
   - patterns like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` count as `code/evidence` when they hold runnable validation logic
11. Apply sync-first push gate:
   - tick start: development machine must sync first (`fetch --prune + ff-only`) and local HEAD must equal remote tracking HEAD before coding
   - pre-commit: local authoritative repo must be syncable with `fetch + ff-only`
   - post-push: local authoritative repo must be synced and verified equal to remote HEAD
   - any sync failure blocks success and must be reported
12. Apply lock hygiene when the guard holds `flock` locks and also uses `tmux`:
   - close the held lock fd before `tmux new-session`, `tmux new-window`, and `tmux respawn-pane` so the `tmux` server cannot inherit and pin the lock
   - keep scheduler/global state separate from worker/slot state files
   - if a stale `tmux` server already inherited the lock, rotate the lock-file version or kill/restart that server before the next tick
13. Sync the main blueprint and today's todo after each successful batch.
14. Enforce documentation reconciliation after every completion backfill:
   - if a batch closes checklist items, it must update every required status surface in the same batch (for example: authoritative blueprint + stage blueprint mirror + today's todo)
   - todo entries must point to stable repository paths (never automation clone absolute paths) so diffs stay reviewable and do not leak local runtime paths
   - treat "code done but blueprint/todo stale" as an execution failure, not a cosmetic issue
15. If the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items, regenerate today's todo, and notify the human clearly.
16. Remove cron when complete.

## Two-worker pattern

Use this only when one worker is leaving material throughput on the table and the repository can be split into disjoint write lanes.

- Keep concurrency at `2`, not higher, unless the repo already has proven lane partitioning.
- Give each worker its own automation clone:
  - `.cron/automation_repo`
  - `.cron/automation_repo_slot2`
- Use a scheduler lock to spawn/respawn workers, and worker-specific locks so the same slot never overlaps with itself.
- When spawning workers from a locked scheduler, close the scheduler lock fd on every `tmux` launch/respawn path (for example `9>&-`) so the lock dies with the scheduler instead of living inside the `tmux` server.
- Keep the scheduler's state file authoritative; workers should write only to slot-specific state files.
- Force an explicit ownership split. Example:
  - `worker-1`: `core/ services/ ops/ data/` plus integration closure
  - `worker-2`: `tauri/` and UI assets
- Require every worker batch to start with `fetch + pull --ff-only` or `fetch + rebase`.
- Require every worker push to rebase and resolve only inside that worker's owned paths.
- Keep blueprint/todo mutation centralized to one integration lane after honest validation on the combined tree.
- Re-sync or mirror the authoritative local repo after successful worker pushes so future blueprint seeding does not revert checkmarks and today's todo stays current.
- Track repeated unresolved checklist items; if one item survives >=5 ticks unresolved, split it into child checklist items and keep execution on that branch until children close.

## Blueprint surface styles

### Authoritative checklist in blueprint
Preferred for new execution crons.
- keep the checklist in the same blueprint file that defines the work
- initialize it with all `[ ]` marks before first execution
- generate todos from that section only
- write completed `[x]` marks back to that same blueprint after real validation

### Legacy private mirror
Allowed only as a convenience mirror after the authoritative blueprint checklist already exists.
- never treat the mirror as a second requirement source
- never let the mirror become the only place where completion is reported

## Typical runtime files

- `.cron/<project>_guard.state`
- `.cron/<project>_guard.log`
- `.cron/<project>_guard.pending_checkpoint`
- `.cron/<project>_guard.last_message.txt`
- `.cron/<project>_guard.progress`

## Common failure modes

- multiple requirement sources leaking into the prompt
- dirty automation repo blocking every tick
- local-only docs/tests accidentally being committed
- `.cron/`/log/state artifacts accidentally being committed
- docs-only commits or docs volume outgrowing code volume
- historical tracked local-only files not being cleaned, causing repeated accidental staging
- starting implementation while local development machine HEAD is stale versus remote
- push succeeded but local authoritative repo stayed stale due swallowed sync failure
- `tmux` server inherited the scheduler `flock` fd, so future ticks report "previous run still active" even though no real scheduler is running
- claiming model/algorithm completion with mock downloads or fake inference paths
- checking upper-layer items while finer layers still contain unchecked items
- completion never cleaning up because the guard only validates and never exits
- repeated empty no-op runs after blueprint completion
- repeated real commits with zero checklist movement because the cron keeps hammering one non-closable cluster
- repeated unresolved checklist items without automatic split into executable child items
- worker clones pushing code while the authoritative local repo blueprint stays stale, causing later seed steps to roll completed checkmarks back
- worker clones updating the automation repo todo while the main repo todo stays stale, leaving humans with the wrong completion picture
- todo snapshots embedding `.cron/automation_repo*` absolute paths, causing noisy diffs and misleading progress references
- implementation merged while blueprint/todo completion surfaces stayed stale, creating false "not done" reports
- allowing both workers to edit root manifests or blueprint files directly, creating avoidable merge conflicts

## Lock leak recovery

- Symptom: repeated `skip: previous run still active` with no corresponding live scheduler workload.
- First confirm the lock holder:
  - inspect `/proc/<pid>/fd/*` for the lock path
  - if the holder is a long-lived `tmux` server or unrelated child, treat it as leaked
- Recovery sequence:
  - stop the affected session/server
  - remove stale lock files only after the holder is gone
  - if needed, rotate to a new versioned lock path so old inherited fds cannot block the new scheduler
  - relaunch the scheduler and verify the next tick acquires the lock normally
