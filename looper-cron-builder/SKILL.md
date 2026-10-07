---
name: looper-cron-builder
description: Defines an optional external loop layer that sets granularity and governs repeated attempts with leases, side-effect gates, reward and ROI ledgers. Use when a loop must attach to an item, metric, or surface, or when several loops share a budget. 循环、粒度、预算、ROI。
---

# Looper

For a user-facing choice guide, read `docs/skill-selection.md`. Use this skill
when an explicit external loop must set granularity or govern shared resources.
The smallest work unit is normally internal to the selected skill.

core v2 · owner of loop v1. Read `references/core.md`, then `loop.md`.

Looper has two layers. It owns `loop.md`, the shared attempt-loop definition
that the other four skills bind by name. The `looper-cron-builder` skill is an
optional external definition: it attaches a loop to an item, metric, or surface
and sets its granularity, budget, and governance. A small internal loop can use
`loop.md` without a separately named looper definition.

## Objects

| Object | Holds |
|---|---|
| Loop | target (item, metric, or surface), oracle, budget envelope, attachment point |
| Lease | budget slice for one attempt: tokens, time, money, disk, diff size, TTL, heartbeat, owner, workspace |
| Attempt | hypothesis, shape, receipt, `ADVANCED` / `STALLED` / `REGRESSED` |
| Evidence row | changed paths, commands, results, side-effect decisions, nested-run refs, reward class |
| Decision | `continue`, `pause`, `split`, `lower`, `raise`, `escalate`, or `retire` |
| Friction note | instrument, effect (`helped`, `blocked`, `wasted`, `under-validated`), evidence, suggestion |

Field schemas, bridge levels, signal types, and the full ledger set live in
`references/schemas.md`. Use them when a loop needs them; omit the rest.

## Governance

- No lease, no attempt. Release expired leases and dead owners before issuing
  new ones.
- Process operator signals before new leases: `cancel`, `drain`, `pause`,
  `resume`, `replan`. `cancel`, `drain`, and `pause` block new leases.
- Gate side effects of these classes only: push or publish, spend or network,
  delete or broad write, protected or authoritative paths, secret exposure,
  identity-level writes. Ordinary reads and owned-path edits pass ungated.
- Refill normal DAG workers before loop attempts; run heavy ROI reports after
  refill.
- Rank eligible loops by priority, ROI, reward recency, and urgency; the
  envelope, not each daemon, caps global concurrency.
- Classify reward after evidence exists. Primary reward clears the no-reward
  counter; secondary reward lowers it; negative or empty output raises it.
- Nested skill runs spend the parent lease and submit candidates; the parent
  classifies reward.
- Same loop, same strategy, and no reward never runs again.

## Workflow

1. Inspect the repository: bridge targets, metrics, DAG nodes, oracles,
   resource limits.
2. Write sanitized loop specs to `Docs/looper/`; keep private names, paths, and
   ledgers under ignored `.b3ehive/looper/` and `.cron/`.
3. Generate the broker, lease allocator, gate evaluator, signal reader, daemon
   runner, ledgers, ROI accountant, space guard, installer, and cleanup.
4. Run `VALIDATE_ONLY=1`, then one manual tick on a tiny envelope.
5. Install cron after validate-only, the manual tick, the budget guard, and the
   privacy scan pass.
6. Clean up only with no live lease, no unaccounted attempt, no unfinished
   nested run, no open attached item, and no pending signal.

## Validation

- Specs, envelopes, leases, and ledgers parse.
- Every loop attaches to an item, metric, or surface and names an oracle or
  monitoring source.
- Every attempt holds a lease; nested spend rolls into the parent.
- Pending signals precede new leases; protected side effects carry decisions.
- A paused loop refuses resume without new budget and a changed strategy.
- Generated shell passes `bash -n`; the privacy scan finds no private names or
  absolute paths in committed files.

## Ablation

`B3_LOOP=full|single|null` swaps the loop variant for every skill at once.
`B3_LOOPER_GOVERNANCE=off` runs loops on their leases alone. Evaluations in
`evals/` compare both switches; the loop keeps its own version number.

## References

- `loop.md`: the loop definition, synced into the other skills
- `references/core.md`: shared laws
- `references/schemas.md`: every looper schema and enumeration, once
- `references/privacy-checklist.md`: publication hygiene
- `references/substrate-cron.md`: cron, runners, disk guards
- `references/lessons.md`: v1 rules moved out of this body
