# Learn Coverage Contract

## Source Manifest

`Docs/learn/source_manifest.tsv` is the source of truth.

Minimum columns:

```text
source_id
source_path
source_kind
source_bytes
source_hash
subset_id
group_id
chunk_set_id
target_artifact
folder_artifact
mapping_mode
status
```

Rules:

- Every in-scope source file appears exactly once.
- Any source path not in the manifest is out of scope.
- Any output not traceable to a manifest row cannot count toward completion.
- Regeneration preserves stable `source_id`, `[_]`, and `[x]` marks.

## One-to-One File Tree Gate

For `learn_mode=understand`, completion requires:

```text
source_file_count == file_learn_index_rows
source_file_count == final_per_file_artifact_count
every source row has exactly one final target_artifact
every target_artifact exists and is non-empty
every target_artifact names source_path and source_hash
no duplicate final target_artifact paths
no extra final artifacts outside the manifest
```

Opaque slug-only final paths are invalid:

```text
Docs/learn/files/<hash>_learn.md
Docs/learn/slugs/<slug>.md
Docs/learn/grouped/<group>.md as final per-file output
```

## Folder Coverage

Folder artifacts:

```text
Docs/learn/<folder_path>/current_folder_learn.md
Docs/learn/current_folder_learn.md
```

Completion requires:

```text
represented_folder_count == folder_learn_index_rows
represented_folder_count == current_folder_learn.md artifact count
every folder row is OK
folder artifacts derive from accepted [x] file-level artifacts
```

## Subsets

Subset files:

```text
Docs/learn/subsets/<subset_id>/subset_manifest.tsv
Docs/learn/subsets/<subset_id>/subset_candidates.tsv
Docs/learn/subsets/<subset_id>/subset_decision.md
Docs/learn/subsets/<subset_id>/source_manifest.tsv
```

Explicit subset validation:

- every included file matches at least one include rule
- no included file matches an exclude rule
- excluded files never appear in checklist, todo, index, or final outputs

Fuzzy subset validation:

- every candidate has `source_path`, `matched_signal`, `confidence`,
  `include_decision`, `reason`, and `context_only`
- high confidence files may be auto-included
- borderline files must be surfaced for master review
- context-only files cannot count toward completion unless promoted

## Grouping and Chunking

Grouping is an input efficiency technique only.

```text
small file groups default <=256KiB source input
oversized chunks default <=256KiB source input
group output must contain one section per source file in manifest order
chunk outputs merge into exactly one final per-file artifact
group/chunk artifacts never satisfy final file coverage by themselves
```

Preferred ledgers:

```text
Docs/learn/learn_groups.tsv
Docs/learn/chunk_manifest.tsv
```

Accept old `research_groups.tsv` only as a one-time import alias while cleaning
up older runs. Do not expose it as a public learn surface.
