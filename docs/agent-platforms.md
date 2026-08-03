# Agent Platform Compatibility

[中文](agent-platforms.zh-CN.md)

b3ehive skills use the portable `SKILL.md` directory contract. The same skill
directories can be installed for Codex, Claude Code, opencode, OpenClaw, and Hermes without
maintaining separate copies of the skill body.

## Supported Targets

| Target | User install root | Project install root | Invocation |
|---|---|---|---|
| Codex | `~/.codex/skills/<skill>/SKILL.md` | `.codex/skills/<skill>/SKILL.md` | Mention the skill by name, for example `Use execution-cron-builder ...` |
| Claude Code | `~/.claude/skills/<skill>/SKILL.md` | `.claude/skills/<skill>/SKILL.md` | Invoke `/skill-name` or mention the skill by name |
| opencode | `~/.config/opencode/skills/<skill>/SKILL.md` | `.opencode/skills/<skill>/SKILL.md` | Mention the skill by name or reference its skill path in a prompt |
| OpenClaw | `~/.openclaw/skills/<skill>/SKILL.md` | `skills/<skill>/SKILL.md` | `openclaw skills info <skill>` or mention the skill by name |
| Hermes | `~/.hermes/skills/<skill>/SKILL.md` | `skills/<skill>/SKILL.md` | Mention the skill by name in Hermes chat |

opencode does not require a different skill body for this repository. It uses
the same `SKILL.md` directory shape and recognizes frontmatter such as `name`
and `description`. Its main difference is discovery location. It also reads
Claude-style skill locations, but b3ehive installs to opencode's native paths so
the target is explicit and inspectable.

OpenClaw and Hermes are also in the AgentSkills/`SKILL.md` family. OpenClaw's
current parser is conservative: keep frontmatter simple with single-line
`name` and `description`, and put richer platform data in package/config files
or simple JSON-valued `metadata` when needed. Hermes supports user skills under
`~/.hermes/skills/`, tap/repository skills under `skills/<skill>/SKILL.md`, and
Hermes-specific metadata under `metadata.hermes.*` when a skill needs it.

The five portable skill directories are:

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

The repository root `SKILL.md` is the b3ehive skill index. Install the five skill
directories for Codex, Claude Code, opencode, OpenClaw, and Hermes.

## Runner Contract

Cron-oriented skills should describe worker execution in terms of an agent
runner, then select a platform command at installation or repository bootstrap
time.

Default Codex execution transport:

```bash
codex_argv=(codex -C "{workspace}" -c features.goals=true --no-alt-screen)
[[ -n "${CODEX_MODEL:-}" ]] && codex_argv+=(-m "$CODEX_MODEL")
[[ -n "${CODEX_REASONING_EFFORT:-}" ]] && \
  codex_argv+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
[[ -n "${CODEX_SERVICE_TIER:-}" ]] && \
  codex_argv+=(-c "service_tier=$CODEX_SERVICE_TIER")
tmux -S "{task_root}/tmux.sock" -f /dev/null new-session -d \
  -s "{session}" -c "{workspace}" \
  env CODEX_HOME="{task_root}/codex-home" "${codex_argv[@]}"
tmux -S "{task_root}/tmux.sock" set-buffer -b goal \
  "/goal {goal} Integrity token: {claim_specific_completion_token}"
tmux -S "{task_root}/tmux.sock" paste-buffer -b goal -t "{session}" -d
# Poll `capture-pane -p -J` until the final integrity token is visible in the
# active composer. On timeout, fail without submitting partial input.
tmux -S "{task_root}/tmux.sock" send-keys -t "{session}" C-m
```

Every Codex claim owns a separate tmux server/socket/session, interactive Codex
OS process tree, writable `CODEX_HOME`, thread, and active goal. Generated
controllers must authenticate all of those identities before counting the lane
as live. `codex app-server`, controller-managed JSON-RPC, shared Codex daemons,
`codex exec`, and Codex without tmux are forbidden with no fallback. This
repository does not prescribe a Codex model, provider, effort, service tier, or
worker count; explicit target-repository/operator policy wins, otherwise the
installed Codex defaults are used and the resolved route is recorded.

Default Claude Code runner:

```bash
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
```

Default opencode runner:

```bash
opencode run --dir "{workspace}" ${OPENCODE_MODEL:+--model "$OPENCODE_MODEL"} \
  ${OPENCODE_VARIANT:+--variant "$OPENCODE_VARIANT"} \
  ${OPENCODE_AGENT:+--agent "$OPENCODE_AGENT"} \
  < "{prompt_file}" > "{output_file}"
```

Default OpenClaw runner:

```bash
openclaw agent --local --message "$(cat "{prompt_file}")" > "{output_file}"
```

Default Hermes runner:

```bash
hermes chat --toolsets "${HERMES_TOOLSETS:-skills,terminal}" \
  ${HERMES_MODEL:+--model "$HERMES_MODEL"} \
  ${HERMES_SKILLS:+-s "$HERMES_SKILLS"} \
  -q "$(cat "{prompt_file}")" > "{output_file}"
```

Generated cron guards may expose these settings:

| Shared setting | Codex setting | Claude Code setting | opencode setting | OpenClaw setting | Hermes setting |
|---|---|---|---|---|---|
| `B3EHIVE_AGENT_PLATFORM=codex|claude|opencode|openclaw|hermes` | `CODEX_MODEL` | `CLAUDE_MODEL` | `OPENCODE_MODEL` | `OPENCLAW_AGENT` | `HERMES_MODEL` |
| `B3EHIVE_AGENT_RUNNER` | `CODEX_REASONING_EFFORT` | `CLAUDE_EFFORT` | `OPENCODE_VARIANT` | `OPENCLAW_THINKING` | `HERMES_TOOLSETS` |
| `B3EHIVE_AGENT_WORKSPACE` | `CODEX_SERVICE_TIER` | `CLAUDE_PERMISSION_MODE` | `OPENCODE_AGENT` | `OPENCLAW_PROFILE` | `HERMES_SKILLS` |

When a user explicitly sets `B3EHIVE_AGENT_RUNNER`, generated cron code should
use it as the authoritative command template for non-Codex platforms and print
it in validate-only output. For Codex it may customize TUI arguments but cannot
bypass the required task-local tmux + interactive TUI + `/goal` transport.

## Skill Authoring Rules

- Keep each skill as a directory containing `SKILL.md` plus optional
  `references/`, `scripts/`, `templates/`, and `agents/` files.
- Keep YAML frontmatter with at least `name` and `description`; Codex,
  Claude Code, opencode, OpenClaw, and Hermes can discover or reuse that shape.
- Keep frontmatter portable. Avoid nested YAML that OpenClaw's conservative
  parser may skip; use package metadata or documented single-line metadata
  fields for platform-specific data.
- Keep platform-specific details in short compatibility sections, references,
  or generated config. Do not fork the main instructions unless the workflow
  truly differs.
- Use "agent runner" for generic orchestration text. Codex templates use the
  interactive `codex` TUI in task-local tmux; other platform templates may use
  `claude -p`, `opencode run`, `openclaw agent`, or `hermes chat`.
- For cleanup gates, check for a live process matching the selected runner,
  not only for a `codex` process.
