# Changelog

## 3.0.0 — 2026-11-28

- Multi-layer blueprint stacks: support three-tier `master` / `platform` /
  `leaf` stacks via `blueprint_stack.json` (`templates/blueprint-stack.json`)
  and `execution-cron-builder/scripts/validate_blueprint_stack.py`
  (`bin/b3ehive validate stack | boundaries | export-ir`).
- Occam anti-Cartesian factoring: add `Factor` practice and `promote` verb in
  `core/core.md`, synced into all five skills. Target 2,000–5,000 LOC items
  directly and promote shared capabilities to `platform` only when `>= 2` real
  leaves share them and net compression beats abstraction overhead `k`
  (`k + M + N < M * N`). Enforces zero sibling imports (`leaf ↛ leaf`), zero
  reverse imports (`platform ↛ leaf`, `harvest: true` for upward extraction
  edges), and `O(N log N)` prefix-aware `dag_ordered` / `strict_disjoint` path
  non-interference.
- Lean 4 formal verification (`formal/b3lean/`, pinned `leanprover/lean4:v4.34.0`,
  zero Mathlib): pure `Init`-only specification (`Core.lean`) and kernel-proved
  soundness (`Soundness.lean`) covering global acyclicity (`topo_acyclic_sound`),
  antichain path non-interference (`dag_ordered_noninterference`), boundary and
  transitive acceptance safety (`checkBoundaries_sound`,
  `checkTransitiveAccepted_sound`, `master_only_acceptance`), Occam Rule-of-Two
  and compression bounds (`occam_no_gain_for_single_leaf`,
  `occam_factoring_strict_saving`), and Major Revision `keep` non-regression
  (`major_revision_non_regression`).
- Anti-gaming Lean runner (`execution-cron-builder/scripts/verify_lean.py`,
  `bin/b3ehive verify-lean stack | oracle | self-check`): compiled native
  `b3lean check`, kernel certificate emission (`--cert`, `StackCert.lean` via
  `rfl`), external `leanchecker`, read-only `Specs/` tamper guard, and strict
  standard-axiom allowlist (`{propext, Classical.choice, Quot.sound}` — rejects
  `sorryAx`, custom axioms, and `native_decide`).
- All five skills, Codex plugin, grokbot skill set, templates, docs, evals, and
  package move to 3.0.0.

## 2.3.1 — 2026-11-07

- grokbot: new grokbot-only skill set. Each of the five skills gets a
  `grokbot-<skill>` build, packed as `grokbot/grokbot-<skill>-skill.zip` for
  `unzip ... -d ~/.claude/skills/`.
- grokbot: every build opens with a gate. Only grokbot loads it; other hosts,
  `claude` subagents included, stop and use the base skill.
- grokbot: every subagent call uses only `claude --dangerously-skip-permissions`
  as its agent runtime. The runner template fixes `-p` and the flag, any other
  runner fails closed, and a missing `claude` stops with
  `user_action_required`. `references/substrate-cron.md` names only that
  runtime; Codex, Cursor, and other host adapters are dropped.
- `scripts/build_grokbot.py` builds the set reproducibly from the base skills,
  `core/grokbot-gate.md`, and `core/grokbot-runtime.md`; `--check` runs in
  `scripts/check_all.sh`.
- install: `scripts/install_skills.sh --target grokbot`; `bin/b3ehive sync`
  rebuilds the set and `bin/b3ehive doctor` checks installed `grokbot-*`
  copies.
- lint: grokbot gate, runtime, and dropped-adapter checks; 7 new unit tests.
- All five skills, the Codex plugin, and the package move to 2.3.1.

## 2.2.0 — 2026-10-16

- loop v2: closed result vocabulary (`validated_progress`, `repair_required`,
  `replan_required`, `user_action_required`, `wait`, `failed`); `repair_noop`
  counts as a stall; the ratchet compares against the best accepted state; two
  stalls open a replan obligation that only new evidence clears; direction
  (`grow`, `switch`, `verify`) with mechanism distance; one remediation per
  lineage; `observed_only` evidence; typed item closure.
- optimization: statistics rule (`B3_STATS`: paired alternating fresh-process
  trials, interval must exclude zero and clear the minimum effect) and
  experiment identity over the full toolchain closure.
- learn: experience ledger (`canon/lessons.tsv`, lesson and incident rows) with
  `scripts/find_lesson.py` for bounded search, activation by use-site recall,
  and separate `applied` and `helpful` records.
- compete: guard-set regressions (`REGRESSED:`), `OBSERVED_ONLY`, integrity
  suspicion (`SUSPECT:`) confirmed only by two channels, shadow mode for prompt
  and policy changes.
- execution: effect intent and readback with blocking on unknown, retry table by
  failure kind, revision fence at every admission, receipt fingerprint over
  untracked content.
- looper: `replan` before pause, novelty as secondary reward, no-spend closeouts.
- examples: RSI example prompt (`examples/rsi-prompt.md`).
- evals: four new scenarios; 10 new unit tests.

## 2.1.0 — 2026-10-08

- learn: `learn_depth=what|how|why` with per-glob `depth_map`. `how` lists the
  quality principles followed, each with evidence; `why` records driver,
  alternatives and why each is worse, tradeoff, significance, and a `V` or `I`
  level. Applies to understand, transform, translate, and canon.
- learn: `references/depth.md` and `scripts/check_depth.py`; `why` runs in loop
  shape `review`.
- evals: scenario `learn-4`.

## 2.0.0 — 2026-10-04

- One law (`core/core.md`), one loop (`looper-cron-builder/loop.md`), five skills.
- Oracle-first acceptance with receipts and fresh re-runs; blueprint grammar adds
  `oracle`, `tier`, `budget`, `canon`, and cross-blueprint dependencies.
- learn canon mode; optimization measured mode; looper as thin governance.
- compete selection fixed: oracle, blind review, votes without self-votes.
- Structure and lexicon lint, unit tests, behavior evals; install `--link`,
  version stamps, `b3ehive doctor`.
