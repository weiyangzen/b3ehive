# b3ehive 文档

[English](README.md)

面向用户的文档使用成对 Markdown 文件：

- `*.md` 是默认英文 canonical 页面。
- `*.zh-CN.md` 是简体中文页面。
- 每组文件顶部链接到配对页面。
- 技术名词保留英文原文，例如 `blueprint`、`DAG`、`skill`、`worker`、
  `master lane`、`validation gate`、`LooperLog` 和命令名。

## 文档列表

| English | 中文 |
|---|---|
| [Core Concepts](concepts.md) | [核心概念](concepts.zh-CN.md) |
| [Blueprint](blueprint.md) | [Blueprint 蓝图](blueprint.zh-CN.md) |
| [Codex Plugin](codex-plugin.md) | [Codex Plugin](codex-plugin.zh-CN.md) |
| [Agent Platform Compatibility](agent-platforms.md) | [Agent 平台兼容性](agent-platforms.zh-CN.md) |

## 语言契约

- 面向用户的文档成对添加。
- 链接尽量指向同语言页面。
- 临时只有一种语言的主题在 release 前补齐配对文件。
- 每份正文使用一种语言，通过顶部语言链接切换配对译文。
