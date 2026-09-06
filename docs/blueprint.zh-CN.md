# Blueprint（蓝图）

[English](blueprint.md)

> Blueprint 是 b3ehive 工作流的唯一权威需求源，是整个蜂群的"心脏"和"燃料"。

---

## 1. 什么是 Blueprint

Blueprint 不是传统意义上的需求文档。它是**可执行的、自带状态的、驱动机器工作**的活的规格说明。

### 1.1 核心特征

| 特征 | 说明 |
|---|---|
| **唯一性** | 每个 Skill 有且只有一个 blueprint 文件，禁止多个需求来源互相冲突 |
| **自带 Checklist** | Blueprint 内包含 `[ ]` / `[_]` / `[x]` 标记的执行清单，本身就是进度表 |
| **自带依赖 DAG** | Checklist 项之间可以定义依赖关系，生成每日 todo 时变成拓扑排序的 DAG |
| **动态更新** | 每完成一批工作，guard 会把 `[ ]` 改为 `[x]` 写回 blueprint，它是活的 |
| **分层结构** | 可定义"层"（layer），强制执行"底层未完成前上层不能关闭" |

### 1.2 与传统 Spec 的本质区别

| 维度 | 传统 Spec | b3ehive Blueprint |
|---|---|---|
| **文档性质** | 静态文档，写给人看 | 动态文档，给机器执行 |
| **内容构成** | 需求描述 + 验收标准 | 需求描述 + **执行清单** + **实时进度** + **依赖关系** |
| **生命周期** | 项目启动时写好，完成后归档 | 贯穿整个开发周期，持续被修改（打勾、拆分、更新） |
| **权威源** | 可能有多个子文档、多个版本 | **有且只有一个权威源**，所有工作由此派生 |
| **完成状态** | 在 Jira/Trello/项目管理工具里 | 完成状态就在 **blueprint 文件本身**里（`[ ]` → `[_]` → `[x]`） |
| **执行驱动** | 人读了 Spec 再去写代码 | Blueprint **直接驱动** Worker 执行，无需人工翻译 |
| **验证方式** | 靠人工 review 是否符合 Spec | 靠自动**验证门**（编译/测试/lint）决定能否打勾 |
| **变更管理** | 变更需要走流程、重审文档 | Guard 自动管理变更（超时拆分、层门重置、子项展开） |
| **完整性检查** | 靠人判断是否遗漏 | Guard 自动检查 DAG 完整性，拒绝环和缺失依赖 |
| **粒度** | 通常较粗，描述功能模块 | 可细化到**文件级别**（`owned_paths`），甚至子项拆分 |
| **与代码的关系** | Spec 和代码是分离的两件事 | Blueprint 和代码在同一个仓库里**共同演化** |

> **Blueprint = Spec（需求规格）+ Task Board（任务板）+ State Store（状态存储）+ DAG Engine（依赖引擎），四合一。**
>
> 传统 Spec 回答的是**"做什么"**，Blueprint 回答的是**"做什么 + 做到哪了 + 下一步做什么 + 能不能做"**。

---

## 2. Blueprint 的两种形态

| 形态 | 说明 | 适用场景 |
|---|---|---|
| **Prose-first** | 先写散文式的需求描述，再从中抽取 checklist | 需求尚不清晰，需要逐步细化 |
| **Checklist-first** | 直接以 checklist 作为 blueprint 主体 | 需求已明确，可直接执行 |

对于 prose-first 的 blueprint，在第一次 cron tick 前，guard 会自动在同一个文件中插入一个权威的 execution checklist 段落，并将所有项初始化为 `[ ]`。

---

## 3. Checklist 的结构约定

一个标准的 checklist 项包含以下要素：

```markdown
- [ ] [ITEM-001] 实现用户认证模块
  - depends_on: []
  - layer: foundation
  - owned_paths: src/auth/

- [ ] [ITEM-002] 实现 JWT Token 签发
  - depends_on: [ITEM-001]
  - layer: foundation
  - owned_paths: src/auth/jwt.ts

- [ ] [ITEM-003] 实现登录 API
  - depends_on: [ITEM-001, ITEM-002]
  - layer: api
  - owned_paths: src/api/login.ts
```

