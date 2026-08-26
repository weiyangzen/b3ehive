# Agent 平台兼容性

[English](agent-platforms.md)

b3ehive skills 使用可移植的 `SKILL.md` 目录约定。同一组 skill 目录可以安装到 Codex、Claude Code、Cursor、Grok Build、opencode、OpenClaw 和 Hermes，不需要为不同平台维护多份 skill 正文。

## 支持目标

| Target | User install root | Project install root | Invocation |
|---|---|---|---|
| Codex | `~/.codex/skills/<skill>/SKILL.md` | `.codex/skills/<skill>/SKILL.md` | 在 prompt 中提到 skill 名称，例如 `Use execution-cron-builder ...` |
| Claude Code | `~/.claude/skills/<skill>/SKILL.md` | `.claude/skills/<skill>/SKILL.md` | 使用 `/skill-name` 或在 prompt 中提到 skill 名称 |
| Cursor | `~/.cursor/skills/<skill>/SKILL.md` | `.cursor/skills/<skill>/SKILL.md` | 在 Cursor agent thread 中提到 skill 名称 |
| Grok Build | `~/.grok/skills/<skill>/SKILL.md` | `.grok/skills/<skill>/SKILL.md` | 提到 skill 名称，或使用 `/skill-name` |
| opencode | `~/.config/opencode/skills/<skill>/SKILL.md` | `.opencode/skills/<skill>/SKILL.md` | 在 prompt 中提到 skill 名称，或引用 skill path |
| OpenClaw | `~/.openclaw/skills/<skill>/SKILL.md` | `skills/<skill>/SKILL.md` | `openclaw skills info <skill>` 或在 prompt 中提到 skill 名称 |
| Hermes | `~/.hermes/skills/<skill>/SKILL.md` | `skills/<skill>/SKILL.md` | 在 Hermes chat 中提到 skill 名称 |

opencode 不需要单独的 skill body。它使用同样的 `SKILL.md` 目录形态，并识别 `name`、`description` 等 frontmatter。主要差异是 discovery location。

OpenClaw 和 Hermes 也属于 AgentSkills / `SKILL.md` 家族。OpenClaw 当前 parser 更保守：frontmatter 保持简单，使用单行 `name` 和 `description`，更复杂的平台数据放到 package/config 文件或简单 JSON-valued `metadata` 中。Hermes 支持 user skills、repository skills，以及需要时的 `metadata.hermes.*`。

五个可移植 skill 目录是：

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

Cursor 和 Grok Build 复用同一套 `name` / `description` frontmatter。Grok Build
在 `GROK_CURSOR_SKILLS_ENABLED` 开启时也会读取 Cursor skill 目录，但 b3ehive
仍安装到 `~/.grok/skills`，让 Grok 目标可检查。无头 Grok worker 必须带
`--always-approve`；`grok -p`、`grok agent stdio` 和 `grok agent serve` 默认
是 ask，除非设置该 flag 或 `_meta.yoloMode`。

仓库根目录的 `SKILL.md` 是 b3ehive skill index。实际安装到 Codex、Claude Code、
Cursor、Grok Build、opencode、OpenClaw 和 Hermes 的是这五个 skill 目录。

## Runner Contract

Cron-oriented skills 应该用通用的 agent runner 描述 worker 执行，再在安装或仓库 bootstrap 时选择具体平台命令。

默认 Codex 执行 transport：

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
# 轮询 `capture-pane -p -J`，直到 claim 专属的末尾完整性 token 出现在当前
# composer；超时则失败，不能提交截断输入。确认后只提交一次。
tmux -S "{task_root}/tmux.sock" send-keys -t "{session}" C-m
```

每个 Codex claim 都必须独占 tmux server/socket/session、interactive Codex
OS process tree、可写 `CODEX_HOME`、thread 和 active goal。生成的 controller
只有在这些身份全部认证后才能把 lane 计为 live。禁止 `codex app-server`、
controller 管理的 JSON-RPC、共享 Codex daemon、`codex exec` 以及不经过 tmux
的 Codex，且不得 fallback。本仓库不预设 Codex model、provider、effort、
service tier 或 worker count；优先使用目标仓库或 operator 的显式策略，否则
使用本机 Codex 默认值并记录实际 route。

默认 Claude Code runner：

```bash
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
```

默认 Cursor runner：

```bash
python3 "{b3ehive_root}/scripts/run_cursor_agent.py" \
  --workspace "{workspace}" --prompt-file "{prompt_file}" > "{output_file}"
