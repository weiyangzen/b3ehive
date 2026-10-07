# b3ehive 文档

[English](README.md)

面向用户的文档使用成对 Markdown 文件：

- `*.md` 是默认英文 canonical 页面。
- `*.zh-CN.md` 是简体中文页面。
- 每组文件顶部链接到配对页面。
- 技术名词保留英文原文，例如 `blueprint`、`DAG`、`skill`、`worker`、
  `master lane`、`validation gate`、`LooperLog` 和命令名。

## 从这里开始

| 需求 | 页面 |
|---|---|
| 安装 b3ehive 并完成第一次调用 | [开始使用](getting-started.zh-CN.md) |
| 按任务选择 skill | [Skill 选择与使用](skill-selection.zh-CN.md) |
| 理解 v1 到 v2 的变化 | [v1 到 v2 迁移](migration-v1-v2.zh-CN.md) |
| 编写和审查 b3ehive 文档 | [写作规范](writing-style.zh-CN.md) |

## 文档列表

| English | 中文 |
|---|---|
| [Core Concepts](concepts.md) | [核心概念](concepts.zh-CN.md) |
| [Blueprint](blueprint.md) | [Blueprint 蓝图](blueprint.zh-CN.md) |
| [Codex Plugin](codex-plugin.md) | [Codex Plugin](codex-plugin.zh-CN.md) |
| [Agent Platform Compatibility](agent-platforms.md) | [Agent 平台兼容性](agent-platforms.zh-CN.md) |
| [Getting Started](getting-started.md) | [开始使用](getting-started.zh-CN.md) |
| [Skill Selection and Use](skill-selection.md) | [Skill 选择与使用](skill-selection.zh-CN.md) |
| [v1 to v2 Migration](migration-v1-v2.md) | [v1 到 v2 迁移](migration-v1-v2.zh-CN.md) |
| [Writing Style](writing-style.md) | [写作规范](writing-style.zh-CN.md) |

## 语言契约

- 面向用户的文档成对添加。
- 链接尽量指向同语言页面。
- 临时只有一种语言的主题在 release 前补齐配对文件。
- 每份正文使用一种语言，通过顶部语言链接切换配对译文。
