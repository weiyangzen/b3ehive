# b3ehive loop v2

A loop repeats attempts on one item until its oracle passes and the master
accepts, or until its lease ends.

This file defines loop mechanics. `looper-cron-builder` is an optional external
layer that chooses the attachment and granularity of a loop. The selected skill
usually handles its smallest work unit internally.

## Shapes

- `single`: one worker per attempt.
- `relay`: model families alternate; each turn opens a fresh session; the
  repository and its notes are the only memory.
- `review`: an actor works; each round a fresh, read-only, non-author reviewer
  judges the repository, not the actor's summary.
- `lanes`: attempts run in parallel; compete selects.

## Results

Each attempt submits a receipt and ends in exactly one result:
`validated_progress`, `repair_required`, `replan_required`,
`user_action_required`, `wait`, or `failed`. Code routes on the result field,
never on prose. Only `validated_progress` with its receipt counts as progress; a
repair that leaves the open work unchanged is `repair_noop`, which counts as a
stall.

## Direction

Each attempt names its direction: `grow` (extend what works), `switch` (change
mechanism), or `verify` (test a belief). It states the slice size, the mechanism
distance from the incumbent, and the evidence breadth it targets. Each lineage
gets one remediation for a data or measurement gap; the next attempt in that
lineage switches mechanism.

## Rules

- Ratchet: keep a change only if the oracle measures it correct and better than
  the best accepted state, not merely the previous attempt; otherwise revert.
- Two stalls open a replan obligation whose id hashes its trigger. A replan
  clears it only by citing evidence absent from the stalled window; a restated
  plan is `replan_noop`. Three stalls: pause the loop and report why.
- Untrusted evidence (replay or measurement below the declared fidelity) is
  `observed_only`: kept for review, never ranked, never treated as a rejection.
- Log each rejected hypothesis with its measurement; retry it only on new evidence.
- A verdict that can end a loop carries a round cap.
- Iterate on `oracle.fast`; submit on `oracle.full`.
- An item closes with a successor item, a `wait` naming `resume_when`, or an
  explicit `no_followup`; anything else is a gap the master reopens.
- Paused loops resume on new budget and a new strategy, never alone.

## Ablation

`B3_LOOP=full|single|null` selects the module variant: all shapes, `single` only,
or one attempt without retry. `B3_REPLAN_OBLIGATION=off` falls back to pause on
the third stall. Evaluations compare variants; the loop version changes apart
from core.
