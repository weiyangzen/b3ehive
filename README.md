# b3ehive

[中文](README.zh-CN.md)

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://github.com/openai/codex)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![opencode Skill](https://img.shields.io/badge/opencode-Skill-green)](https://opencode.ai)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-purple)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

b3ehive provides five portable swarm skills for bounded agent work. Each skill
defines its inputs, worker organization, validation boundary, evidence, and
cleanup rule. The same skill directories support Codex, Claude Code, opencode,
OpenClaw, and Hermes.

Its design draws on the Feynman Technique: clear explanations, inspectable
steps, and repeatable evidence expose the current level of understanding.
Each workflow inspects the task context, selects an organization, runs bounded
cycles, validates the result, and leaves evidence that another person can
inspect, repeat, and improve.

## Skills

| Skill | English | 中文 | 日本語 |
|---|---|---|---|
| `compete-cron-builder` | Runs bounded proposal competitions with `n` workers, `m` proposals, `choose k`, all-valid coverage or risk union, repair queues, blueprint synthesis, and three-way challenge artifacts. | 运行有边界的方案竞争，支持 `n` 个 worker、`m` 个 proposal、`choose k`、全量有效 coverage 或 risk union、修复队列、蓝图综合和三方竞争产物。 | `n` workers、`m` proposals、`choose k`、all-valid coverage / risk union、repair queue、blueprint synthesis、three-way challenge artifact を扱う bounded proposal competition を実行します。 |
| `execution-cron-builder` | Executes one authoritative blueprint through a DAG, daily todo, isolated automation clone, bounded worker batches, master validation, checkpoints, and cleanup. | 通过 DAG、每日 todo、隔离 automation clone、有界 worker batch、master 验证、checkpoint 和 cleanup 执行一个权威 blueprint。 | 一つの authoritative blueprint を DAG、daily todo、isolated automation clone、bounded worker batch、master validation、checkpoint、cleanup で実行します。 |
| `learn-cron-builder` | Converts a bounded source scope into validated code-to-human notes, strict subset learning, code-to-code transforms, or routed human-language translations. | 把有边界的 source scope 转成经验证的 code-to-human notes、严格 subset learning、code-to-code transform 或带 route 的人类语言翻译。 | bounded source scope を、検証済みの code-to-human notes、strict subset learning、code-to-code transform、route 付き翻訳へ変換します。 |
| `optimization-cron-builder` | Converts a design philosophy into a bounded `Stage_*_AR_Blueprint.md` and one architecture-refinement research document per item. Product-code implementation remains downstream. | 根据 design philosophy 生成有边界的 `Stage_*_AR_Blueprint.md` 和逐项 architecture-refinement research doc；产品代码实施属于后续工作。 | design philosophy から bounded `Stage_*_AR_Blueprint.md` と項目別 architecture-refinement research document を生成します。product-code implementation は後続工程です。 |
| `looper-cron-builder` | Builds resource-aware bridge controllers around DAG nodes, bridge surfaces, metrics, nested skill attempts, and operator signals, with leases, side-effect gates, compact evidence, rewards, ROI, no-reward pause, and re-funded resume. | 围绕 DAG 节点、bridge surface、指标、嵌套 skill attempt 和 operator signal 构建资源感知 bridge controller，包含 lease、副作用门、紧凑证据、reward、ROI、无奖励暂停和再注资恢复。 | DAG node、bridge surface、metric、nested skill attempt、operator signal の周りに、lease、side-effect gate、compact evidence、reward、ROI、no-reward pause、re-funded resume を持つ resource-aware bridge controller を構築します。 |

## Dual-Cursor Checklist Protocol

Execution and learn workflows use one progress grammar:

- `[ ]` means unfinished and available for a worker claim.
- `[_]` means worker self-tested; output and evidence await master integration
  or curation.
- `[x]` means master accepted after validation, integration, and reconciliation.

Workers may move only `[ ] -> [_]`. The master lane alone may move
`[_] -> [x]`. Cleanup requires zero `[ ]` and zero `[_]` items. Todos, ledgers,
progress summaries, and status commands preserve these exact marks. Extra queue
labels may add detail but cannot replace the checkbox state.

## Install

Clone the repository:

