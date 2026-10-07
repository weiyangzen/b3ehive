# b3ehive

[中文](README.zh-CN.md)

**Five swarm skills. One law. One loop.**

[![Codex](https://img.shields.io/badge/Codex-Skill-blue)](https://github.com/openai/codex)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-orange)](https://docs.anthropic.com/en/docs/claude-code)
[![Cursor](https://img.shields.io/badge/Cursor-Skill-black)](https://cursor.com)
[![Grok Build](https://img.shields.io/badge/Grok%20Build-Skill-red)](https://x.ai/cli)
[![opencode](https://img.shields.io/badge/opencode-Skill-green)](https://opencode.ai)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![Hermes](https://img.shields.io/badge/Hermes-Skill-purple)](https://hermes-agent.nousresearch.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

b3ehive arranges coding agents into a hive. Each skill is a different arrangement
for a different kind of work. All five obey one short law, share one attempt
loop, and accept nothing they have not re-run.

## The Five

| Skill | When | Arrangement |
|---|---|---|
| [`compete`](compete-cron-builder/SKILL.md) | one-round proposal comparison, a root cause, an audit | one bounded parallel comparison; oracle first, then blind review, then votes without self-votes; or a deduplicated union of findings |
| [`execution`](execution-cron-builder/SKILL.md) | a long implementation | one blueprint as a DAG; isolated workers; the master accepts |
| [`learn`](learn-cron-builder/SKILL.md) | unknown code, migration, translation, outside knowledge | a locked manifest mapped one to one, or a pinned canon |
| [`optimization`](optimization-cron-builder/SKILL.md) | faster, smaller, cheaper, cleaner | serial measured comparison under a frozen oracle, or design research |
| [`looper`](looper-cron-builder/SKILL.md) | external loop granularity or shared governance | an optional layer attached to an item, metric, or surface |

## How It Holds Together

```text
core/core.md ─────────── seven laws + verb lexicon ──┐
                                                     ├── copied into every skill
looper-cron-builder/loop.md ── the attempt loop ─────┘

SKILL.md  ── judgment: when, how to split, which oracle, which shape, when to stop
artifacts ── mechanics: gates, harnesses, receipts, hooks, cron and flow configs
```

Prompts carry judgment. Generated artifacts carry mechanics. A rule that must
never break becomes a generated check, not a repeated sentence.

## Seven Laws

1. **One authority.** One blueprint. `[ ]` open, `[_]` submitted, `[x]` accepted.
2. **Oracle first.** Each item names its judge before work begins.
3. **Cite before you claim.** Outside facts come from a pinned canon.
4. **Accept only what you re-run.** Receipts, recomputed metrics, fresh inputs.
5. **Lease before you spend.** No reward accrues toward pause.
6. **Isolate honestly.** One worker, one workspace, every request counted.
7. **Observe instruments; change them apart.**

Verbs carry authority. Workers *claim* and *submit*; oracles *measure*;
non-author reviewers *judge*; the master *accepts*, *rejects*, and *reverts*;
looper *leases*, *pauses*, and *retires*. A lint rejects any other pairing.

## The Loop

```text
attempt ─ receipt ─ ADVANCED | STALLED | REGRESSED
   ▲                         │
   │   two stalls: replan    │   three: pause
   └─ ratchet: keep only what the oracle measures better; else revert
```

Shapes: `single`, `relay` (model families alternate, fresh sessions, the
repository is the memory), `review` (a fresh, read-only, non-author reviewer each
round), `lanes` (parallel attempts, compete selects). `B3_LOOP=full|single|null`
swaps the loop for ablation. The looper skill is an optional external layer
that sets loop granularity and governance.

## Outside Knowledge

- **Canon.** Learn builds pinned entries from documentation MCP servers, specs,
  datasheets, source, and curated wikis. Each entry records version, hash, level
  (`V` primary, `F` community, `I` inferred), license, and the decisions it
  governs. Skills cite entries when a decision needs them.
- **Instruments.** Profilers and analyzers are probed before use and listed in
  `instruments.tsv` with a diagnosis playbook.

b3ehive bundles no domain knowledge. Domain packs, such as a CUDA docs MCP
server, a kernel wiki, or an Nsight Compute skill, enter through canon and
instruments.

## Install

```bash
git clone -b v2 https://github.com/weiyangzen/b3ehive.git && cd b3ehive
scripts/install_skills.sh --target all --scope user --link
```

`--link` symlinks each skill to the checkout, so `git pull` updates every
platform. Without it, copies carry a version stamp that `bin/b3ehive doctor`
checks.

| Target | User skill path |
|---|---|
| Codex | `~/.codex/skills/<skill>/` |
| Claude Code | `~/.claude/skills/<skill>/` |
| Cursor | `~/.cursor/skills/<skill>/` |
| Grok Build | `~/.grok/skills/<skill>/` |
| opencode | `~/.config/opencode/skills/<skill>/` |
| OpenClaw | `~/.openclaw/skills/<skill>/` |
| Hermes | `~/.hermes/skills/<skill>/` |

Codex plugin: `codex plugin marketplace add weiyangzen/b3ehive` then
`codex plugin add b3ehive@b3ehive`. Platform details:
[docs/agent-platforms.md](docs/agent-platforms.md).

## Start Here

- New installation: [Getting Started](docs/getting-started.md)
- Choose a task arrangement: [Skill Selection and Use](docs/skill-selection.md)
- Understand the upgrade: [v1 to v2 Migration](docs/migration-v1-v2.md)
- Write and review docs: [Writing Style](docs/writing-style.md)

## Use

```text
Use execution-cron-builder for this repository and this blueprint.
Use compete-cron-builder to pick the root cause; the oracle is `make test`.
Use learn-cron-builder to build a canon from these specs for BLUEPRINT.md.
Use optimization-cron-builder in measured mode on this kernel. Compare
candidates serially and re-run the oracle after each candidate.
Use looper-cron-builder only when an external loop must set granularity or share
a weekly budget.
```

A competition from the shell:

```bash
bin/b3ehive compete --question-type precision \
  --oracle-command 'make check CANDIDATE={candidate_dir}' --oracle-runs 3 \
  "Pick the root cause of the failing scheduler test"
```

The runner comes from `B3EHIVE_AGENT_RUNNER`; `--mock` runs a dry competition.

There is no `b3ehive execution` or `b3ehive learn` command. Those names refer
to skills that an agent loads and follows. The CLI provides maintenance
commands and a direct competition runner.

## Check

```bash
scripts/check_all.sh        # sync, lint, unit tests, layout and platform checks
bin/b3ehive doctor --repo .  # stale installs and controllers
```

`evals/scenarios.json` holds fifteen behavior scenarios, three per skill, and the
ablation matrix that decides which mechanisms stay.

## v2 At A Glance

| | v1 | v2 |
|---|---|---|
| SKILL.md bodies | 11,461 words | 3,432 words |
| execution load per invocation | ~11.1k tokens | ~3.0k tokens |
| shared contract | ~3.8k tokens, inside looper | ~1.1k tokens, core + loop, copied into each skill |
| acceptance | self-test plus repository gates | oracle per item, receipts, master re-run, fresh inputs |
| outside knowledge | — | canon and instruments |
| optimization | research documents | measured mode plus design mode |
| compete selection | first ids; self-votes counted; keyword-guessed question type | oracle, blind review, votes without self-votes; caller decides |
| checks | vocabulary presence | structure and lexicon lint, unit tests, behavior evals |

Rules moved out of skill bodies live in each skill's `references/lessons.md`.

## Repository

- `core/`: shared law and substrate guide (sources of the copies)
- `*-cron-builder/`: the five skills
- `evals/`: behavior scenarios and ablation matrix
- `templates/`: blueprint, oracle, canon, instruments
- `tests/`: unit tests for the compete script and the lint
- `scripts/`: install, sync, lint, checks
- `plugins/b3ehive/`: Codex plugin package
- `docs/`: [concepts](docs/concepts.md), [blueprint](docs/blueprint.md),
  [platforms](docs/agent-platforms.md), [Codex plugin](docs/codex-plugin.md),
  [getting started](docs/getting-started.md), [skill selection](docs/skill-selection.md),
  [migration](docs/migration-v1-v2.md), and [writing style](docs/writing-style.md)

## Name And License

`b3` = Blueprint, Batch, Behavior. `hive` = swarm intelligence.

MIT © Weiyang ([@weiyangzen](https://github.com/weiyangzen))
