# 核心概念

[English](concepts.md)

如果需要选择 skill，先阅读 [Skill 选择与使用](skill-selection.zh-CN.md)。本页
解释共享模型。

## 一类工作，一种编排

| 工作 | Skill | 编排 |
|---|---|---|
| 单轮方案比较、根因、审计、覆盖 | compete | 并行候选；oracle 优先择一，或去重取并集 |
| 长程实现 | execution | 一份 blueprint 化为 DAG；worker 隔离；master 验收 |
| 陌生代码、迁移、翻译、外部知识 | learn | 锁定 manifest 一一映射，或建 canon |
| 更快、更小、更省、更简 | optimization | 冻结 oracle 下的串行测量比较，或设计研究 |
| 外挂 loop 粒度或共享治理 | looper | 挂到 item、metric 或 surface 的可选层 |

五个 skill 是可选的编排，不是必经阶段。一个任务可以只用一个 skill，也可以
组合少量 skill。

## 三个共享单元

- **core**（`core/core.md`）：七律与定词表；只写一次，同步入每个 skill。
- **loop**（`looper-cron-builder/loop.md`）：形状、停止规则、ratchet、消融开关；其他 skill 按名绑定。looper skill 另外提供可选的外挂挂载和粒度层。
- **生成物**：gate、harness、receipt、hook、cron 或 flow 配置、ledger。提示词载判断，产物载机制。

## 七律

1. 一源：一份 blueprint；`[ ]` 未做，`[_]` 已交，`[x]` 已收。
2. 先立判官：开工前定 oracle。
3. 引而后断：外部事实出自 canon。
4. 复跑方收：receipt、重算指标、新输入。
5. 先租后用：无奖励累积至暂停。
6. 隔离如实：一 worker 一工作区，请求逐一计数。
7. 察器而不改器：仪器之改另立条目。

## 动词即授权

worker claim、submit；oracle measure；非作者评审 judge；master accept、reject、revert；外部 loop 需要治理时，looper lease、pause、retire。lint 拒绝其他搭配，故“只有 master 能收”只存于一张表。

## 外部知识

- learn 建 canon：每条有版本、哈希、级别（`V`、`F`、`I`）、许可与所辖决策。文档 MCP 是来源之一，与规范、datasheet、源码、策展 wiki 并列。
- 决策依赖外部事实时，各 skill 引 canon。
- 测量工具（profiler、analyzer）是仪器：先探测再用，记入 `instruments.tsv`，附诊断手册。

## 名

`b3` = Blueprint、Batch、Behavior；`hive` = 蜂群。择编排，行有界之事，留证据。
