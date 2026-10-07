# v1 to v2 Migration

[中文](migration-v1-v2.zh-CN.md)

v2 changes the acceptance model of b3ehive. It does not only shorten the skill
files. It moves shared rules into common modules and makes evidence, oracle
re-runs, and master acceptance explicit.

## Why Upgrade

The v1 workflow carried many rules in long skill bodies. This made the same
rule hard to keep consistent across skills. It also made it easy to confuse a
worker report with accepted work.

v2 addresses four problems:

1. Shared laws now live in `core/core.md`.
2. The attempt loop now has one source in `looper-cron-builder/loop.md`.
3. Each item names its oracle before work starts.
4. The master accepts only after integration and a fresh oracle run.

v2 also adds pinned canon and instruments for outside knowledge and measured
optimization.

## Main Changes

| Area | v1 | v2 |
|---|---|---|
| Rule location | Long skill bodies | Shared core and loop plus skill-specific rules |
| Acceptance | Self-test and repository gates | Item oracle, receipt, master integration, and re-run |
| Worker authority | Work and acceptance could be mixed | Worker submits; master accepts |
| External knowledge | No shared canon contract | Pinned canon with version, hash, level, license, and governed decisions |
| Optimization | Research-oriented workflow | Serial measured comparison with a baseline, fresh inputs, and a hypothesis ledger; design mode remains available |
| Competition | Older layouts and selection rules | One bounded parallel comparison round with oracle-first selection, blind review, and votes without self-votes |
| Loop granularity | Often implicit in the selected work | An optional external looper layer can attach a loop to an item, metric, or surface |
| Validation | Vocabulary presence checks | Structure, lexicon, unit, and behavior checks |

The exact historical measurements are recorded in the root README. Treat them
as the v2 release snapshot, not as a promise for every future release.

## New v2 Concepts

### Core

[`core/core.md`](../core/core.md) defines the seven laws and the verb lexicon.
The same file is copied into every skill under `references/core.md`.

### Loop

[`looper-cron-builder/loop.md`](../looper-cron-builder/loop.md) defines attempt
shapes, stop rules, the ratchet, and the ablation switch. The other skills bind
this loop by name.

The smallest work unit is normally internal to the selected skill. The
`looper-cron-builder` skill is an optional external layer. Use it when a loop
must be defined at another granularity or must share an explicit resource and
side-effect envelope.

### Comparison shape

`compete` is for one bounded round of parallel candidates. It answers a frozen
question and selects or unions the results.

`optimization` normally compares one candidate after another. It measures,
keeps or reverts, and uses the result to choose the next candidate. Parallel
`lanes` are an exception for independent hypotheses that need one comparison
round.

### Oracle

An oracle is the command or review protocol that decides whether an item is
acceptable. Define it before work starts. A test command is one type of oracle;
a benchmark or a non-author review protocol is another.

### Receipt

A receipt records the submitted paths, commands, results, and other evidence.
It shows what a worker submitted. It does not grant acceptance.

### Master acceptance

The master integrates a valid submission into the canonical checkout and runs
the oracle again. Only then can an item move from `[_]` to `[x]`.

### Canon and instruments

`learn` uses a canon for pinned outside facts. `optimization` uses instruments
with probe commands and diagnosis playbooks. These records stop an unpinned
external fact or an unverified measurement from becoming a decision.

## Migration Steps

### 1. Install v2

Use the v2 checkout or package. For a portable installation:

```bash
scripts/install_skills.sh --target all --scope user --link
```

For Codex:

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new session after installation.

### 2. Check installed skills and controllers

```bash
bin/b3ehive doctor --repo .
```

The doctor reports stale installed skills and controllers generated from an
older skill contract. Regenerate a controller from the current repository
evidence before starting a new long execution.

### 3. Convert the blueprint

For each item, add or confirm:

- a stable id;
- `depends_on`;
- `owned_paths`;
- an `oracle` or `review:<protocol>`;
- `tier` when evidence levels matter;
- `budget` when item size must be bounded;
- `canon` when outside facts govern the design.

Do not infer dependencies from document order. Reject duplicate ids, missing
dependencies, cycles, and unknown marks.

### 4. Update acceptance handling

Use the v2 states:

```text
[ ] open or rejected
[_] submitted with a receipt
[x] accepted after a master re-run
```

Do not let a worker edit the acceptance mark. The master owns the transition to
`[x]`.

### 5. Choose the current artifact layout

The native v2 competition layout is the default. The old three-way layout can
still be requested for compatibility:

```text
--shape three_way_challenge --artifact-layout old_three_way
```

Use the compatibility layout only when an existing consumer needs its
`run_a`/`run_b`/`run_c` paths. It does not restore the old selection authority.

### 6. Move detailed rules to references

Keep the skill body focused on judgment: when to use the skill, how to choose a
shape, which oracle to use, and when to stop. Keep long protocols in the
skill's `references/` directory. Edit root skill sources first, then sync the
Codex plugin copy.

## What Stays Historical

The repository can keep v1 text when it explains a migration, a compatibility
surface, or the origin of a rule. Mark it as historical. Do not use it as the
current v2 entry point.

Examples include:

- `references/lessons.md` migration tables;
- sections marked `v1 text`;
- `three-way-layout.md` compatibility details;
- `old_three_way` artifact support;
- one-time import aliases in learn coverage rules.

## Migration Check

- Installed skills report the current version.
- The blueprint has an oracle for every item.
- Every worker submission has a receipt.
- The master re-runs the oracle after integration.
- The current layout is native unless compatibility requires the old layout.
- Historical v1 pages are not linked as current usage instructions.
- Root skill sources and generated plugin copies are synchronized.
