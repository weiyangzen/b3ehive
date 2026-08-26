---
name: b3ehive
description: Root guide for b3ehive's five portable swarm skills: compete, execution, learn, optimization, and looper cron builders for Codex, Claude Code, Cursor, Grok Build, opencode, OpenClaw, and Hermes.
---

# b3ehive Skill Index

b3ehive provides five portable `SKILL.md` directories:

- `compete-cron-builder`: bounded proposal competitions with `n` workers,
  `m` proposals, choose `k`, all-valid coverage union, repair queues, blueprint
  synthesis, and three-way challenge artifact coverage.
- `execution-cron-builder`: blueprint-driven DAG execution with worker/master
  cursors, validation gates, checkpointing, and cleanup.
- `learn-cron-builder`: source-to-target learning cron for code understanding,
  subset learning, code-to-code transform, and human-language translation.
- `optimization-cron-builder`: design-guided architecture and optimization
  cron.
- `looper-cron-builder`: resource-aware bridge controller for DAG nodes,
  BridgeSurfaces, BridgeMetrics, ResourceEnvelopes, ResourceLeases,
  SideEffectGates, OperatorSignals, nested run ledgers, compact evidence,
  reward ledgers, ROI, and no-reward pause.

Shared invariants across all five skills:

- `[ ]`, `[_]`, and `[x]` are the only authoritative acceptance states.
- Runtime labels such as paused, cancelled, done, accepted, or finalized are
  telemetry unless paired with the checkbox state.
- Auto choices should use `EstimatorPolicy`; hardcoded values must be hard caps
  for AI boundaries, safety, compatibility, or operator overrides.
- Nontrivial skill selection, model/provider choice, and nested skill
  composition should leave a `RouteDecision`.
- Nested skill calls require route, lease, evidence, side-effect, depth, and ROI
  controls; child skills cannot write `[x]`.
- Evidence lint, not narrative confidence, gates acceptance.
- `LooperLog` is the shared multi-grain feedback surface for `TargetObject`
  movement and `InstrumentObject` quality across micro, skill, composition,
  scaffold, tool, and task grains. It is evidence/backlog, not accepted policy
  change.
- Normal execution may change the target object inside the task boundary.
  Instrument changes to skills, scaffolds, validators, routes, ledgers, scripts,
  or tools require a separate `[ ]` -> `[_]` -> `[x]` improvement lifecycle.
- Self-evolution requires EvidenceLint, ROI, ParetoGate, rollback, and master
  `[x]`.
- Prompt blocks, hooks, validators, and coding-tool glue are generated
  engineering artifacts unless promoted by evidence; do not grow a prompt/hook
  forest inside the five core skills.

Read `looper-cron-builder/references/b3ehive-bridge-contract.md` for the shared
contract when updating skills, generating coding-tool adapters, using nested
skills, or designing route/evidence/looper_log/ROI/self-evolution behavior.
