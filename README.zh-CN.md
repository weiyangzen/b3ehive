# b3ehive

[English](README.md)

**五编排，一律，一环。**

b3ehive 把编码 agent 编成蜂群。五个 skill 各司一类工作；共守一部短律，共用一个尝试循环；未经复跑，一概不收。

## 五编排

| Skill | 用于 | 编排 |
|---|---|---|
| [`compete`](compete-cron-builder/SKILL.md) | 难抉择、根因、审计 | 并行候选；先 oracle，次盲审，再计票（自投作废）；或发现去重取并集 |
| [`execution`](execution-cron-builder/SKILL.md) | 长程实现 | 一份 blueprint 化 DAG；worker 隔离；master 验收 |
| [`learn`](learn-cron-builder/SKILL.md) | 陌生代码、迁移、翻译、外部知识 | 锁定 manifest 一一映射，或建 canon；深度可选 `what`、`how`、`why` |
| [`optimization`](optimization-cron-builder/SKILL.md) | 更快、更小、更省、更简 | 冻结 oracle 下测量循环，或设计研究 |
| [`looper`](looper-cron-builder/SKILL.md) | 预算内反复尝试 | 共享 loop 与治理 |

## 结构

```text
core/core.md ─────────── 七律 + 定词表 ──┐
                                         ├── 同步入每个 skill
looper-cron-builder/loop.md ── 尝试循环 ─┘

SKILL.md ── 判断：何时用、如何拆、用何 oracle、取何形状、何时止
生成物   ── 机制：gate、harness、receipt、hook、cron 与 flow 配置
```

提示词载判断，产物载机制。不可违之规，化为生成的检查，不复述。

## 七律

1. **一源。** 一份 blueprint。`[ ]` 未做，`[_]` 已交，`[x]` 已收。
2. **先立判官。** 开工前，每条定 oracle。
3. **引而后断。** 外部事实出自已钉的 canon。
4. **复跑方收。** receipt、重算指标、新输入。
5. **先租后用。** 无奖励累积至暂停。
6. **隔离如实。** 一 worker 一工作区，请求逐一计数。
7. **察器而不改器。**

动词即授权：worker *claim*、*submit*；oracle *measure*；非作者评审 *judge*；master *accept*、*reject*、*revert*；looper *lease*、*pause*、*retire*。他种搭配，lint 拒之。

## 循环

```text
attempt ─ receipt ─ ADVANCED | STALLED | REGRESSED
   ▲                         │
   │   二滞：重规划          │   三滞：暂停
   └─ ratchet：oracle 测得更优方留，否则回退
```

形状：`single`；`relay`（模型族交替，新 session，仓库即记忆）；`review`（每轮新的只读非作者评审）；`lanes`（并行，由 compete 选）。`B3_LOOP=full|single|null` 供消融。

## 外部知识

- **Canon。** learn 从文档 MCP、规范、datasheet、源码、策展 wiki 建条目；每条记版本、哈希、级别（`V` 一手、`F` 社区、`I` 推断）、许可、所辖决策。决策需要时引之。
- **仪器。** profiler 与 analyzer 先探测后用，记入 `instruments.tsv`，附诊断手册。

b3ehive 不内置领域知识。CUDA 文档 MCP、kernel wiki、Nsight Compute skill 一类领域包，经 canon 与仪器接入。

## 安装

```bash
git clone -b v2 https://github.com/weiyangzen/b3ehive.git && cd b3ehive
scripts/install_skills.sh --target all --scope user --link
```

`--link` 以软链接安装，`git pull` 即更新各平台。不加则复制并写版本戳，`bin/b3ehive doctor` 可查漂移。安装路径见 [docs/agent-platforms.zh-CN.md](docs/agent-platforms.zh-CN.md)。

## 使用

```text
Use execution-cron-builder for this repository and this blueprint.
Use compete-cron-builder to pick the root cause; the oracle is `make test`.
Use learn-cron-builder to build a canon from these specs for BLUEPRINT.md.
Use optimization-cron-builder in measured mode on this kernel.
Use looper-cron-builder to govern these loops within a weekly budget.
```

```bash
bin/b3ehive compete --question-type precision \
  --oracle-command 'make check CANDIDATE={candidate_dir}' --oracle-runs 3 \
  "Pick the root cause of the failing scheduler test"
```

runner 取自 `B3EHIVE_AGENT_RUNNER`；`--mock` 为空跑。

## 检查

```bash
scripts/check_all.sh         # 同步、lint、单测、布局与平台校验
bin/b3ehive doctor --repo .  # 过期安装与控制器
```

`evals/scenarios.json`：十六个行为场景（每 skill 至少三个）与消融矩阵。

## v2 一览

| | v1 | v2 |
|---|---|---|
| SKILL.md 正文 | 11,461 词 | 3,432 词 |
| execution 单次加载 | 约 11.1k token | 约 3.0k token |
| 共享契约 | 约 3.8k token，寄于 looper | 约 1.1k token，core + loop，同步入各 skill |
| 验收 | 自测加仓库 gate | 每条 oracle、receipt、master 复跑、新输入 |
| 外部知识 | 无 | canon 与仪器 |
| optimization | 研究文档 | measured 与 design 两模式 |
| compete 选择 | 按 id 取前；自投计入；关键词猜题型 | oracle、盲审、去自投计票；题型由调用方定 |
| 校验 | 词汇存在性 | 结构与定词 lint、单测、行为评测 |

移出正文的规则，存于各 skill 的 `references/lessons.md`。

## 名与许可

`b3` = Blueprint、Batch、Behavior；`hive` = 蜂群。

MIT © Weiyang（[@weiyangzen](https://github.com/weiyangzen)）
