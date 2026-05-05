# Research Cron Pattern

## Local reference repositories

- `/home/sansha/Github/codex/.ops/`
- `/home/sansha/Github/openviking/.ops/`
- `/home/sansha/Github/pi-mono/.ops/`

## Best-practice pattern

1. Generate a repository-derived checklist.
2. Generate a daily todo from that checklist.
3. Start a guard that:
   - creates parallel `tmux` workers
   - claims DIR/FILE work under lock files
   - calls `kimi --print --yolo`
   - verifies output documents are non-empty
   - reconciles checklist marks from output docs
   - checkpoints progress locally
4. Remove cron on completion.

## Code-only scope rule

Use code-only scope by default for repositories with heavy docs or generated content. Include:
- source files
- config files
- scripts
- tests

Exclude by default:
- docs and markdown
- `Docs/researches/`
- caches
- build output
- dependency trees

## Typical runtime files

- `.cron/research_guard.state`
- `.cron/research_guard.log`
- `.cron/research_guard.block_count`
- `.cron/research_claims/*.claim`
- `.cron/research_guard.kimi_key_index`
- `.cron/research_guard.progress`

## Typical cron shape

- daily todo generation: once per day shortly after midnight
- guard wake-up: every 5 minutes

## Common failure modes

- `kimi` quota/auth failures causing `exec_failed`
- duplicate work due to missing claim locks
- empty output docs accepted as success
- checklist corruption from non-atomic writes
- completed repos left running because cleanup never fires
