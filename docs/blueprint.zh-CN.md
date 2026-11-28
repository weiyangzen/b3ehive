# Blueprint 蓝图

[English](blueprint.md)

第一次运行前，先阅读[开始使用](getting-started.zh-CN.md)和 [Skill 选择与使用](skill-selection.zh-CN.md)。

blueprint 是一次运行的唯一需求源、状态源、依赖源。guard 据此判定何者可做、何者受阻、何者可收。

blueprint 是权威来源。Gantt 或 todo 视图只是只读投影。

## 条目语法

```markdown
- [ ] [ITEM-030] title
  - depends_on: [ITEM-010, board#HW-041]
  - owned_paths: src/hal/, verify/gates/ITEM-030.sh
  - oracle: verify/gates/ITEM-030.sh
  - tier: T1
  - budget: loc<5000
  - canon: [A2, SPEC-12§4.4]
```

| 字段 | 必填 | 义 |
|---|---|---|
| id | 是 | 稳定唯一 |
| `oracle` | 是 | gate 命令，或由非作者执行的 `review:<protocol>` |
| `depends_on` | 否 | 依赖；`other#ID` 指向他份 blueprint，只阻验收 |
| `owned_paths` | 否 | worker 唯一可改路径 |
| `tier` | 否 | `[x]` 所需证据层；不足者止于 `[_]` |
| `budget` | 否 | 体量上限；估算超限者认领前先拆 |
| `canon` | 否 | 约束本条设计的 canon id |
| `layer` | 否 | 严格层门：下层先闭 |

## 状态

| 标记 | 义 | 设者 |
|---|---|---|
| `[ ]` | 未做或被退 | 作者、master |
| `[_]` | 已交，附 receipt | harvest 后的 controller |
| `[x]` | 复跑后收 | master |

cleanup 需 `[ ]` 与 `[_]` 皆零。blocked、paused 等词是遥测，不代标记。

## 规则

- 一次运行一源；todo 与 Gantt 投影只读。
- 无 oracle 的条目，先立造 oracle 的父条目。
- 重复 id、缺依赖、成环、未知标记，校验不过。
- 子条目皆 `[x]`，父条目方闭。
- 多 tick 不动者，guard 可拆为子条目。
- canon 中 `[I]` 事实未经 gate 证实，依赖它的条目不得收。

## 多层蓝图栈、奥卡姆最小拆解与 Lean 4

单份蓝图能装下就不拆多层。当多个目标共享中台时，用 `blueprint_stack.json` 组织 `master` / `platform` / `leaf` 三层栈，直奔 2,000–5,000 LOC 粒度，仅在复用收益大于常量成本 `k` 时才抽中台，并用 `bin/b3ehive validate stack|boundaries` 与 `bin/b3ehive verify-lean stack` 校验；高价值契约可声明 `oracle: lean:<Module>.<Theorem>`。详见[多层 Blueprint、奥卡姆最小拆解与 Lean 4 校验](multi-layer-and-anti-cartesian.zh-CN.md)。

## 生命周期

```text
bootstrap [ ] → claim → submit [_] → master 复跑 → accept [x] → cleanup
                               └→ reject [ ] 附 notes → 下一代
```

![生命周期：reject 退回未做](diagrams/accept.gif)

`reject` 把条目从 master 退回 `[ ]`。侧栏是授权，不是告警。亮起顺序是示意。

## 各 skill 的 blueprint

| Skill | 形态 |
|---|---|
| execution | 需求与 checklist 同在一份 Markdown |
| learn | 由锁定的 `source_manifest.tsv` 派生 `learn_checklist.md` |
| optimization | `Stage_*_AR_Blueprint.md`（design）；oracle 合同与假设账本（measured，通常串行） |
| compete | 已定的题型、m、k、oracle |
| looper | 可选的外挂 loop spec，挂在条目、指标或面上 |
