# Completion Gate Rules

## Never mark done without all of these

- operable entry exists and is runnable
- model/algorithm foundations are real: artifacts are truly downloaded and can run end-to-end (no mock weights, no fake inference path)
- end-to-end feature path is real
- API closure is real when relevant: endpoint exists, request succeeds, and effect/quality check matches expectation
- underlying algorithm or state model is complete enough to support the feature
- validation commands passed and were logged

## Strict layer gate rule

When the blueprint has explicit layers, enforce strict bottom-up closure:
- only the finest still-open layer is executable for new checkmarks
- if any lower-layer item is still `[ ]`, upper-layer items must remain `[ ]`
- if a tick detects upper-layer `[x]` while lower layers remain open, auto-reset those upper-layer `[x]` items back to `[ ]` in the authoritative blueprint, then continue from the lower layer
- emit an explicit autoclear report with violating layer counts and cleared item counts
- block only when auto-reset is disabled or re-validation still fails after autoclear

## Local-only artifact rule

For execution cron repos, decide explicitly which artifacts remain local-only.
Typical examples:
- `.cron/`
- `*.log`
- `Docs/todos_*.md`
- `.venv/`
- `tests/`
- `spec/`
- `target/`
- `node_modules/`

Do not silently commit these unless the repo's policy explicitly requires it.

## Commit hygiene gate rule

- Execution batches are code-first: reject docs-only commits.
- In one batch commit, changed docs files must not exceed changed code files.
- If a repository stores runnable validation packages or executable scripts under docs-like folders, classify those paths as `code/evidence` instead of prose docs for commit hygiene counting.
- At minimum, treat patterns like `Docs/Stage3IOSPathValidation/**` and `Docs/scripts/*.sh` as `code/evidence` when they contain runnable validation logic.
- Never stage or commit tests in execution batches (`tests/**`, `test/**`, `spec/**`, `*_test.*`, `test_*.py`).
- Never stage or commit runtime artifacts (`.cron/**`, logs, state files, generated todo snapshots).
- If forbidden artifacts were already tracked by git, clean them with `git rm --cached ...` and add ignore/exclude entries before continuing cron.

## Sync-first push gate rule

- At execution tick start, development machine must pass `fetch --prune + merge --ff-only` sync and local HEAD must match remote tracking HEAD before any coding.
- Before each checkpoint commit, local authoritative repo must pass `fetch + merge --ff-only` sync.
- After each successful push, run local authoritative sync again and verify local HEAD equals remote tracking HEAD.
- If local repo has dirty tracked files, detached HEAD, non-fast-forward divergence, or sync/network failure: block the tick and surface a clear error.
- Do not treat "push succeeded but local sync failed" as success.

## Lock hygiene rule

- If the guard uses `flock` and also spawns `tmux`, explicitly close the held lock fd before every `tmux new-session`, `tmux new-window`, and `tmux respawn-pane`.
- Do not let workers reuse the scheduler's state file; use slot-specific state files so no-focus or failed workers cannot overwrite scheduler truth.
- If future ticks report "previous run still active" but there is no live scheduler workload, inspect `/proc/<pid>/fd/*` for inherited lock holders before deleting lock files.
- If the inherited holder is a long-lived `tmux` server, restart that server/session or rotate to a new versioned lock path before resuming cron.

## Bootstrap and backfill rule

- before the first cron tick, initialize the authoritative execution checklist in the blueprint with all `[ ]` marks
- daily todos must derive from that authoritative blueprint checklist
- after each successful batch, backfill the authoritative blueprint checkmarks and refresh today's todo in the main repo
- if the same `[ ]` item remains unresolved for repeated ticks (default >=5), auto-split it into child checklist items and report the split clearly to the human
- if all child checklist items become `[x]`, parent checklist item must auto-close to `[x]`; if any child is `[ ]`, parent must remain `[ ]`

## Documentation reconciliation gate

- Completion is not accepted until all required documentation surfaces are reconciled in the same batch.
- If a repo requires multiple surfaces (for example `Overall Blueprint + Stage Blueprint + today's todo`), a partial update is invalid.
- Daily todo entries must reference stable repository-relative blueprint paths, not automation clone absolute paths.
- If code implementation advances but completion surfaces remain stale, mark the tick failed and force a backfill repair batch.

## Cleanup rule

When the blueprint is fully checked and validation passes:
- require hard cleanup signals before cleanup:
  - authoritative blueprint unchecked count is zero
  - latest todo snapshot shows `Unfinished = 0`
  - no active `codex` execution in automation repos
  - no pending checkpoint artifacts remain
- run the cleanup script
- verify cron line was actually removed from crontab
- leave final state as `completed` or `paused` only after cleanup verification
- do not continue waking the repo for empty no-op batches

## Parallel lane rule

When execution uses 2 workers:
- only one lane may close blueprint/todo checkmarks
- the other lane should land code plus validation evidence only
- both lanes must sync from origin before work and rebase before push
- never allow both lanes to own the same path family
