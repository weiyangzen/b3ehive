# b3ehive

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Fake it until make it"** — The Feynman Way

## The B3ehive Philosophy

I learned from one of the greatest physicists, **Richard Feynman**, whose nature was cheerful and whose intellect moved easily between worlds. He left behind the renowned **Feynman Technique**: learn by teaching.

That is the seed of **b3ehive**. Let agents teach, argue, check, repair, and keep moving until the work is real. Not one clever answer. A small hive with rules.

This best result is still, fundamentally, **a teacher for humanity**.

### Why Swarms?

Feynman would explain the same thing to a freshman, a colleague, and a child in three different ways. Three angles reveal what one angle hides.

Through **competition**, agents expose blind spots. Through **research**, they map the ground. Through **execution**, they ship. Through **optimization**, they refine. Through **migration**, they carry useful craft from one toolchain to another.

**b3ehive** is not just code generation. It is collective work shaped like the scientific method: hypothesize, test, debate, conclude, then leave evidence.

---

## Three Introductions

| English | 中文 | 日本語 |
|---|---|---|
| **b3ehive** is a collection of five swarm algorithms for agent work. Each skill has a narrow job, a hard boundary, and a cleanup rule. The point is not to sound smart. The point is to finish with traces you can inspect. | **b3ehive** 是一组面向 agent 工作的五个蜂群算法。每个 skill 都有明确职责、边界和收尾规则。目标不是说得漂亮，而是把事情做完，并留下能检查的证据。 | **b3ehive** は、agent 作業のための五つの swarm algorithm です。それぞれの skill は役割、境界、終了条件を持ちます。賢そうに見せるためではなく、検証できる形で仕事を終えるための道具です。 |

---

## The Five Hive Skills

| Skill | English | 中文 | 日本語 |
|---|---|---|---|
| `debating-cron-builder` | Three agents build, criticize, revise, vote, and produce the final repair path. Best when the answer needs pressure from more than one mind. | 三个 agent 并行产出、互相批评、更新、投票，再给出最终修复路径。适合需要多角度压测的任务。 | 三つの agent が並行して作り、批評し、直し、投票し、最後の修復方針を出します。複数視点で詰めたい仕事に向きます。 |
| `execution-cron-builder` | Turns one blueprint into a bounded execution cron: daily todo, isolated clone, validation gate, checkpoint, cleanup. It ships code only when the gate is real. | 把一个 blueprint 变成持续执行的 cron：每日 todo、隔离 clone、验证门、checkpoint、完成后清理。只有真实通过 gate 才算完成。 | 一つの blueprint を実行 cron に変えます。daily todo、隔離 clone、validation gate、checkpoint、cleanup まで持ちます。gate を通った実装だけを完了扱いにします。 |
| `research-cron-builder` | Walks a codebase, writes research notes, tracks progress, runs workers, rotates keys, and stops itself when the map is complete. | 持续扫描代码库，写 research 文档，追踪进度，并行跑 worker，轮换 key，完成后自动停掉。 | コードベースを読み、research docs を書き、進捗を追い、worker と key rotation を管理し、完了したら自分で止まります。 |
| `optimization-cron-builder` | Starts from a design idea, derives a bounded AR blueprint, researches each item, and pushes the repo toward clearer architecture. | 从设计理念出发，生成有边界的 AR blueprint，逐项研究，把仓库推向更清晰的架构。 | design philosophy から bounded AR blueprint を作り、項目ごとに調査し、repo をより明快な architecture へ寄せます。 |
| `migration-cron-builder` | Converts Claude-first assets into Codex-ready artifacts one by one, with validation and cleanup. Useful craft should travel cleanly. | 把 Claude-first 的 agents、skills、hooks、rules、docs、templates、settings 逐个迁移成 Codex 可用资产，并做验证和清理。 | Claude-first の assets を Codex-ready な成果物へ一つずつ移します。検証と cleanup 付きです。良い craft をきれいに運びます。 |

---

## Install

Clone the whole hive:

```bash
git clone https://github.com/weiyangzen/b3ehive.git
```

Install all five Codex skills:

```bash
for skill in debating-cron-builder execution-cron-builder research-cron-builder optimization-cron-builder migration-cron-builder; do
  cp -a "b3ehive/$skill" ~/.codex/skills/
done
```

## Quick Start

Run the original debating flow in dry-run mode:

```bash
python3 debating-cron-builder/scripts/debating_cron_builder.py \
  --task "Implement a thread-safe rate limiter" \
  --output ./debating-runs/rate-limiter \
  --runner mock
```

For a repository-local cron, call the matching skill by name:

```text
Use execution-cron-builder for this repo and this blueprint.
Use research-cron-builder to research this codebase.
Use optimization-cron-builder with this design philosophy.
Use migration-cron-builder to migrate Claude assets to Codex.
```

## What Makes b3ehive Different

| Traditional AI | b3ehive |
|---|---|
| Single answer | **Swarm process** |
| One-shot output | **Iterative refinement** |
| Hidden reasoning | **Inspectable artifacts** |
| "Trust me" | **Pass the gate** |

## Repository Map

- [debating-cron-builder](debating-cron-builder/SKILL.md) — three-agent debate and selection
- [execution-cron-builder](execution-cron-builder/SKILL.md) — blueprint-driven implementation cron
- [research-cron-builder](research-cron-builder/SKILL.md) — code research cron
- [optimization-cron-builder](optimization-cron-builder/SKILL.md) — design-guided optimization cron
- [migration-cron-builder](migration-cron-builder/SKILL.md) — Claude-to-Codex migration cron
- [SKILL.md](SKILL.md) — original PCTF debating specification
- [config.yaml](config.yaml) — root configuration

## The Name

**b3** = Build x 3  
**hive** = Swarm intelligence

> **Build x3, evaluate each other, and evolve.**  
> So called b3ehive.

## License

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))

---

*"What I cannot create, I do not understand."* — Richard Feynman
