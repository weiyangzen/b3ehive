# Core Concepts

[中文](concepts.zh-CN.md)

## One Arrangement Per Kind Of Work

| Work | Skill | Arrangement |
|---|---|---|
| hard choice, root cause, audit, coverage | compete | parallel candidates, oracle-first selection, or a deduplicated union |
| long implementation | execution | one blueprint as a DAG, isolated workers, master acceptance |
| unknown code, migration, translation, outside knowledge | learn | a locked manifest mapped one to one, or a pinned canon; depth what, how, or why |
| faster, smaller, cheaper, or cleaner | optimization | measured loops under a frozen oracle, or design research |
| repeated attempts under a budget | looper | the shared loop and its governance |

## Three Shared Units

- **core** (`core/core.md`): seven laws and a verb lexicon, stated once, copied
  into every skill.
- **loop** (`looper-cron-builder/loop.md`): the attempt loop: shapes, stop rules,
  ratchet, ablation switch. Looper owns it; the other skills bind it by name.
- **generated artifacts**: gates, harnesses, receipts, hooks, cron or flow
  configs, ledgers. Prompts carry judgment; artifacts carry mechanics.

## Seven Laws

1. One authority: one blueprint; `[ ]` open, `[_]` submitted, `[x]` accepted.
2. Oracle first: each item names its judge before work.
3. Cite before you claim: outside facts come from a pinned canon.
4. Accept only what you re-run: receipts, recomputed metrics, fresh inputs.
5. Lease before you spend: no reward accrues toward pause.
6. Isolate honestly: one worker, one workspace, every request counted.
7. Observe instruments; change them apart.

## Verbs Carry Authority

Workers claim and submit. Oracles measure. Non-author reviewers judge. The
master accepts, rejects, and reverts. Looper leases, pauses, and retires. A lint
rejects any other pairing, so the rule "only the master accepts" lives in one
table instead of many sentences.

## Outside Knowledge

- Learn builds a canon: pinned entries with version, hash, level (`V`, `F`,
  `I`), license, and the decisions they govern. Documentation MCP servers are
  one source among specs, datasheets, source code, and curated wikis.
- Every skill cites the canon when a decision rests on an outside fact.
- Measurement tools (profilers, analyzers) are instruments, probed before use
  and kept in `instruments.tsv` with a diagnosis playbook.

## Name

`b3` = Blueprint, Batch, Behavior. `hive` = swarm intelligence. Choose the
arrangement, run bounded work, keep the proof.
