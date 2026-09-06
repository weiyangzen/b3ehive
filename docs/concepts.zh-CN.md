# b3ehive 核心概念

[English](concepts.md)

> 本文档整理自社区讨论，用于帮助新用户快速理解 b3ehive 的设计哲学和关键抽象。

---

## 一、项目理念：为什么是蜂群？

### 1.1 费曼技巧的启发

b3ehive 的灵感来自物理学家理查德·费曼的**费曼技巧**（Feynman Technique）：

> **"What I cannot create, I do not understand."**
>
> 如果你不能用简单的语言把它教给别人，说明你还没有真正理解它。

b3ehive 把这个思想搬到了 AI Agent 的工作中：让 Agent 把问题拆分、执行、验证，留下一条**可检查、可重复、可改进**的路径。最终产出的不只是代码，更是一份"教给人类"的完整证据链。

### 1.2 一个 Agent 是声音，一群 Agent 是编排

| 传统 AI 助手 | b3ehive |
|---|---|
| 一个助手，一种形态 | **五种蜂群组织形态** |
| Prompt In → Answer Out | **Checklist → Worker → Validator → Cleanup** |
| 隐藏状态 | **可检查的 Spec、Todo、Log、Artifact** |
| "看起来完成了" | **通过验证门，才能 Checkpoint** |

不同的工作，需要不同的组织方式：

- **难以决策或需要覆盖** → 需要 **compete**（proposal competition / coverage union）
- **长期实现** → 需要**执行**（execution）
- **未知代码库 / source-to-target 转换 / 翻译** → 需要 **learn**
- **成熟系统** → 需要**优化**（optimization）
- **重复反馈 / bridge surface / 指标桥接** → 需要**资源感知 bridge controller**（looper）

`LooperLog` 是 looper 内部的多粒度反馈证据面，用来记录 `TargetObject`
movement 和 `InstrumentObject` quality。正常执行推进任务对象；looper 同时
观察 skills/scaffolds/tools/routes/validators/scripts/ledgers 是否帮助、阻塞、
浪费或验证不足。它不是第六个 public skill，也不是运行时自动改 skill 的入口。

b3ehive 不是代码生成器，而是**按科学方法组织的集体工作**：观察地面 → 选择组织形态 → 运行有边界的循环 → 诚实验证 → 留下证据。

---

## 二、Blueprint（蓝图）

Blueprint 是 b3ehive 工作流的**唯一权威需求源**，是整个蜂群的"心脏"和"燃料"。

它不是一个静态的 Spec 文档，而是**可执行的、自带状态的、驱动机器工作**的活的规格说明。Blueprint 内嵌 checklist（`[ ]` / `[_]` / `[x]`）、依赖 DAG、分层结构，guard 直接读取它来决定"今天做什么、做到哪了、下一步做什么"。

> **一句话：传统 Spec 回答"做什么"，Blueprint 回答"做什么 + 做到哪了 + 下一步做什么 + 能不能做"。**

详细说明见：[Blueprint 详解](./blueprint.zh-CN.md)

---

## 三、五大 Skill 速查

| Skill | 核心能力 | 输入 | 输出 |
|---|---|---|---|
| `compete-cron-builder` | 多 proposal 竞争、选优、合并或修复队列 | 一个局部问题 + n/m/k 预算 | selected candidates、coverage union、repair queue 或 blueprint synthesis |
| `execution-cron-builder` | 按蓝图持续执行代码 | 一个 Blueprint | 逐项实现的代码 + checkpoint 提交 |
| `learn-cron-builder` | 源到目标学习：understand / transform / translate | source scope + subset + target contract | learning notes、transformed artifacts、translations、traceability |
| `optimization-cron-builder` | 架构优化研究 | 设计理念 + 阶段蓝图 | 每项优化的研究文档 |
| `looper-cron-builder` | 资源感知 bridge controller | BridgeSurface / BridgeMetric + ResourceEnvelope + SideEffectGate + Validator | bridge delta、compact evidence、reward/ROI ledger、暂停/恢复策略 |

---

## 四、命名由来

- **b3** = **B**lueprint, **B**atch, **B**ehavior
- **hive** = Swarm intelligence（蜂群智能）

> Choose the right swarm, run bounded work, and leave proof.
> So called b3ehive.
