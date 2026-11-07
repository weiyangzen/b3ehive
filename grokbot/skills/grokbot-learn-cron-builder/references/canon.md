# Canon

A canon is a pinned subset of outside knowledge that governs decisions: specs,
datasheets, official guides, source code, documentation MCP answers, and
curated wikis. Learn builds it; every skill cites it.

## Layout

```text
canon/manifest.tsv          one row per entry
canon/excerpts/<id>.md      excerpt or synthesis, when the license allows
ref/raw/                    original snapshots, git-ignored
instruments.tsv             measurement tools, kept apart from knowledge
```

## Manifest Columns

| Column | Meaning |
|---|---|
| `id` | stable short id: `A2`, `SPEC-12§4.4`, `PTX-ISA§9.7` |
| `locator` | URL, repository path, or `mcp:<server>:<tool>?q=<query>` |
| `version` | document version, release tag, or commit |
| `retrieved` | retrieval date |
| `sha256` | hash of the snapshot or excerpt; detects drift |
| `mode` | `verbatim`, `extracted`, or `derived` |
| `level` | `V` primary source, `F` forum or community, `I` inference awaiting a gate |
| `license` | `excerpt-ok`, `pointer-only`, or the SPDX id |
| `governs` | item or decision ids this entry constrains |

## Lessons And Incidents

Canon also holds experience: `canon/lessons.tsv`, one row per lesson or incident.

| Column | Meaning |
|---|---|
| `id`, `kind` | stable id; `lesson` or `incident` |
| `trigger` | the situation or symptom that should recall this row |
| `evidence` | where it was observed: commit, receipt, log, ticket |
| `cause` | root cause (incidents) |
| `action` | what to do: the durable repair or the future behavior |
| `validation` | how to tell the action worked |
| `stop` | when to stop applying it |
| `limits` | where it does not apply |
| `governs` | items, skills, or decisions it constrains |
| `applied` | `applied`, `not_applied`, or `refuted` at the last use |
| `helpful` | `helpful`, `harmful`, `neutral`, or `unknown`; stays `unknown` without independent evidence |

Rules:

- A lesson enters only after the oracle or a non-author reviewer validated the
  attempt it came from; a turn summary never enters.
- A lesson is active only when `find_lesson.py activate <id> "<use-site query>"`
  recalls it; a successful write proves nothing.
- Look up before acting: `find_lesson.py search "<symptom>"` returns at most 20
  summaries; read a full row with `show <id>`.
- Evidence strength ranks owner correction above controlled replay, replay above
  deterministic effect, effect above evaluator judgment; a weaker signal never
  flips a stronger one.
- A lesson grants no authority. `harmful` proposes retirement; the master
  accepts it.
- Repair the layer that owns the data; never raise a limit or timeout to hide
  an incident.

```bash
python3 scripts/find_lesson.py --ledger canon/lessons.tsv search "stale lease blocks refill"
python3 scripts/find_lesson.py --ledger canon/lessons.tsv check
```

## Building

1. Lock the scope: which decisions need outside facts.
2. Query domain MCP servers first, then official sources, then community.
3. Snapshot each answer; MCP output changes between calls.
4. Write one row per fact cluster; split rows that govern unrelated decisions.
5. Mark inferences `I` and add the gate that would confirm them.
6. Submit rows as `[_]`; the master accepts after checking locators and hashes.

## Using

- Cite by id in evidence rows and `DECIDE` lines: `canon: [A2]`.
- Read the entry a decision needs; never paste the whole canon into a prompt.
- An `I` entry blocks acceptance of dependent items until its gate passes.
- Measure the canon's value by ablation; drop entries that change no decision.

## Auditing

- Re-hash snapshots; a changed hash reopens the entry.
- Track upstream corrections and newer versions.
- Prune wrong or unused entries; record each removal in the manifest history.
- Enforce licenses with a generated check, not a note.