```bash
git clone https://github.com/weiyangzen/b3ehive.git
```

### Codex Plugin

The Codex plugin package is under
[`plugins/b3ehive`](plugins/b3ehive). The marketplace catalog is
[`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json).
[The plugin contract](docs/codex-plugin.md) covers installation, maintenance,
validation, and release.

Install from this repository checkout:

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

Install from GitHub:

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new Codex thread after installation so the five bundled skills load:

```text
Use b3ehive to create an execution blueprint.
Use b3ehive to compare routes and evidence.
Use b3ehive looper for bounded ROI control.
```

After editing a root skill directory, sync the plugin package before release:

```bash
scripts/sync_codex_plugin.sh
```

### Portable Skills

Install all five skills for Codex, Claude Code, opencode, OpenClaw, and Hermes:

```bash
cd b3ehive
scripts/install_skills.sh --target all --scope user
```

Install one target:

```bash
scripts/install_skills.sh --target codex --scope user
scripts/install_skills.sh --target claude --scope user
scripts/install_skills.sh --target opencode --scope user
scripts/install_skills.sh --target openclaw --scope user
scripts/install_skills.sh --target hermes --scope user
```

Install all five skills inside a project:

```bash
scripts/install_skills.sh --target all --scope project --project-dir /path/to/repo
```

[The platform contract](docs/agent-platforms.md) defines the portable layout:

| Target | User skill path |
|---|---|
| Codex | `~/.codex/skills/<skill>/SKILL.md` |
| Claude Code | `~/.claude/skills/<skill>/SKILL.md` |
| opencode | `~/.config/opencode/skills/<skill>/SKILL.md` |
| OpenClaw | `~/.openclaw/skills/<skill>/SKILL.md` |
| Hermes | `~/.hermes/skills/<skill>/SKILL.md` |

## Use

Run a three-way competition with the mock runner:

```bash
python3 compete-cron-builder/scripts/compete_cron_builder.py \
  --task "Implement a thread-safe rate limiter" \
  --output ./competition-runs/rate-limiter \
  --competition-shape three_way_challenge \
  --artifact-layout old_three_way \
  --runner mock \
  --min-free-gb 0
```

Invoke a repository-local workflow by skill name:

```text
Use compete-cron-builder to compare local proposals, synthesize a blueprint, or run coverage union.
Use execution-cron-builder for this repo and this blueprint.
Use learn-cron-builder to learn a codebase, transform source artifacts, or translate docs.
Use optimization-cron-builder with this design philosophy.
Use looper-cron-builder to add resource-aware bridge controllers around these bridge surfaces and metrics.
```

Claude Code also accepts slash syntax such as
`/execution-cron-builder`. opencode discovers `SKILL.md` directories from
`.opencode/skills/`, `~/.config/opencode/skills/`, `.claude/skills/`, and
`~/.claude/skills/`. OpenClaw and Hermes accept
`skills/<skill>/SKILL.md` for repository or tap installs.

## Repository Map

- [compete-cron-builder](compete-cron-builder/SKILL.md) — bounded proposal competition, selection, synthesis, and coverage union
- [execution-cron-builder](execution-cron-builder/SKILL.md) — blueprint-driven implementation cron
- [learn-cron-builder](learn-cron-builder/SKILL.md) — source-to-target learning, transform, and translation cron
- [optimization-cron-builder](optimization-cron-builder/SKILL.md) — design-guided optimization cron
- [looper-cron-builder](looper-cron-builder/SKILL.md) — resource-aware bridge controller cron
- [SKILL.md](SKILL.md) — skill index and removed-tool cleanup note
- [plugins/b3ehive](plugins/b3ehive/README.md) — Codex plugin package
- [docs/README.md](docs/README.md) — documentation index and language contract
- [docs/concepts.md](docs/concepts.md) — core concepts
- [docs/blueprint.md](docs/blueprint.md) — blueprint contract and lifecycle
- [docs/codex-plugin.md](docs/codex-plugin.md) — Codex plugin contract
- [docs/agent-platforms.md](docs/agent-platforms.md) — platform compatibility contract
- [config.yaml](config.yaml) — root configuration

## Name And License

`b3` means Blueprint, Batch, Behavior. `hive` means swarm intelligence.

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))
