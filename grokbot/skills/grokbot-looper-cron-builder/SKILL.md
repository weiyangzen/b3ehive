---
name: grokbot-looper-cron-builder
description: Grokbot only. Subagents run only as claude --dangerously-skip-permissions. Defines an optional external loop layer that sets granularity and governs repeated attempts with leases, side-effect gates, reward and ROI ledgers. Use when a loop must attach to an item, metric, or surface, or when several loops share a budget. 循环、粒度、预算、ROI。
---

# Looper (grokbot)

## Grokbot Gate

Grokbot build of `looper-cron-builder`, b3ehive 2.3.1.
This section overrides every runner, platform, transport, and subagent rule in
this skill and in its references.

Load:

- Only grokbot loads this skill. Grokbot installs it with the command below
  and names the subagent runtime explicitly:
  `unzip grokbot-looper-cron-builder-skill.zip -d ~/.claude/skills/`
- Any other host stops here and loads nothing from this directory: Claude Code,
  a `claude` subagent that grokbot started, Codex, Cursor, Grok Build without
  grokbot, opencode, OpenClaw, and Hermes. Those hosts use the base skill
  `looper-cron-builder` instead.

Subagent runtime:

- Every subagent call uses only `claude --dangerously-skip-permissions` as its
  agent runtime. This covers workers, reviewers, verifiers, voters, repair
  generations, nested runs, and in-session subagents.
- Runner template, also the value of `B3EHIVE_AGENT_RUNNER`, with
  `B3EHIVE_AGENT_PLATFORM=claude`:

  ```bash
  claude -p --dangerously-skip-permissions \
    --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
    --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
  ```

- No other runtime: no Grok subagent or task tool, no `grok`, `codex`, Cursor,
  opencode, OpenClaw, or Hermes worker, no Codex TUI transport, and no
  `--permission-mode` flag. Where the body or a reference names another runner,
  read this runtime.
- A runner that does not start with `claude -p --dangerously-skip-permissions`
  fails closed with its value. A missing `claude` binary stops the run with
  `user_action_required`; there is no fallback.
- The flag removes every permission check, so the task root is the only fence.
  `--add-dir` names the claim workspace only, never the canonical checkout or
  `$HOME`. Each subagent still counts against every cap and lease.
- Each subagent prompt states its role and tells it not to load any
  `grokbot-*` skill.
- Validate-only output prints `platform=claude`,
  `runtime=claude --dangerously-skip-permissions`, and the resolved runner.

For a user-facing choice guide, read `docs/skill-selection.md`. Use this skill
when an explicit external loop must set granularity or govern shared resources.
The smallest work unit is normally internal to the selected skill.

core v2 · owner of loop v2. Read `references/core.md`, then `loop.md`.

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
| Attempt | hypothesis, direction, shape, receipt, result (loop v2 vocabulary) |
| Evidence row | changed paths, commands, results, side-effect decisions, nested-run refs, reward class |
| Decision | `continue`, `replan`, `pause`, `split`, `lower`, `raise`, `escalate`, or `retire` |
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
- A stalling loop gets a `replan` decision before any pause; pause follows only
  when the replan obligation is still open at the third stall.
- Novelty is secondary reward: an attempt that adds evidence ids or observation
  keys absent from the loop's history lowers the no-reward counter; a replayed
  or renamed claim does not.
- An attempt that produces no state transition closes without spending its
  lease; record the no-spend closeout.

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
