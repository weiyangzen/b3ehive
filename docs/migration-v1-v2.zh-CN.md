# v1 到 v2 迁移

[English](migration-v1-v2.md)

v2 改变了 b3ehive 的验收模型。它不只是缩短 skill 文件，还把共享规则移入
公共模块，并明确要求 evidence、oracle 复跑和 master acceptance。

## 为什么升级

v1 把很多规则写在较长的 skill body 中。这样会带来两个问题：不同 skill
之间的规则难以保持一致，worker 的报告也容易被误认为已经验收。

v2 解决四个问题：

1. 共享法律集中在 `core/core.md`。
2. attempt loop 在 `looper-cron-builder/loop.md` 中只有一个 source。
3. 每个 item 在工作开始前声明 oracle。
4. master 集成后重新运行 oracle，才能接受结果。

v2 还增加了用于外部知识的 pinned canon，以及用于 measured optimization 的
instruments。

## 主要变化

| 方面 | v1 | v2 |
|---|---|---|
| 规则位置 | 较长的 skill body | shared core、loop 和 skill-specific rules |
| 验收 | 自测和仓库 gate | item oracle、receipt、master 集成和复跑 |
| worker 权限 | 实现和验收容易混在一起 | worker submit；master accept |
| 外部知识 | 没有共享 canon 契约 | 记录 version、hash、level、license 和所辖 decision 的 pinned canon |
| 优化 | 以研究流程为主 | 围绕 baseline、fresh inputs 和 hypothesis ledger 的串行测量比较；保留 design mode |
| 竞争 | 旧布局和旧选择规则 | 一轮有边界的并行比较，再进行 oracle-first、blind review 和去除自投后的投票 |
| Loop 粒度 | 常隐含在选中的工作中 | 可选的外挂 looper 层可以把 loop 挂到 item、metric 或 surface |
| 校验 | 词汇存在性检查 | structure、lexicon、unit 和 behavior 检查 |

具体的历史测量值保留在根 README 中。它们是 v2 release snapshot，不是每个
未来版本都必须保持的承诺。

## v2 新概念

### Core

[`core/core.md`](../core/core.md) 定义七条法律和 verb lexicon。相同文件会被
复制到每个 skill 的 `references/core.md`。

### Loop

[`looper-cron-builder/loop.md`](../looper-cron-builder/loop.md) 定义 attempt
shape、stop rule、ratchet 和 ablation switch。其他 skill 按名称绑定这个
loop。

最小工作单元通常已经内化在选中的 skill 中。`looper-cron-builder` 是可选的
外挂层。loop 需要定义在其他粒度上，或需要共享明确的资源和副作用边界时，才
使用它。

### 比较形态

`compete` 用于一轮有边界的并行 candidate。它回答一个冻结问题，再选择结果
或合并 findings。

`optimization` 通常一次比较一个 candidate。它测量、保留或回退，再用结果选
择下一个 candidate。只有独立 hypothesis 需要同一轮比较时，才使用并行
`lanes`。

### Oracle

oracle 是判断 item 是否可接受的 command 或 review protocol。它必须在工作开
始前定义。test command 是一种 oracle，benchmark 或非作者 review protocol
也是 oracle。

### Receipt

receipt 记录提交的路径、命令、结果和其他 evidence。它说明 worker 提交了什
么，但不代表结果已经被接受。

### Master acceptance

master 把合法 submission 集成到 canonical checkout，再次运行 oracle。只有
这样，item 才能从 `[_]` 变为 `[x]`。

### Canon 和 instruments

`learn` 使用 canon 固定外部事实。`optimization` 使用带 probe command 和
diagnosis playbook 的 instruments。这些记录可以阻止未固定的外部事实或未经
验证的测量直接变成 decision。

## 迁移步骤

### 1. 安装 v2

使用 v2 checkout 或 package。portable installation：

```bash
scripts/install_skills.sh --target all --scope user --link
```

Codex installation：

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

安装后新开 session。

### 2. 检查已安装 skill 和 controller

```bash
bin/b3ehive doctor --repo .
```

doctor 会报告过期的已安装 skill，以及由旧 skill contract 生成的 controller。
开始新的长期 execution 前，应根据当前 repository evidence 重新生成
controller。

### 3. 转换 blueprint

为每个 item 添加或确认：

- 稳定的 id；
- `depends_on`；
- `owned_paths`；
- `oracle` 或 `review:<protocol>`；
- 需要证据等级时使用 `tier`；
- 需要限制 item 大小时使用 `budget`；
- 外部事实影响设计时使用 `canon`。

不要从文档顺序推断 dependencies。重复 id、缺失 dependency、循环和未知
mark 都必须拒绝。

### 4. 更新验收处理

使用 v2 状态：

```text
[ ] open 或 rejected
[_] 带 receipt 的 submitted
[x] master 复跑后 accepted
```

不要让 worker 修改 acceptance mark。`[x]` 的状态转换由 master 负责。

### 5. 选择当前 artifact layout

native v2 competition layout 是默认值。已有 consumer 需要旧结构时，仍可请求
old three-way layout：

```text
--shape three_way_challenge --artifact-layout old_three_way
```

只有已有 consumer 依赖 `run_a`、`run_b`、`run_c` 路径时才使用兼容布局。它不
会恢复旧的选择权限。

### 6. 把详细规则移入 references

skill body 只保留判断：何时使用、如何选择 shape、使用哪个 oracle 和何时停
止。长协议放在 skill 的 `references/` 目录。先修改 root skill source，再同
步 Codex plugin 副本。

## 哪些内容只保留为历史资料

仓库可以保留用于说明迁移、兼容面或规则来源的 v1 text，但必须标明历史性。
它们不能作为当前 v2 使用入口。

例如：

- `references/lessons.md` 的迁移表；
- 标记为 `v1 text` 的章节；
- `three-way-layout.md` 的兼容细节；
- `old_three_way` artifact 支持；
- learn coverage rules 中的一次性 import alias。

## 迁移检查

- 已安装 skill 报告当前版本。
- 每个 item 都有 oracle。
- 每个 worker submission 都有 receipt。
- master 在集成后重新运行 oracle。
- 除非兼容要求旧布局，否则使用 native layout。
- 当前使用说明不再链接到历史 v1 页面。
- root skill source 和生成的 plugin 副本保持同步。
