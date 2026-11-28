# 多层 Blueprint 与奥卡姆最小拆解（实验特性）

[English](multi-layer-and-anti-cartesian.md)

分支 `exp/multilayer-anticartesian` 为多层 `blueprint` 栈与反笛卡尔积拆解提供最小可用规约。

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
