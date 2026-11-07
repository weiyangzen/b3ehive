# Measured Mode

## Oracle Contract

Freeze this before any candidate runs. Workers read it and never edit it.

| Field | Meaning | CUDA kernel example |
|---|---|---|
| definition | inputs, outputs, shapes, types, layout | shapes, dtypes, strides |
| workloads | cases drawn from real use, covering its dynamic range | sampled production traces |
| reference | a trusted implementation | PyTorch or CPU version |
| tolerance | what counts as correct | element-wise bound, relative L2, all finite, state error |
| measurement | how numbers are taken | warmup, repeats, events or CUPTI, cold cache, locked clocks |
| baseline | best known implementation with source and version; never chosen by the agent | current SOTA kernel |
| anti-gaming | checks a gamed result fails | refill inputs after timing and re-check; secret seeds; holdout cases; evaluator outside the workspace |
| `oracle.fast` | quick check for iteration | one shape |
| `oracle.full` | acceptance check | every shape, fresh inputs |
| tier | evidence fidelity needed for acceptance | named GPU model |

## Ledgers

`hypotheses.tsv`:

| Column | Meaning |
|---|---|
| `id` | stable id |
| `lineage` | hypothesis family; one remediation per lineage, then switch mechanism |
| `parent` | candidate it builds on |
| `direction` | `grow`, `switch`, or `verify`, with mechanism distance from the incumbent |
| `evidence` | profile values behind it |
| `canon` | cited entries |
| `expected` | predicted gain |
| `measured` | `oracle.full` result on fresh inputs |
| `decision` | `kept`, `reverted`, `rejected`, or `observed_only` |
| `reason` | one line |

`candidates.jsonl` holds one row per candidate: parent, change summary, receipt
path, per-workload rows, and the aggregate recomputed by the master.

## Statistics

Set `B3_STATS=on` (default in measured mode). A comparison counts only when:

- Each arm runs at least N paired trials; decide N from pilot variance, never
  below 5 for acceptance.
- Trials alternate baseline and candidate (`ABBA`, `BAAB`), each in a fresh
  process, with warmups excluded and recorded.
- The confidence interval of the paired difference excludes zero and its lower
  bound clears the declared minimum effect.
- Every metric reported keeps its interval; a metric whose interval crosses zero
  is reported as unchanged, never as a gain.
- The measured revision and the merged revision are recorded separately; numbers
  for one never stand for the other.

## Experiment Identity

Hash into each trial key: source revision, build flags, compiler and runtime
versions, the full dependency closure, driver and firmware, device model, clocks,
and the oracle contract digest. A trial whose identity differs from its pair is
discarded, not averaged.

## Instruments

`instruments.tsv`:

| Column | Meaning |
|---|---|
| `id` | `ncu`, `nsys`, `perf`, `py-spy`, `explain` |
| `probe` | command proving the instrument exists; failure means absent |
| `capability` | what it measures |
| `skill` | bound domain skill, if any |
| `playbook` | diagnosis playbook path |

Playbook entries read: signals → cause → first fix → deeper fixes → exceptions.

## Loop Discipline

- Shorten feedback: iterate on one workload with `oracle.fast`, widen with
  `oracle.full` before submitting.
- Change one thing per candidate; keep alternatives switchable for paired
  measurement.
- A stalled direction stops after five attempts unless new evidence appears.
- Stop reasons are exact: `target_reached`, `budget_spent`,
  `no_actionable_bottleneck`, `capability_exhausted`, `reference_parity`, or a
  written blocker.
