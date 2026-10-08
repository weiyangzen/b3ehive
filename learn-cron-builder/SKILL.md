---
name: learn-cron-builder
description: Turns a frozen source scope into validated artifacts such as one-to-one code understanding, code-to-code transforms, translations, or a pinned canon of normative documents, at a chosen depth of what, how, or why. Use to learn a codebase or spec, migrate code, or translate docs. 学习代码库、规范子集、迁移、翻译、原理与动机。
---

# Learn

core v2 · loop v1; an item's oracle is traceability to its source row, plus the
depth check. Read `references/core.md` and `references/loop.md` first; this body
adds only learning rules. Working frame: understand it until you can make it.

## Modes

| Mode | Direction | Final artifact |
|---|---|---|
| `understand` | code → human language | one note per source file plus one per folder |
| `transform` | code → code, API, schema, runtime, tool asset | target files with source-target traceability |
| `translate` | human language → human language | translated docs with structural parity |
| `canon` | external documents → pinned normative subset | `canon/manifest.tsv` plus excerpts |

Every mode runs:
`scope → subset → manifest → target contract → depth → submissions [_] → master [x] → cleanup`.

## Depth

Decide `learn_depth` per run, and optionally per glob through `depth_map`:

| Level | Adds | Each artifact must show |
|---|---|---|
| `what` (default) | what it is and does | purpose, entry points, flow, data, dependencies, side effects, risks, unknowns |
| `how` | how it is done well | the quality principles followed, each with evidence (`path:line`, test, mapping row, glossary entry), plus departures from them |
| `why` | why it is done this way | per decision: driver, alternatives and why each is worse here, tradeoff, deeper significance, level `V` (cited) or `I` (inferred, worded as inference) |

- `understand` writes `## What`, `## How`, `## Why` inside each note.
- `transform` and `translate` keep target artifacts clean and write how and why
  to a mirrored companion note under `Docs/learn/rationale/`.
- `canon` writes how to apply each entry and why it is authoritative.
- `why` routes to high reasoning and runs the loop in shape `review`: a
  non-author reviewer checks sampled entries against the source and its
  history; an unsupported `V` drops to `I` or the entry is rejected.
- Folder notes at `how` or `why` explain the decomposition: these modules, these
  boundaries, this dependency direction.

Principles per mode, note format, and acceptance: `references/depth.md`.
Mechanical check: `scripts/check_depth.py --depth <level> [--map depth_map.tsv] <dir>`.

## Manifest And Coverage

- Lock `source_manifest.tsv` before any claim. A path outside it is out of
  scope; an output that traces to no row counts for nothing.
- `understand` maps one note per file and keeps the tree shape:
  `src/app/main.ts` → `Docs/learn/files/src/app/main.ts_learn.md`;
  `src/app/` → `Docs/learn/src/app/current_folder_learn.md`. Slug-only final
  paths are invalid; group and chunk reports stay intermediate.
- Completion needs zero `[ ]`, zero `[_]`, passing indexes, and a passing depth
  check. Detail: `references/coverage-contract.md`.

## Subsets

- Explicit: globs, branch diffs, languages.
- Fuzzy (for example "scheduler core"): write `subset_candidates.tsv`,
  `subset_decision.md`, and a locked manifest under
  `Docs/learn/subsets/<subset_id>/`. High-confidence files enter; borderline
  files go to the master; context-only files count for nothing until promoted.

## Canon Mode

Canon is how outside knowledge enters the hive: documentation MCP servers,
official specs, datasheets, source code, and curated wikis.

- Source order: domain MCP server → official docs, specs, source → community.
- Each entry records `id`, `locator`, `version`, `retrieved`, `sha256`, `mode`,
  `level` (`V` primary, `F` community, `I` inferred), `license`, and `governs`.
- MCP answers drift: snapshot each excerpt with its date and hash, and name tools
  in full as `mcp:<server>:<tool>`.
- A license that forbids excerpts leaves a pointer only, enforced by a check.
- Audit on a schedule for drift, upstream corrections, and wrong content.
- Other skills cite entries when a decision needs one; the canon never fills
  every prompt, and ablation measures its value.

Schema and audit: `references/canon.md`.

## Route

`route_policy=auto|high_reasoning|standard|cheap_translation|uncommon_translation|custom`.
Complex code, transforms, and `why` depth take high reasoning; mechanical
conversions and most `what`-depth translation take cheaper routes; escalate on
high-stakes meaning, glossary conflicts, or repeated check failure. Record
route, depth, and map in `Docs/learn/route_decision.md`. Detail:
`references/route-policy.md`.

## Surfaces

Base: `source_manifest.tsv`, `learn_checklist.md`, `todos_YYYYMMDD.md`,
`file_learn_index.tsv`, `folder_learn_index.tsv`, `route_decision.md` under
`Docs/learn/`. Transform adds `target_contract.md`, `mapping_policy.tsv`,
`validation_policy.md`, `traceability_index.tsv`. Depth `how` or `why` on
transform or translate adds `rationale/` and `rationale_index.tsv`. Canon adds
`canon/manifest.tsv` and `canon/excerpts/`.

## Validation

- The manifest covers exactly the locked scope; notes map one to one; folder
  notes cover every represented folder; subsets exclude out-of-scope files.
- Transform output carries traceability, and sources stay untouched.
- Translate output preserves headings, anchors, links, code blocks, tables,
  glossary decisions, and section parity.
- Canon entries resolve, hashes match, and licenses hold.
- `check_depth.py` passes at the decided depth and map.
- Generated shell passes `bash -n`; the cron space guard passes.

## References

- `references/core.md`, `references/loop.md`: shared laws and loop
- `references/depth.md`: what, how, why per mode; note format; acceptance
- `references/coverage-contract.md`: 1:1 tree, grouping, chunking, subsets
- `references/transform-contract.md`: per-mode content, runtime, repair
- `references/route-policy.md`: route choice and escalation
- `references/canon.md`: canon schema and audit
- `references/substrate-cron.md`: cron, runners, disk guards
- `references/lessons.md`: where each v1 rule now lives
