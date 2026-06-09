# Repair Playbook

## When the checklist is wrong

1. Stop the repo's workers.
2. Regenerate `Docs/researches/blueprint_checklist.md`.
3. Reconcile `[_]` marks from existing source-tree-aligned `*_research.md`
   files; do not require worker self-test JSON.
4. Reconcile `[x]` marks only from artifacts that pass master validation.
5. Regenerate today's todo.
6. Confirm counts before resuming workers.

## When completed repos keep running

Check:
- whether `AUTO_CLEANUP_ON_COMPLETE` is enabled
- whether the guard can actually see `open=0`
- whether the cleanup script matches the installed cron lines
- whether the completion branch sets `completed` instead of `idle_waiting`

## When key rotation is flaky

Probe all keys outside the main worker loop.
Record:
- usable keys
- unusable keys
- first usable index

Then seed `.cron/research_guard.provider_key_index` or the selected provider's
equivalent key cursor to the first usable slot.
