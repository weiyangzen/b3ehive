# Optimization Cron Repair Playbook

## When the AR blueprint item grain is bad

1. Stop all workers.
2. Regenerate the AR blueprint with a finer or cleaner item grain.
3. Preserve `[x]` only for items that still have one valid matching doc.
4. Regenerate today's todo.
5. Resume workers.

## When a section stalls

Check:
- whether the section has too many heterogeneous items
- whether the prompt allows the worker to write outside its owned scope
- whether output docs are too broad and therefore blocked from completion

If needed:
- split the section
- reduce per-run item count
- rerun only the affected worker lane

## When cleanup does not happen

Check:
- the guard sees `open=0`
- no worker session is still alive
- the cleanup script matches the installed cron marker
- the cleanup script removes both crontab entry and tmux sessions
