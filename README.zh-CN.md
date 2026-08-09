# b3ehive

[English](README.md)

[![Codex Skill](https://img.shields.io/badge/Codex-Skill-blue)](https://github.com/openai/codex)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![opencode Skill](https://img.shields.io/badge/opencode-Skill-green)](https://opencode.ai)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Hermes Skill](https://img.shields.io/badge/Hermes-Skill-purple)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

b3ehive 提供五个面向 agent 工作的 swarm skills。每个 skill 定义职责、边界、
验证门和 cleanup 规则，把工作组织成可检查、可验证、可继续的有界流程。其设计
受 Feynman Technique 启发，以清晰说明、可检查步骤和可重复证据呈现理解程度。
每项 workflow 均先观察任务实况，再选择组织形态、运行有界循环、验证结果并留下
可供他人检查、复现和改进的证据。

## 五个 Skills

| Skill | 作用 |
|---|---|
| `compete-cron-builder` | 运行有边界的方案竞争：`n` 个 workers、`m` 个 proposals、`choose k`、coverage union、repair queue 和 blueprint synthesis。 |
| `execution-cron-builder` | 把一个已确认的 blueprint 转成 execution cron：DAG、同名 Gantt Kanban 监控、worker/master 双通道、validation gate、checkpoint 和 cleanup。 |
| `learn-cron-builder` | 把 source scope 转成可验证 artifacts：code-to-human notes、subset learning、code-to-code transform 和 human-language translation。 |
| `optimization-cron-builder` | 根据 design philosophy 生成 `Stage_*_AR_Blueprint.md` 和逐项 architecture-refinement research docs。 |
| `looper-cron-builder` | 为反复尝试建立 resource-aware bridge controller：lease、side-effect gate、evidence、reward、ROI 和 pause/resume。 |

## Dual-Cursor Checklist Protocol

execution 和 learn workflows 共用一套进度语法：

- `[ ]` 表示未完成，worker 可以 claim。
- `[_]` 表示 worker 已自测，等待 master integration 或 curation。
- `[x]` 表示 master 已验证、集成并接受。

worker 只能执行 `[ ] -> [_]`；只有 master lane 可以执行 `[_] -> [x]`。
cleanup 要求 `[ ]` 和 `[_]` 均为零。

## 安装

Clone 仓库：

```bash
git clone https://github.com/weiyangzen/b3ehive.git
```

### Codex Plugin

Codex plugin package 位于
[`plugins/b3ehive`](plugins/b3ehive/README.zh-CN.md)，marketplace catalog
位于 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)。

从当前 checkout 安装：

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

从 GitHub 安装：

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后启动新的 Codex thread，加载五个 bundled skills。

### Portable Skills

为 Codex、Claude Code、opencode、OpenClaw 和 Hermes 安装全部五个 skills：

```bash
cd b3ehive
scripts/install_skills.sh --target all --scope user
```

安装单个平台：

```bash
scripts/install_skills.sh --target codex --scope user
scripts/install_skills.sh --target claude --scope user
scripts/install_skills.sh --target opencode --scope user
scripts/install_skills.sh --target openclaw --scope user
scripts/install_skills.sh --target hermes --scope user
```

## 快速使用

```text
Use compete-cron-builder to compare local proposals, synthesize a blueprint, or run coverage union.
Use execution-cron-builder for this repo and this blueprint.
Use learn-cron-builder to learn a codebase, transform source artifacts, or translate docs.
Use optimization-cron-builder with this design philosophy.
Use looper-cron-builder to add resource-aware bridge controllers around these bridge surfaces and metrics.
```

## 文档

- [docs/README.zh-CN.md](docs/README.zh-CN.md) — 文档索引和多语言规则
- [docs/concepts.zh-CN.md](docs/concepts.zh-CN.md) — 核心概念
- [docs/blueprint.zh-CN.md](docs/blueprint.zh-CN.md) — blueprint 契约和生命周期
- [docs/codex-plugin.zh-CN.md](docs/codex-plugin.zh-CN.md) — Codex plugin 安装、使用和发布
- [docs/agent-platforms.zh-CN.md](docs/agent-platforms.zh-CN.md) — 平台兼容契约

## Repository Map

- [compete-cron-builder](compete-cron-builder/SKILL.md)
- [execution-cron-builder](execution-cron-builder/SKILL.md)
- [learn-cron-builder](learn-cron-builder/SKILL.md)
- [optimization-cron-builder](optimization-cron-builder/SKILL.md)
- [looper-cron-builder](looper-cron-builder/SKILL.md)
- [plugins/b3ehive](plugins/b3ehive/README.zh-CN.md)
- [SKILL.md](SKILL.md)

## License

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))
