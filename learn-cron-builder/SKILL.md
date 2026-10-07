---
name: learn-cron-builder
description: Turns a frozen source scope into validated artifacts such as one-to-one code understanding, code-to-code transforms, translations, or a pinned canon of normative documents. Use to learn a codebase or spec, migrate code, or translate docs. 学习代码库、规范子集、迁移、翻译。
---

# Learn

For a user-facing choice guide, read `docs/skill-selection.md`. Lock the source
scope before producing learning, transformation, translation, or canon output.

core v2 · loop v1; an item's oracle is traceability to its source row. Read
`references/core.md` and `references/loop.md` first; this body adds only
learning rules. Working frame: understand it until you can make it.

## Modes

| Mode | Direction | Final artifact |
|---|---|---|
| `understand` | code → human language | one note per source file plus one per folder |
| `transform` | code → code, API, schema, runtime, tool asset | target files with source-target traceability |
| `translate` | human language → human language | translated docs with structural parity |
| `canon` | external documents → pinned normative subset | `canon/manifest.tsv` plus excerpts |

Every mode runs:
`scope → subset → source manifest → target contract → submissions [_] → master [x] → cleanup`.

## Manifest And Coverage

- Lock `source_manifest.tsv` before any claim. A path outside it is out of
  scope; an output that traces to no row counts for nothing.
- `understand` maps one note per file and keeps the source tree shape:
  `src/app/main.ts` → `Docs/learn/files/src/app/main.ts_learn.md`;
  `src/app/` → `Docs/learn/src/app/current_folder_learn.md`. Slug-only final
  paths are invalid. Group and chunk reports stay intermediate.
- Completion needs zero `[ ]`, zero `[_]`, and passing file and folder indexes.
- Rules for grouping, chunking, and folder synthesis:
  `references/coverage-contract.md`.

## Subsets

- Explicit subsets: globs, branch diffs, languages.
- Fuzzy subsets (for example "scheduler core") produce
  `subset_candidates.tsv`, `subset_decision.md`, and a locked manifest under
  `Docs/learn/subsets/<subset_id>/`. High-confidence files enter; borderline
  files go to the master; context-only files count for nothing until promoted.

## Canon Mode

Canon is how outside knowledge enters the hive: documentation MCP servers,
official specs, datasheets, source code, and curated wikis.

- Source order: domain MCP server → official docs, specs, source → community.
- Each entry records `id`, `locator`, `version`, `retrieved`, `sha256`, `mode`,
  `level` (`V` primary, `F` community, `I` inferred), `license`, and `governs`.
- MCP answers drift; snapshot the excerpt and record its date and hash. Name MCP
  tools by full name: `mcp:<server>:<tool>`.
- A license that forbids excerpts leaves a pointer only; a generated check
  enforces it.
- Audit on a schedule: hash or version drift, upstream corrections, wrong
  content to prune.
- Other skills cite entries when a decision needs them; nobody pastes the canon
  into every prompt. Its value is measured by ablation.
- An `understand` note may be promoted into a canon entry for another run.

Schema and audit rules: `references/canon.md`.

## Route

`route_policy=auto|high_reasoning|standard|cheap_translation|uncommon_translation|custom`.
Complex code and transforms take high reasoning; mechanical conversions and most
translation take cheaper routes; escalate on high-stakes meaning, glossary
conflicts, or repeated validator failure. Record each route in
`Docs/learn/route_decision.md`. Detail: `references/route-policy.md`.

## Surfaces

Base: `source_manifest.tsv`, `learn_checklist.md`, `todos_YYYYMMDD.md`,
`file_learn_index.tsv`, `folder_learn_index.tsv`, `route_decision.md` under
`Docs/learn/`. Transform adds `target_contract.md`, `mapping_policy.tsv`,
`validation_policy.md`, `traceability_index.tsv`. Canon adds
`canon/manifest.tsv` and `canon/excerpts/`.

## Validation

- Manifest covers exactly the locked scope; per-file notes map one to one.
- Folder notes cover every represented folder.
- Subset output excludes out-of-scope files.
- Transform output carries traceability; workers leave sources untouched.
- Translate output preserves headings, anchors, links, code blocks, tables,
  glossary decisions, and section parity.
- Canon entries resolve, hashes match, and licenses hold.
- Generated shell passes `bash -n`; the cron space guard passes.

## References

- `references/core.md`, `references/loop.md`: shared laws and loop
- `references/coverage-contract.md`: 1:1 tree, grouping, chunking, subsets
- `references/transform-contract.md`: per-mode content, runtime, repair
- `references/route-policy.md`: route choice and escalation
- `references/canon.md`: canon schema and audit
- `references/substrate-cron.md`: cron, runners, disk guards
- `references/lessons.md`: where each v1 rule now lives
