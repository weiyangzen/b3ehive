---
name: b3ehive
description: Index of b3ehive 3.0's five portable swarm skills (compete, execution, learn, optimization, looper) with multi-layer blueprint stacks, Occam anti-Cartesian factoring, and Lean 4 formal verification.
---

# b3ehive

For user-facing orientation, read `docs/getting-started.md` and
`docs/skill-selection.md`. The public writing rules live in
`docs/writing-style.md`.

| Skill | Use |
|---|---|
| `compete-cron-builder` | hard choices, repair search, audits, coverage |
| `execution-cron-builder` | one blueprint executed as a DAG |
| `learn-cron-builder` | understand, transform, translate, build a canon |
| `optimization-cron-builder` | measured performance work or design refinement |
| `looper-cron-builder` | the shared loop and budget governance |

Grokbot set: `grokbot/grokbot-<skill>-skill.zip`, unzipped into
`~/.claude/skills/`. Only grokbot loads it; every subagent runs only as
`claude --dangerously-skip-permissions`. Source: `scripts/build_grokbot.py`.

Shared law: `core/core.md`, copied into each skill's `references/core.md`.
Shared loop: `looper-cron-builder/loop.md`, copied into the other four skills.
Formal verifier: `formal/b3lean/` (Lean `v4.34.0`, zero Mathlib), invoked via `bin/b3ehive verify-lean`.
