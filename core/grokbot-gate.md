## Grokbot Gate

Grokbot build of `{base}`, b3ehive {version}.
This section overrides every runner, platform, transport, and subagent rule in
this skill and in its references.

Load:

- Only grokbot loads this skill. Grokbot installs it with the command below
  and names the subagent runtime explicitly:
  `unzip {name}-skill.zip -d ~/.claude/skills/`
- Any other host stops here and loads nothing from this directory: Claude Code,
  a `claude` subagent that grokbot started, Codex, Cursor, Grok Build without
  grokbot, opencode, OpenClaw, and Hermes. Those hosts use the base skill
  `{base}` instead.

Subagent runtime:

- Every subagent call uses only `claude --dangerously-skip-permissions` as its
  agent runtime. This covers workers, reviewers, verifiers, voters, repair
  generations, nested runs, and in-session subagents.
- Runner template, also the value of `B3EHIVE_AGENT_RUNNER`, with
  `B3EHIVE_AGENT_PLATFORM=claude`:

  ```bash
  claude -p --dangerously-skip-permissions \
    --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
    --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
  ```

- No other runtime: no Grok subagent or task tool, no `grok`, `codex`, Cursor,
  opencode, OpenClaw, or Hermes worker, no Codex TUI transport, and no
  `--permission-mode` flag. Where the body or a reference names another runner,
  read this runtime.
- A runner that does not start with `claude -p --dangerously-skip-permissions`
  fails closed with its value. A missing `claude` binary stops the run with
  `user_action_required`; there is no fallback.
- The flag removes every permission check, so the task root is the only fence.
  `--add-dir` names the claim workspace only, never the canonical checkout or
  `$HOME`. Each subagent still counts against every cap and lease.
- Each subagent prompt states its role and tells it not to load any
  `grokbot-*` skill.
- Validate-only output prints `platform=claude`,
  `runtime=claude --dangerously-skip-permissions`, and the resolved runner.
