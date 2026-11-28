# 多层 Blueprint、奥卡姆最小拆解与 Lean 4 校验

[English](multi-layer-and-anti-cartesian.md)

b3ehive v3.0.0 在原仓库内提供多层 `blueprint` 栈、奥卡姆反笛卡尔最小拆解，以及位于 `formal/b3elean/` 的 Lean 4 形式化校验能力。

## 原则：最低生成式复杂度（奥卡姆剃刀）

单份蓝图能装下就不拆多层。抽中台不仅看渐进复杂度 $O(M+N)$，更看抽象与协作常量 $k$：

- 比较 $k + M + N$ 与 $M \times N$：仅当真实复用收益大于常量成本 $k$ 时才抽入 `platform`，否则留在本地，不建空壳中台与多余仪式。
- 粒度直奔 **2,000–5,000 LOC** 可执行条目：既避免单体膨胀，也不硬拆高协调开销的碎片项。
- 满二晋升（Rule-of-Two）：仅当至少 2 个真实 `leaf` 共享同一能力且抽取能缩短总描述长度时，才由单写者（`master` 或 `steward`）晋升到 `platform`。

## 三层栈（`blueprint_stack.json`）

| 角色 | 权属 | 跨蓝图依赖规则 |
|---|---|---|
| `master` | 全局约束、波次收口门、共享 canon | 波次收口可依赖 `platform` 与 `leaf` |
| `platform` | 共享契约与晋升模块（单写者） | 可依赖 `master`；指向 `leaf` 必须显式标 `harvest: true` |
| `leaf` | 单个具体目标代码与门禁 | 可依赖 `master` 与 `platform`；严禁指向同层 `leaf` |

每份蓝图各自维持同名只读 Gantt（`<name>_Gantt.<ext>`）。

## 六项不可约简校验

```bash
bin/b3ehive validate stack blueprint_stack.json --repo-root .
bin/b3ehive validate boundaries blueprint_stack.json --repo-root .
bin/b3ehive validate export-ir blueprint_stack.json --repo-root . -o stack_ir.json
```

1. 全栈 `blueprint_id` 与 item ID 唯一；跨蓝图有向图全局无环（输出 `topo_witness`）。
2. 本地依赖不发生 `layer` 层级倒置。
3. 前缀级路径不干扰（默认 `dag_ordered`：路径重叠或嵌套的条目必须在 DAG 中有先后偏序；也支持 `strict_disjoint`）。
4. 跨蓝图 `[x]` 验收传递闭包成立。
5. 边界单向（禁 `leaf -> leaf`、`platform -> leaf` 需 `harvest: true`）+ 源码零同层导入与零中台反向依赖扫描。
6. 跨 `leaf` 条目 `capability:` 满二晋升检查。

## 多代修订

- **局部修订**：追加新 ID 与 `DECIDE`，不改动已 `[x]` 历史。
- **大版本重构**：新建 `<Name>_Rev2_Blueprint.md`，头部标明 `keep`（继承原门禁作不退化约束）与 `rebuild` 及量化目标。

## Lean 4 形式化校验（`formal/b3elean/`）

锁定 `leanprover/lean4:v4.34.0`，**零 Mathlib**（仅依赖核心 `Init`/`Std`），在 `B3ELean/Soundness.lean` 一次性证明四组不变量：全局无环（`topo_acyclic_sound`）、反链并发路径不干扰（`dag_ordered_noninterference`）、跨层边界与验收闭包安全（`checkBoundaries_sound`、`checkTransitiveAccepted_sound`、`master_only_acceptance`），以及奥卡姆满二晋升必要条件与大版本 `keep` 不退化（`occam_no_gain_for_single_leaf`、`major_revision_non_regression`）。

```bash
bin/b3ehive verify-lean self-check
bin/b3ehive verify-lean stack blueprint_stack.json --repo-root . [--cert]
bin/b3ehive verify-lean oracle lean:Module.Theorem --project path/to/lean --spec-dir Specs
```

反作弊门禁强制执行 `Specs/` 只读保护、外部 `leanchecker` 复验及严格公理白名单（仅放行 `propext`、`Classical.choice`、`Quot.sound`，硬拒绝 `sorryAx`、自定义 `axiom` 与 `native_decide`）。无 Lean 环境时可设 `B3_FORMAL_VERIFIER=off`。
