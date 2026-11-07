## Agent Runner

This is the grokbot build. Generated cron code supports one agent runtime:
`claude --dangerously-skip-permissions`. Every worker, reviewer, verifier,
voter, repair generation, nested run, and in-session subagent uses it.

- `B3EHIVE_AGENT_PLATFORM` is fixed to `claude`. Any other value, `auto`
  included, fails closed with its value.
- `B3EHIVE_AGENT_RUNNER`, when set, must start with
  `claude -p --dangerously-skip-permissions`; otherwise the guard fails closed
  and launches nothing.
- A missing `claude` binary writes state `user_action_required` and launches
  nothing. There is no fallback runtime.
- Each worker generation owns one `claude` process tree, one task root, and one
  workspace. `--add-dir` names that workspace only, never the canonical
  checkout or `$HOME`.
- Nested agents run only when the specification admits them; each child is an
  independent `claude --dangerously-skip-permissions` execution under the same
  global caps.

Command template:

```bash
claude -p --dangerously-skip-permissions \
  --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"
```

Run the command with `$WORKER_REPO` as its working directory, inside the
worker's tmux session when the substrate is `cron+tmux`.

Validate-only output must print `platform=claude`,
`runtime=claude --dangerously-skip-permissions`, and the resolved runner.

