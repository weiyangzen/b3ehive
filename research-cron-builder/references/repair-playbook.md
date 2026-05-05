# Repair Playbook

## When the checklist is wrong

1. Stop the repo's workers.
2. Regenerate `Docs/researches/blueprint_checklist.md`.
3. Reconcile `[x]` marks by scanning existing research docs.
4. Regenerate today's todo.
5. Confirm counts before resuming workers.

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

Then seed `.cron/research_guard.kimi_key_index` to the first usable slot.
