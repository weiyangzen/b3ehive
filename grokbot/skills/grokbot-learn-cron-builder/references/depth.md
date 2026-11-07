# Learn Depth

`learn_depth` sets how far each artifact explains. Levels are cumulative.

| Level | Answers | Default route |
|---|---|---|
| `what` (default) | what the source is and does, or what was produced | per `route-policy.md` |
| `how` | which quality principles the work follows, with evidence | standard or high reasoning |
| `why` | why it is built or rendered this way, and why that beats the alternatives | high reasoning; `review` loop shape |

`depth_map` may raise or lower depth by glob, for example `why` for `src/core/**`
and `what` elsewhere. Log the level and map as `DECIDE` lines in
`Docs/learn/route_decision.md`.

## Placement

- `understand`: sections `## What`, `## How`, `## Why` inside each per-file and
  per-folder note; one-to-one coverage stays unchanged.
- `transform`, `translate`: the target artifact stays clean. How and why go to a
  companion note mirroring the source tree:
  `Docs/learn/rationale/<source_path>_rationale.md` and
  `Docs/learn/rationale/<folder>/current_folder_rationale.md`, indexed in
  `Docs/learn/rationale_index.tsv`.
- `canon`: how and why go into `canon/excerpts/<id>.md`.

## What Each Level Covers

### How: principles followed, each with evidence

| Mode | Principles to name |
|---|---|
| `understand` | invariants the code upholds; error and failure handling; concurrency and state discipline; performance techniques; interface contracts; test strategy; naming and structure conventions; places where the code departs from its own principles |
| `transform` | behavior parity; target idioms over literal translation; traceability; test parity; incremental verifiability; reversible mapping |
| `translate` | terminology fixed by glossary; register and audience; meaning over word order; structural parity; locale conventions; handling of untranslatable terms |
| `canon` | conditions under which the entry applies; common misreadings; how to verify compliance |

Every principle cites evidence: `path:line`, a test, a mapping row, a diff, or
a glossary entry.

### Why: reasons, alternatives, and depth

Each significant decision gets one entry with five fields:

- **driver**: the constraint or goal that forces the choice: correctness,
  performance, compatibility, cost, team, history, or a cited canon entry.
- **alternatives**: at least one realistic alternative and the concrete reason it
  is worse here; or `none viable` with the reason.
- **tradeoff**: what the choice gives up.
- **significance**: the principle the choice embodies beyond this file, and what
  breaks if someone changes it.
- **level**: `V` when the reason is stated in code comments, commit messages,
  docs, design records, issues, or canon (cite it); `I` when inferred. An `I`
  reason reads as an inference ("likely because"), never as fact.

## Format

```markdown
## What
<purpose, entry points, flow, data, dependencies, side effects, risks, unknowns>

## How
- Single writer per ledger — evidence: `src/ledger.py:41`
- Retries stay idempotent through request keys — evidence: `tests/test_retry.py::test_replay`

## Why
### Single writer per ledger
- driver: concurrent appends corrupted rows (commit `a1b2c3d`)
- alternatives: file locks per append — worse: slower and fails on network disks
- tradeoff: writes queue behind one process
- significance: ordering lives in one place, so recovery replays a single log
- level: V (commit `a1b2c3d`)
```

## Acceptance

- The item's oracle adds `scripts/check_depth.py`: required sections exist for
  the item's depth; every how line cites evidence; every why entry carries all
  five fields with a valid level.
- At `why` depth, a non-author reviewer judges a sample of entries against the
  source and its history; an unsupported `V` drops to `I` or the entry is
  rejected.
- Folder notes at `how` or `why` depth explain the decomposition: why these
  modules, these boundaries, this dependency direction.

```bash
python3 scripts/check_depth.py --depth why Docs/learn/files
python3 scripts/check_depth.py --depth how Docs/learn/rationale
```
