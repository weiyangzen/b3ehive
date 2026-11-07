# Looper Lessons

Rules moved out of the v1 SKILL.md body. They stay binding where the v2 text
points here.

| v1 source | v2 location |
|---|---|
| Controller Contract, 19 objects | SKILL.md Objects (6) and `references/schemas.md` |
| LoopSpec, Resources And Leases, Bridge Control | `references/schemas.md` |
| SideEffectGate (9 types), OperatorSignal (13) | SKILL.md Governance (6 classes, 5 signals); full lists in `references/schemas.md` |
| Nested Runs, EvidenceLedger, LooperLog | `core.md` Compose and law 7; `references/schemas.md` |
| Reward, Pause, Resume | SKILL.md Governance; `loop.md` |
| `b3ehive-bridge-contract.md` | `core.md`; schemas in `references/schemas.md`; B3IR section removed until an implementation exists |
| `bridge-control.md`, `looper-pattern.md` | `references/schemas.md`; this file |
| Output Discipline | `core.md` Practice: Write |

Origin: 4a8265a (looper), 9a89ec1 (bridge control), f054d11 (shared contract).

## Concurrency Model

Looper adds a third cursor to b3ehive's existing worker/master pattern:

```text
DAG Claim Cursor:
  fills normal worker lanes from [ ] DAG items.

Loop Attempt Cursor:
  fills loop daemon lanes from eligible loops with active resource envelopes.

Master Integration Cursor:
  validates [_] outputs and looper candidates in DAG dependency order.
```

Required scheduler order:

1. Read authoritative blueprint, bridge surfaces, bridge signals, loop ledgers,
   and resource ledgers.
2. Process pending operator signals.
3. Release expired leases and dead daemons.
4. Cheaply refresh finished attempt state.
5. Refill normal DAG workers first so core implementation does not starve.
6. Rank eligible loops by bridge priority, ROI, reward recency, and urgency.
7. Allocate leases through the resource broker.
8. Start or wake loop daemons.
9. Defer heavy ROI reports until after worker refill or behind an explicit
   refresh flag.
10. Let the master lane integrate validated candidates in DAG order.

High-concurrency rules:

- Finished attempts do not consume live worker capacity.
- Heavy integration or ROI scans must not block worker refill.
- Dependent loop outputs remain provisional until dependencies are `[x]`.
- Path-overlapping attempts must run in isolated workspaces.
- Resource broker, not individual daemons, controls global concurrency.
- Master lane resolves conflicts and writes accepted `[x]` marks.

## Common Failure Modes

- adding feedback edges directly to the DAG and creating cycles
- treating `BridgeMetric` as the only bridge type
- recording bridge movement without before/after refs
- counting bridge deltas as reward before master classification
- starting attempts without resource leases
- letting nested compete, learn, execution, or optimization runs escape parent
  lease accounting
- letting paused loops start nested runs
- allowing workers to mutate protected authoritative surfaces
- treating operator cancel or drain as best-effort instead of authoritative
  loop state
- using full transcript review when compact evidence would suffice
- treating no-reward attempts as harmless retries
- resuming a paused loop with the same strategy and fresh budget only
- measuring token spend but not human review time or disk/log pressure
- counting narrative summaries as reward without evidence
- treating looper_log as accepted policy/tool/skill change
- mutating an InstrumentObject during the same runtime attempt that first
  observed the instrument feedback
- allowing daemon workers to write `[x]`
- letting heavy ROI reporting block worker refill
- committing private metric names, local paths, or customer identifiers

## Project-Specific Extensions

Core Looper machinery excludes:

- plan-understanding quizzes
- draft relevance checkers
- read validators
- full transcript compliance judges
- dense prompt-template validators
- hook chains around every operation
- separate long-term feedback subsystem
- separate looper-log public skill
- new public bridge or feedback skill

An explicit project requirement may add one of these as a project-specific
validator or side-effect gate under an existing loop. It stays outside core
Looper machinery.

## Privacy And Generalization

Generated looper specs, docs, prompts, ledgers, and examples stay
project-neutral. An explicit user request for a private, local-only artifact
permits private content only in that artifact.

The following data stays out of public or committed Looper artifacts:

- private repository names
- customer names
- local absolute paths
- personal evidence directories
- internal product codenames
- private strategy document paths
- raw user conversations or account identifiers
- vendor secrets, API keys, or billing identifiers

Use generic labels such as `product_beta`, `repo_maintenance`,
`benchmark_lane`, `claim_audit`, `customer_workflow`, `growth_experiment`, and
`ops_review`. Private names required for local execution stay in `.cron/`,
`.ops/`, `.b3ehive/looper/*.local.*`, or another ignored surface.

## 2.2.0

`replan` before pause, novelty as secondary reward, no-spend closeouts; loop v2 owned here.
