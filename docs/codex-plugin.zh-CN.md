# Codex Plugin

[English](codex-plugin.md)

b3ehive 作为 Codex plugin 打包在 `plugins/b3ehive`，并通过仓库内 marketplace catalog `.agents/plugins/marketplace.json` 暴露。

对 Codex 用户来说，plugin 是推荐分发方式。它把仓库根目录下同一组五个可移植 `SKILL.md` 目录打包成一个命名 package，方便 Codex 一次安装和加载。

## Plugin 包含什么

plugin 暴露五个 Codex skills：

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

每个 skill 在 `plugins/b3ehive/skills/<skill>/` 下保留自己的 `SKILL.md`、`agents/`、`references/` 和可选 `scripts/`。

root skill directories 仍然是 source of truth。plugin 目录中的副本是从 root skills 同步出来的 release package。

## 什么时候使用 Plugin

当消费者是 Codex，并且希望一次安装全部五个 b3ehive skills 时，使用 Codex plugin。

当消费者是 Claude Code、opencode、OpenClaw、Hermes，或需要 project-local `SKILL.md` layout 时，使用 portable skill installer：

```bash
scripts/install_skills.sh --target all --scope user
```

## 从当前仓库安装

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

## 从 GitHub 安装

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后启动新的 Codex thread，让 Codex 加载 plugin skills。

## 使用方式

安装后，在 prompt 中提到 `b3ehive` 或某个 bundled skill：

```text
Use b3ehive to create an execution blueprint.
Use compete-cron-builder to compare local proposals and synthesize a blueprint.
Use execution-cron-builder for this repo and this blueprint.
Use learn-cron-builder to learn this source scope into validated docs.
Use optimization-cron-builder with this design philosophy.
Use looper-cron-builder to add bounded ROI control around these bridge surfaces.
```

Codex 会在新 session 中加载 plugin skills。如果安装或更新前 session 已经打开，测试 discovery 前先启动新 thread。

## Package Layout

```text
.agents/plugins/marketplace.json
plugins/b3ehive/
  README.md
  README.zh-CN.md
  .codex-plugin/plugin.json
  skills/
    compete-cron-builder/
    execution-cron-builder/
    learn-cron-builder/
    optimization-cron-builder/
    looper-cron-builder/
```

`.agents/plugins/marketplace.json` 是仓库 marketplace catalog。它把 `b3ehive` marketplace entry 指向 `./plugins/b3ehive`。

`plugins/b3ehive/.codex-plugin/plugin.json` 是 plugin manifest。它的 version、description、URLs、capabilities 和 skill path 应与 `package.json` 和 public README 保持一致。

`plugins/b3ehive/skills/` 是五个 source skills 的 package copy。发布 plugin 前，先把 root skill directories 同步到 Codex plugin package：

```bash
scripts/sync_codex_plugin.sh
```

## Maintenance Workflow

1. 编辑 root skill directory，例如 `execution-cron-builder/SKILL.md`。
2. 运行 `scripts/sync_codex_plugin.sh`。
3. 检查 `plugins/b3ehive/skills/` 下的 generated diff。
4. 当 package metadata、用户可见行为、policy 或 legal surface 改变时，更新 `plugins/b3ehive/.codex-plugin/plugin.json`、`package.json`、`README.md`、`PRIVACY.md` 和 `TERMS.md`。
5. tag 或 publish 前运行验证。

不要把 `plugins/b3ehive/skills/` 下的 generated copy 当主编辑面。只改 package copy 的内容可能在下一次 sync 时被覆盖。

## Validation

release 前运行：

```bash
jq empty package.json .agents/plugins/marketplace.json plugins/b3ehive/.codex-plugin/plugin.json
scripts/validate_agent_platforms.sh
scripts/validate_learn_upgrade.sh
```

如果改了 plugin packaging，也检查 marketplace catalog 是否指向 package directory：

```bash
jq '.plugins[] | select(.name == "b3ehive").source.path' .agents/plugins/marketplace.json
```

## 当前 Public Directory 状态

这个 repository marketplace 是 public Git-backed distribution path。它不是 OpenAI official Plugin Directory listing。等 OpenAI self-serve public Plugin Directory publishing flow 可用时，再使用对应流程。

## Release Checklist

- 运行 `scripts/sync_codex_plugin.sh`。
- 验证 `plugins/b3ehive/.codex-plugin/plugin.json`。
- 确认 `.agents/plugins/marketplace.json` 指向 `./plugins/b3ehive`。
- 启动新的 Codex thread，确认五个 bundled skills 可被 discovery。
- 保持 `PRIVACY.md`、`TERMS.md`、`LICENSE` 和 README install instructions 最新。
- plugin metadata 和 root package metadata 的 version 对齐后再打 tag。
