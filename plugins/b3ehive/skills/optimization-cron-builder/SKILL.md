---
name: optimization-cron-builder
description: Improves a system against a declared objective. Design mode writes one research doc per refinement item; measured mode compares candidates serially under a frozen oracle. Use for performance work such as CUDA kernels, or for design refinement. 性能优化、串行比较、架构优化。
---

# Optimization

For a user-facing choice guide, read `docs/skill-selection.md`. Use measured
mode when an oracle can measure a target; use design mode for research against a
design philosophy.

core v2 · loop v1; measured mode binds the frozen benchmark as the oracle and
keeps the ratchet. Read `references/core.md` and `references/loop.md` first;
this body adds only optimization rules.

Measured optimization normally compares candidates in series. It measures one
candidate, keeps or reverts it, and uses the result to choose the next
candidate. Use parallel `lanes` only when independent hypotheses need one
comparison round.

## Modes

| Mode | Input | Output |
|---|---|---|
| `design` | a design philosophy and a stage blueprint | `Stage_*_AR_Blueprint.md` and one research doc per item |
| `measured` | an objective and an oracle contract | accepted changes with before/after measurements and a hypothesis ledger |

Decide the mode. A request to make something faster, smaller, or cheaper takes
`measured`; a request to refine architecture against a philosophy takes `design`.

## Measured Mode

1. Contract. Freeze the oracle contract: definition, workloads drawn from real
   use, reference, tolerance, measurement method, baseline with source and
   version, anti-gaming checks, `oracle.fast` and `oracle.full`, tier.
   Template: `references/measured-mode.md`.
2. Baseline. Measure the baseline under the contract; profile it with a bound
   instrument.
3. Hypothesis. Each entry names its profile evidence, cited canon, expected
   gain, and the change.
4. Candidates. Run the loop: `single` by default, `relay` for stubborn targets,
   and serial comparison for the normal ratchet. Use `lanes` when independent
   hypotheses need one parallel comparison round.
5. Re-measure. The master re-runs `oracle.full` on fresh inputs and recomputes
   aggregates from raw rows; agent-reported speedups count for nothing.
6. Ratchet. Keep a change only when it is correct and better; otherwise revert.
7. Record. Log every outcome, rejected ones included; a rejected hypothesis
   returns only with new evidence.

Stop on target reached, budget spent, or a written reason the target is out of
reach. Never relabel a missed target as success.

## Instruments

- Bind profilers, analyzers, and domain skills (for example `ncu`, `nsys`,
  `perf`, `py-spy`, an ncu report skill, a kernel wiki, a docs MCP server) in
  `instruments.tsv` with a probe command; a failed probe means the instrument
  is absent.
- Each instrument carries a playbook: signals → cause → first fix → deeper
  fixes → exceptions. Rank at most five priorities by expected gain over effort.
- Name the two or three measured values behind each diagnosis.
- b3ehive bundles no domain knowledge; domain packs enter through canon and
  instruments.

## Design Mode

1. Capture the philosophy in one stable sentence.
2. Generate one authoritative `Docs/Stage_*_AR_Blueprint.md`: one item per
   optimization topic, at most 100 items (a review-capacity cap), grouped into
   worker-ownable sections.
3. Each item gets one doc under `Docs/researches/Stage_*_AR/`, scoped to that
   item, filtered through the philosophy, grounded in mature practice and cited
   canon, ending in concrete recommendations for this repository.
4. Decide the worker count from the sections; workers own disjoint sections.
5. An empty, broad, or off-philosophy doc keeps its item open; split or narrow
   it and rerun only that section.

Product code stays downstream of design mode. Detail and repair:
`references/design-mode.md`.

## Validation

- Measured: the baseline reproduces; every accepted change has before and after
  receipts on fresh inputs; the hypothesis ledger covers every attempt.
- Design: one authoritative AR blueprint, at most 100 items, one non-empty
  scoped doc per accepted item.
- Generated shell passes `bash -n`; the cron space guard passes.

## References

- `references/core.md`, `references/loop.md`: shared laws and loop
- `references/measured-mode.md`: oracle contract, ledgers, instruments
- `references/design-mode.md`: AR blueprint, research docs, repair
- `references/substrate-cron.md`: cron, runners, disk guards
- `references/lessons.md`: where each v1 rule now lives
