---
name: grokbot-compete-cron-builder
description: Grokbot only. Subagents run only as claude --dangerously-skip-permissions. Runs bounded proposal competitions with n workers and m candidates, selecting by oracle score or independent review, or keeping the union of all valid findings. Use for one-round parallel comparison, root-cause or repair search, audits, coverage sweeps, and blueprint synthesis. 方案竞争、并行比较、择优、覆盖审计。
---

# Compete (grokbot)

## Grokbot Gate

Grokbot build of `compete-cron-builder`, b3ehive 2.3.1.
This section overrides every runner, platform, transport, and subagent rule in
this skill and in its references.

Load:

- Only grokbot loads this skill. Grokbot installs it with the command below
  and names the subagent runtime explicitly:
  `unzip grokbot-compete-cron-builder-skill.zip -d ~/.claude/skills/`
- Any other host stops here and loads nothing from this directory: Claude Code,
  a `claude` subagent that grokbot started, Codex, Cursor, Grok Build without
  grokbot, opencode, OpenClaw, and Hermes. Those hosts use the base skill
  `compete-cron-builder` instead.

Subagent runtime:

- Every subagent call uses only `claude --dangerously-skip-permissions` as its
  agent runtime. This covers workers, reviewers, verifiers, voters, repair
  generations, nested runs, and in-session subagents.
- Runner template, also the value of `B3EHIVE_AGENT_RUNNER`, with
  `B3EHIVE_AGENT_PLATFORM=claude`:

  ```bash
  claude -p --dangerously-skip-permissions \
    --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
    --add-dir "{workspace}" < "{prompt_file}" > "{output_file}"
  ```

- No other runtime: no Grok subagent or task tool, no `grok`, `codex`, Cursor,
  opencode, OpenClaw, or Hermes worker, no Codex TUI transport, and no
  `--permission-mode` flag. Where the body or a reference names another runner,
  read this runtime.
- A runner that does not start with `claude -p --dangerously-skip-permissions`
  fails closed with its value. A missing `claude` binary stops the run with
  `user_action_required`; there is no fallback.
- The flag removes every permission check, so the task root is the only fence.
  `--add-dir` names the claim workspace only, never the canonical checkout or
  `$HOME`. Each subagent still counts against every cap and lease.
- Each subagent prompt states its role and tells it not to load any
  `grokbot-*` skill.
- Validate-only output prints `platform=claude`,
  `runtime=claude --dangerously-skip-permissions`, and the resolved runner.

For a user-facing choice guide, read `docs/skill-selection.md`. This skill
selects proposals or findings; it does not replace the master acceptance step.

core v2 · loop v2, shape `lanes`. Read `references/core.md` and
`references/loop.md` first; this body adds only competition rules.

Compete is a single-round parallel comparison. It runs a bounded set of
candidates against one frozen question and selects or unions the results. It
does not own the serial ratchet used by optimization.

## Decide

Before launch, decide and log:

- question: `precision`, `coverage`, `audit`, `repair`, `blueprint`, or
  `execution_choice`
- m (candidates) and k (selected count, or `all-valid`)
- oracle: the command that measures a candidate, or the review protocol
- routes: spread candidates across model families when more than one exists

Coverage and audit keep every valid finding. Other questions rank by oracle.
Starting points: precision m ≤ 4, k 1; repair m ≤ 4, k 1 plus a fallback;
blueprint m ≤ 5, k 2–3 then synthesis; execution_choice m ≤ 3, k 1.

## Run

1. Freeze task, oracle, and lease; candidates change none of them.
2. Each candidate submits a result and a receipt inside its own directory.
3. A candidate that fails any stage leaves; the rest continue. With none left,
   the run reports failure.
4. Missions differ in approach, not wording; reject cosmetic variants at
   planning time.
5. Coverage and audit findings take the form
   `FINDING: <location> | <claim> | <reproduction> | <severity>`; a finding
   without a reproduction is dropped.

## Select

In this order:

1. Oracle: every run passes; the worst run's score ranks. Where results can be
   gamed, add fresh runs (`--oracle-runs`).
2. Blind review: a non-author, read-only reviewer, preferably of another model
   family, judges candidates labeled A/B/C without scores.
3. Votes from round two; votes for oneself are void.
4. Stable candidate id.

Coverage: dedupe by location and claim, keep the union, rank audits by severity.

Oracle lines the script reads: `SCORE: <x>`; `REGRESSED: <target>` (a guard
target that passed at baseline now fails, so the candidate fails);
`OBSERVED_ONLY` (evidence below declared fidelity: kept, never ranked);
`SUSPECT: <reason>` (integrity suspicion, recorded only).

## Integrity

- A suspicion never disqualifies alone. Confirm cheating only when two channels
  agree (for example a trajectory scan and a runner attestation) and a non-author
  reviewer finds the restricted material was both seen and used.
- Solvers never see analyst outputs, holdout data, or scores of peers.

## Shadow Mode

To change a prompt, policy, or validator, run the incumbent and the proposal as
two candidates on a frozen gold set. Recommend promotion only when the proposal
meets the declared quality thresholds and its token and latency ratios stay
within the declared caps. The master applies the change; compete never does.

## Script

`scripts/compete_cron_builder.py` runs stages in parallel, writes receipts,
measures, tallies, and merges. It never infers the question type or ranks by
id order alone.

```bash
python3 scripts/compete_cron_builder.py \
  --task "Find validation risks in this API" --output ./competition-runs/api \
  --question-type audit --why "release gate" --proposal-count 4 \
  --command '<runner template using {prompt_file} {output_file}>' \
  --review-command '<reviewer template using {prompt_file}>'
```

Precision run with an oracle:

```bash
python3 scripts/compete_cron_builder.py \
  --task "Pick the root cause" --output ./competition-runs/rc \
  --question-type precision --oracle-command 'make check CANDIDATE={candidate_dir}' \
  --oracle-runs 3 --command "$B3EHIVE_AGENT_RUNNER"
```

Template fields: `{candidate_id}`, `{stage}`, `{prompt_file}`,
`{output_file}`, `{candidate_dir}`, `{result_file}`, `{competition_id}`,
`{question_type}`, `{run_index}`. Oracle runs see `B3_ORACLE_RUN` and
`B3_ORACLE_SEED`. `--runner mock` is a dry run. `--shape three_way_challenge`
with `--artifact-layout old_three_way` keeps the run_a/run_b/run_c layout:
`references/three-way-layout.md`.

## Hand Off

- Output is `[_]`: selected ids, rejected ids, repair assignments, validation
  hints, `decisions.log`, and `selection_evidence.json` or `findings.json`.
- Execution turns accepted findings into `[ ]` child items; the master accepts.
- Inside a looper attempt, pass `--handoff-mode looper_attempt` with
  `--parent-lease-ref`; cost rolls into that lease.

## References

- `references/core.md`, `references/loop.md`: shared laws and loop
- `references/three-way-layout.md`: three-way shape and artifact layout
- `references/substrate-cron.md`: cron, runners, disk guards
- `references/lessons.md`: where each v1 rule now lives
