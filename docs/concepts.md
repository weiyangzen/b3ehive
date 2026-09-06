# b3ehive Core Concepts

[中文](concepts.zh-CN.md)

> This document gives new users a compact map of b3ehive's design philosophy and
> key abstractions.

---

## 1. Why A Hive?

### 1.1 The Feynman Technique

b3ehive is inspired by Richard Feynman's learning principle:

> **"What I cannot create, I do not understand."**

The practical lesson is simple: if you cannot explain or recreate something in
clear terms, you do not fully understand it yet.

b3ehive brings that idea to AI agent work. Agents should shape a problem, split
the work, execute it, validate the result, and leave an inspectable trail that a
person can repeat or improve.

### 1.2 One Agent Is A Voice. A Hive Is An Arrangement.

| Traditional AI assistant | b3ehive |
|---|---|
| One assistant, one shape | **Five swarm organizations** |
| Prompt in, answer out | **Checklist -> Worker -> Validator -> Cleanup** |
| Hidden state | **Inspectable specs, todos, logs, and artifacts** |
| "Looks done" | **Pass the gate, then checkpoint** |

Different work needs different arrangements:

- **Hard decisions or coverage** need **compete**: proposal competition,
  selection, synthesis, or coverage union.
- **Long implementation** needs **execution**: blueprint-driven work with
  checkpoints.
- **Unknown code, source-to-target conversion, or translation** needs **learn**:
  understand it until make it.
- **Mature systems** need **optimization**: design-guided architecture
  refinement.
- **Repeated validation, bridge surfaces, or metric movement** need **looper**:
  resource-aware bridge control.

`LooperLog` is the looper's multi-grain evidence surface. It records
`TargetObject` movement and `InstrumentObject` quality. Normal execution moves
the target work; looper also observes whether skills, scaffolds, tools, routes,
validators, scripts, and ledgers helped, blocked, wasted resources, or failed
to validate enough. It is not a sixth public skill and it is not a runtime path
for automatically mutating skills.

b3ehive is not just code generation. It is collective work shaped like the
scientific method: observe the ground, choose the right organization, run
bounded cycles, validate honestly, and leave evidence.

---

## 2. Blueprint

A blueprint is the single authoritative requirement source for a b3ehive
workflow.

It is not a static spec. It is a living, executable document with embedded
checklist state (`[ ]`, `[_]`, `[x]`), dependency DAG, and layer structure.
Guards read it to decide what can be worked on today, what is blocked, and what
can be accepted.

> A traditional spec answers "what should be built." A b3ehive blueprint answers
> "what should be built, what state it is in, what is next, and whether it is
> currently allowed to proceed."

See [Blueprint](./blueprint.md) for the detailed contract.

---

## 3. The Five Skills

| Skill | Core capability | Input | Output |
|---|---|---|---|
| `compete-cron-builder` | Multi-proposal competition, selection, union, or repair queue | A local question plus n/m/k budget | Selected candidates, coverage union, repair queue, or blueprint synthesis |
| `execution-cron-builder` | Continuous blueprint execution | One blueprint | Implemented items and checkpoint commits |
| `learn-cron-builder` | Source-to-target learning: understand, transform, translate | Source scope, subset, and target contract | Learning notes, transformed artifacts, translations, traceability |
| `optimization-cron-builder` | Architecture refinement research | Design philosophy and stage blueprint | Research document for each optimization item |
| `looper-cron-builder` | Resource-aware bridge controller | BridgeSurface or BridgeMetric plus ResourceEnvelope, SideEffectGate, and Validator | Bridge deltas, compact evidence, reward/ROI ledger, pause/resume policy |

---

## 4. Name

- **b3** = **B**lueprint, **B**atch, **B**ehavior
- **hive** = Swarm intelligence

> Choose the right swarm, run bounded work, and leave proof.
> So called b3ehive.