```

默认 Grok Build runner：

```bash
GROK_TELEMETRY_ENABLED=0 GROK_TELEMETRY_TRACE_UPLOAD=0 \
  grok --always-approve --cwd "{workspace}" --prompt-file "{prompt_file}" \
  ${GROK_MODEL:+-m "$GROK_MODEL"} ${GROK_EFFORT:+--effort "$GROK_EFFORT"} \
  > "{output_file}"
```

默认 opencode runner：

```bash
opencode run --dir "{workspace}" ${OPENCODE_MODEL:+--model "$OPENCODE_MODEL"} \
  ${OPENCODE_VARIANT:+--variant "$OPENCODE_VARIANT"} \
  ${OPENCODE_AGENT:+--agent "$OPENCODE_AGENT"} \
  < "{prompt_file}" > "{output_file}"
```

默认 OpenClaw runner：

```bash
openclaw agent --local --message "$(cat "{prompt_file}")" > "{output_file}"
```

默认 Hermes runner：

```bash
hermes chat --toolsets "${HERMES_TOOLSETS:-skills,terminal}" \
  ${HERMES_MODEL:+--model "$HERMES_MODEL"} \
  ${HERMES_SKILLS:+-s "$HERMES_SKILLS"} \
  -q "$(cat "{prompt_file}")" > "{output_file}"
```

生成的 cron guards 可以暴露这些设置：

| Shared setting | Codex setting | Claude Code setting | Cursor setting | Grok Build setting | opencode setting | OpenClaw setting | Hermes setting |
|---|---|---|---|---|---|---|---|
| `B3EHIVE_AGENT_PLATFORM=codex|claude|cursor|grok|opencode|openclaw|hermes` | `CODEX_MODEL` | `CLAUDE_MODEL` | `CURSOR_API_KEY` | `GROK_MODEL` | `OPENCODE_MODEL` | `OPENCLAW_AGENT` | `HERMES_MODEL` |
| `B3EHIVE_AGENT_RUNNER` | `CODEX_REASONING_EFFORT` | `CLAUDE_EFFORT` | `CURSOR_MODEL` | `GROK_EFFORT` | `OPENCODE_VARIANT` | `OPENCLAW_THINKING` | `HERMES_TOOLSETS` |
| `B3EHIVE_AGENT_WORKSPACE` | `CODEX_SERVICE_TIER` | `CLAUDE_PERMISSION_MODE` | | | `OPENCODE_AGENT` | `OPENCLAW_PROFILE` | `HERMES_SKILLS` |

当用户显式设置 `B3EHIVE_AGENT_RUNNER` 时，非 Codex 平台应把它作为 authoritative command template，并在 validate-only 输出中打印。Codex 只能用它定制 TUI 参数，不能绕过 task-local tmux + interactive TUI + `/goal` transport。

## Skill Authoring Rules

- 每个 skill 保持为一个目录，包含 `SKILL.md`，以及可选的 `references/`、`scripts/`、`templates/`、`agents/`。
- YAML frontmatter 至少包含 `name` 和 `description`；Codex、Claude Code、Cursor、Grok Build、opencode、OpenClaw 和 Hermes 都可以复用这个形态。
- frontmatter 保持可移植。避免 OpenClaw conservative parser 可能跳过的嵌套 YAML。
- 平台差异放在短兼容性段落、references 或 generated config 中。除非 workflow 真正不同，不要 fork 主说明。
- 通用 orchestration 文案使用 "agent runner"。Codex 模板必须使用 task-local tmux 中的 interactive `codex` TUI；其他平台模板可以使用 `claude -p`、`scripts/run_cursor_agent.py`、`grok --always-approve`、`opencode run`、`openclaw agent` 或 `hermes chat`。
- cleanup gates 应检查当前 selected runner 的 live process，而不是只查 `codex` process。