### 字段说明

| 字段 | 必填 | 说明 |
|---|---|---|
| `item_id` | ✅ | 稳定唯一标识，如 `ITEM-001` |
| `depends_on` | ❌ | 依赖的其他 item_id，逗号分隔 |
| `layer` | ❌ | 层标识，用于严格层门控制 |
| `owned_paths` | ❌ | 该项涉及的文件/目录路径 |

> Guard 在生成每日 todo 时，会解析这些字段构建 DAG，并拒绝环和重复 ID。

---

## 4. 约束规则

### 4.1 严格层门（Strict Layer Gate）

当 blueprint 显式定义了 layer 时：

- **只允许在最细的未闭合层中执行新任务**
- 如果低层还有 `[ ]` 项，高层项必须保持 `[ ]`
- 如果 guard 检测到高层 `[x]` 而低层仍有 `[ ]`，**自动将高层 `[x]` 重置回 `[ ]`**，然后继续从低层执行

> 这保证了"地基没打好就不能盖楼"的物理约束。

### 4.2 父子项自动关闭

- 如果所有子 checklist 项都变为 `[x]`，父项**自动关闭**为 `[x]`
- 如果有任何一个子项仍是 `[ ]`，父项必须保持 `[ ]`
- 当某项在多次 tick（默认 ≥5 次）后仍未解决，guard 会自动将其拆分为子 checklist 项

---

## 5. Blueprint 与每日 Todo 的关系

Blueprint 是**权威源**，每日 todo 是它的**只读派生视图**：

- Todo 只包含 blueprint 中未完成的项（`[ ]` 和 `[_]`）
- Todo 包含当前 DAG 状态：node_id、依赖、claim_owner、integration_state
- Todo 中的路径必须是**仓库相对路径**，禁止泄露 `.cron/automation_repo*` 等绝对路径
- 每次成功 batch 后，guard 会**先更新 blueprint**，再**刷新 todo**

---

## 6. 不同 Skill 中的 Blueprint 形态

| Skill | Blueprint 的具体形态 |
|---|---|
| `execution-cron-builder` | 一个 Markdown 文件，里面有散文式需求描述 + checklist 段落。cron 按 checklist 逐项实现代码。 |
| `learn-cron-builder` | 生成 `learn_checklist.md`，从锁定 source manifest 派生；可做 code→human understand、code→code transform、human→human translate。 |
| `optimization-cron-builder` | `Stage_*_AR_Blueprint.md`，从设计理念推导出的架构优化清单，每项对应一篇研究文档。 |
| `compete-cron-builder` | blueprint 是一个局部 `question_type`。也可用于 execution choice、coverage union、repair queue、SEO strategy 等局部竞争。 |

---

## 7. Blueprint 的生命周期

```
Bootstrap:   初始化 checklist，所有项标记为 [ ]
    ↓
Daily Todo:  从 blueprint 的未完成项生成当日 todo（含 DAG 依赖）
    ↓
Worker 执行: 按 DAG 顺序 claim 任务，产出代码/文档，将自测通过项标记为 [_]
    ↓
Validation:  Master 集成 [_] 输出并运行验证门（编译、测试、lint 等）
    ↓
Checkpoint:  通过后，将 [_] 改为 [x]，写回 blueprint
    ↓
Cleanup:     当 blueprint 中所有项都变为 [x]，cron 自动停止并清理自身
```

---

## 8. 总结

Blueprint 是 b3ehive 区别于传统 AI 助手的核心设计之一。它把一个"给人读的文档"变成了"给机器执行的程序"：

- **状态即代码**：完成进度直接写在文件里，git 历史就是项目状态历史
- **需求即执行**：不需要 PM 把 Spec 翻译成任务，blueprint 本身就是任务队列
- **约束即规则**：层门、DAG、父子关系等约束由 guard 自动强制执行，而不是靠人的记忆

理解 Blueprint，就理解了 b3ehive 的工作方式。
