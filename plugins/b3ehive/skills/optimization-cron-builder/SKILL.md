---
name: optimization-cron-builder
description: Build or repair a design-idea-guided optimization cron for a repository. Use when the user provides a design philosophy and wants a Stage_*_AR_Blueprint.md with at most 100 checklist items, per-item SOTA optimization research docs under Docs/researches/Stage_*_AR/, parallel tmux workers, Codex, Claude Code, opencode, OpenClaw, or Hermes agent-runner batches, and cleanup-on-complete.
---

# Optimization Cron Builder

## Overview

Build a repository-local optimization research pipeline. Continuously apply a
user-supplied design philosophy to one stage blueprint, derive a bounded AR
checklist, write one research doc per item, track progress, run parallel `tmux`
workers through the selected agent runner, and remove the cron setup when the
AR blueprint is complete. Product-code implementation stays outside this
pipeline.

`AR` means `Architecture Refinement`. The pipeline supports any stage-specific
optimization blueprint.

## Output Discipline And Anti-Slop Contract

- Start with the requested AR artifact, design decision, evidence, action,
  validation result, or executable instruction.
- Give each sentence one concrete payload: design constraint, repository fact,
  optimization item, decision, action, result, evidence, or consequence.
- State verification through its result, evidence, and consequence.
  Omit process narration, opening meta-commentary, routine check narration,
  motivational filler, restatements, and closing recaps.
- Use direct, positive statements when they preserve the truth conditions. Keep
  technical negation that defines scope exclusions, permissions, disk and log
  gates, failure behavior, cleanup safety, or acceptance rules.
- Omit relationship or causal claims unsupported by repository, research, or
  validator evidence. Handle material uncertainty under the next rule; leave no
  speculative transition or placeholder.
- When unresolved uncertainty changes correctness, safety, legality, an AR
  decision, or the available action, state the exact unknown, condition, and
  consequence.
- Keep the response body within 10% above or below an explicit target length.
  Without a target, use the shortest complete form that preserves required AR
  artifacts, evidence, decisions, actions, and consequences.
- Include a boundary statement only when it changes correctness, safety,
  legality, or the available action. Name the exact constraint and permitted
  path.
- Before delivery, silently inspect every character for filler, duplicated
  safeguards, unsupported claims, vague predicates, stale placeholders,
  fabricated evidence, section completeness, and length.
- Treat state marks, paths, environment variables, commands, thresholds,
  platform names, stage names, and validator-dependent strings as contract
  data; preserve their exact spelling.

## Shared b3ehive Contract

Follow `../looper-cron-builder/references/b3ehive-bridge-contract.md` for route
selection, estimator decisions, nested calls, evidence handoff, `looper_log`
capture, ROI, and self-evolution.

Local obligations:

- Optimization docs and AR items remain `[_]` evidence until the owning master
  lane accepts them.
- Nontrivial automatic item-count, worker-grouping, route, research-depth, and
  simplification choices should leave `EstimatorPolicy` and `RouteDecision`
  evidence.
- Recurring skill text bloat,
  scaffold overdesign, validator/hook drift, prompt-block sprawl, route waste,
  or tool-integration friction produces a `looper_log`.
- Each `looper_log` must identify the refined `TargetObject` and the
  signal-producing `InstrumentObject`: AR grain, design rule, route, validator,
  scaffold, prompt/hook artifact, tool, or skill composition.
- Optimization may propose simplification or instrument improvements. Every
  looper-log-derived change to skill text, policy, scaffold, or tooling requires
  EvidenceLint, ROI, ParetoGate, rollback, and master `[x]`.

## Workflow

1. Inspect the target repository and identify the stage's single authoritative
   blueprint source.
2. Capture the user-supplied design philosophy in one short stable sentence.
3. Generate one authoritative `Docs/Stage_*_AR_Blueprint.md` with:
   - a bounded checklist count;
   - exactly one item per optimization topic;
   - no more than 100 items;
   - worker-ownable grouped sections.
4. Gate every `[ ]` item on a corresponding doc under
   `Docs/researches/Stage_*_AR/`. The doc must cover only that item, follow the
   design philosophy, use stable SOTA or mature frontier practice, and give
   concrete recommendations for the repository.
5. Add repo-local `.ops/` and `.cron/` helpers; hide them from git where
   appropriate.
6. Create AR blueprint tools, a daily todo generator, an optimization guard, a
   cron space/log guard, a worker runner, an install script, and a cleanup
   script.
7. Run the guard once in `VALIDATE_ONLY=1`.
8. Install cron only after validate-only succeeds and the disk/log budget guard
   passes.
9. Start parallel `tmux` workers with disjoint section ownership.
10. After each worker batch, reconcile section snapshots into the authoritative
    AR blueprint and refresh today's todo.
11. At full AR completion, remove cron entries and stop `tmux` sessions. Remove
    repo-local cron helpers when cleanup is requested.

## Required Components

### AR Blueprint

- Use exactly one authoritative AR blueprint file.
- Keep total checklist items `<= 100`.
- Set the research grain so one item maps to one optimization doc.
- Put stable repository-relative output paths in checklist items when useful.
- Group checklist items into worker-ownable sections.

### Per-Item Research Output

- Output root: `Docs/researches/Stage_*_AR/`
- One doc per checklist item.
- Keep every doc inside its topic boundary.
- Filter every recommendation through the user design philosophy.
- Prioritize stable SOTA or mature frontier practice over unvalidated novelty.
- Favor decisions that reduce complexity, cognitive load, and future rework.

### Optimization Guard

- Maintain `.cron/*state`, logs, progress, heartbeat, last-message files.
- Enforce disk/log safety on every tick before worker spawn:
  - default `MIN_FREE_GB=30`; when the Data/root volume has less free space,
    run cleanup and refuse to start new workers;
  - default `DANGER_FREE_GB=15`; below this threshold, write state
    `blocked_disk_space`, run lightweight cleanup, and exit immediately;
  - default `MAX_LOG_MB=20` for worker logs and `MAX_KEEPALIVE_MB=5` for
    keepalive/scheduler logs; retain only the tail after a file exceeds its cap;
  - default `LOG_RETENTION_DAYS=3`; delete old `.log`, `.out`, and `.err` files
    under the cron root;
  - default `WORKSPACE_TTL_HOURS=48`; remove only stale, non-live
    `.cron/automation_repo*` or `.cron/**/workspaces/slot*` directories;
  - default `MAX_CRON_ROOT_GB=30`; refuse new worker spawn when the cron root
    remains above this threshold after cleanup;
  - preserve every workspace whose path is referenced by a live selected
    agent-runner process, `tmux`, shell, or lock/pid file;
  - record cleanup decisions in a bounded janitor log, never an unbounded cron log.
- Support parallel `tmux` workers.
- Give each worker a disjoint, section-owned write scope.
- Reconcile worker section snapshots back into the main AR blueprint.
- Refresh today's todo after each successful merge.
- Classify empty or off-topic docs as failure.
- Clean up cron when all AR items are checked.

### Cron Space Guard

Every generated optimization cron must include a repo-local janitor script, such as
`.cron/scripts/cron_space_guard.sh`. The optimization guard calls it from the
top of the guard, before any `tmux` or agent-runner launch.

Minimum behavior:
- Derive the cron root from the script path, independent of the caller's current
  directory.
- Cap active logs by preserving the last `MAX_LOG_MB` with `tail -c`, a temp
  file, and atomic `mv`.
- Rotate or truncate scheduler redirection targets such as `keepalive.log`
  before appending output.
- Clean old logs and stale workspaces before checking the cron-root budget.
- Verify live worker paths with self-match-safe process checks before deleting
  any automation repo or workspace.
- Return a distinct nonzero code for "budget exceeded"; exit without marking
  optimization progress.
- Keep every default overrideable through environment variables.

### Cleanup

- Remove only this repo's optimization cron line.
- Stop guard and worker `tmux` sessions.
- With cleanup-on-complete enabled, remove repo-local `.cron/` and `.ops/`
  artifacts created only for the optimization run.
- Keep the authoritative blueprint and completed research docs.

## Agent Platform Compatibility

Generated optimization cron code must support Codex, Claude Code, opencode,
OpenClaw, and Hermes via a single agent-runner abstraction.

Default platform selection:
- `B3EHIVE_AGENT_PLATFORM=codex` uses one independent interactive Codex TUI
  process in a task-local tmux server with a private writable `CODEX_HOME` and
  exactly one submitted and authenticated `/goal` for each admitted bounded
  optimization execution. It requires controller-owned turn/request admission,
  at most one outstanding request per execution, terminalizes the goal after
  its result/handoff, and stops the tmux server immediately; an idle active goal
  or automatic post-result continuation is forbidden. `codex app-server`,
  shared Codex daemons, `codex exec`, and Codex without tmux are forbidden.
  Nested agents are forbidden unless the target repository explicitly enables
  and budgets them; every enabled child is an independent execution and consumes
  the same global transport, turn, request-rate, in-flight, and outstanding-
  request limits rather than hiding behind its parent worker.
- `B3EHIVE_AGENT_PLATFORM=claude` uses `claude -p`.
- `B3EHIVE_AGENT_PLATFORM=opencode` uses `opencode run`.
- `B3EHIVE_AGENT_PLATFORM=openclaw` uses `openclaw agent`.
- `B3EHIVE_AGENT_PLATFORM=hermes` uses `hermes chat`.
- `B3EHIVE_AGENT_PLATFORM=auto` may choose the first installed CLI from Codex,
  then Claude Code, then opencode, then OpenClaw, then Hermes.

Default command templates:

```bash
# Codex interactive TUI
codex_argv=(codex -C "$WORKER_REPO" -c features.goals=true --no-alt-screen)
[[ -n "${CODEX_MODEL:-}" ]] && codex_argv+=(-m "$CODEX_MODEL")
[[ -n "${CODEX_REASONING_EFFORT:-}" ]] && \
  codex_argv+=(-c "model_reasoning_effort=$CODEX_REASONING_EFFORT")
[[ -n "${CODEX_SERVICE_TIER:-}" ]] && \
  codex_argv+=(-c "service_tier=$CODEX_SERVICE_TIER")
tmux -S "$TASK_ROOT/tmux.sock" -f /dev/null new-session -d \
  -s "$SESSION" -c "$WORKER_REPO" \
  env CODEX_HOME="$TASK_ROOT/codex-home" "${codex_argv[@]}"
# Wait for the composer, paste one short /goal with a claim-specific final
# token, poll joined composer text until that token is visible, submit once,
# then authenticate route/cwd/thread/goal before counting this lane as live.
tmux -S "$TASK_ROOT/tmux.sock" set-buffer -b goal \
  "/goal $GOAL Integrity token: $GOAL_COMPLETION_TOKEN"
tmux -S "$TASK_ROOT/tmux.sock" paste-buffer -b goal -t "$SESSION" -d
# Generated controller polls `capture-pane -p -J`; timeout fails without Enter.
tmux -S "$TASK_ROOT/tmux.sock" send-keys -t "$SESSION" C-m

# Claude Code
claude -p --model "${CLAUDE_MODEL:-sonnet}" --effort "${CLAUDE_EFFORT:-max}" \
  --permission-mode "${CLAUDE_PERMISSION_MODE:-auto}" \
  --add-dir "$WORKER_REPO" < "$PROMPT_FILE" > "$OUTPUT_FILE"

# opencode
opencode run --dir "$WORKER_REPO" ${OPENCODE_MODEL:+--model "$OPENCODE_MODEL"} \
  ${OPENCODE_VARIANT:+--variant "$OPENCODE_VARIANT"} \
  ${OPENCODE_AGENT:+--agent "$OPENCODE_AGENT"} \
  < "$PROMPT_FILE" > "$OUTPUT_FILE"

# OpenClaw
openclaw ${OPENCLAW_PROFILE:+--profile "$OPENCLAW_PROFILE"} agent --local \
  ${OPENCLAW_AGENT:+--agent "$OPENCLAW_AGENT"} \
  ${OPENCLAW_THINKING:+--thinking "$OPENCLAW_THINKING"} \
  --message "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"

# Hermes
hermes chat ${HERMES_MODEL:+--model "$HERMES_MODEL"} \
  --toolsets "${HERMES_TOOLSETS:-skills,terminal}" \
  ${HERMES_SKILLS:+-s "$HERMES_SKILLS"} \
  -q "$(cat "$PROMPT_FILE")" > "$OUTPUT_FILE"
```

Validate-only output must print the selected platform and resolved runner. If
`B3EHIVE_AGENT_RUNNER` is set, use it instead of the default template.

## Batch Rules

- Prefer exactly 5 workers when the blueprint partitions cleanly into 5 sections.
- Each worker owns one section only.
- Workers may update only:
  - their owned section in the clone-local AR blueprint
  - their owned output directory under `Docs/researches/Stage_*_AR/`
- Only the guard merge step updates the main repo's authoritative blueprint.
- State the design philosophy, completion rules, and owned output scope in every
  worker prompt.

## Validation

Readiness requires:

- `bash -n` on all created shell scripts
- one authoritative AR blueprint generation pass
- one daily todo generation pass
- one `VALIDATE_ONLY=1` guard run
- `crontab -l` verification after install
- `tmux ls` verification after worker launch
- non-empty output verification for completed items

## Repair Rules

For an incorrect AR blueprint:

1. Stop workers.
2. Regenerate the blueprint from the same design philosophy and source scope.
3. Preserve existing `[x]` marks only when the corresponding research docs
   still exist and remain non-empty.
4. Regenerate today's todo before resuming.

For a broad, non-item-pure worker doc:

1. Keep the item incomplete.
2. Split the checklist item or narrow the doc title and scope.
3. Rerun only the affected section.

## Looper Embed Rules

When embedded in `looper-cron-builder`, optimization runs operate only inside
an active `ResourceLease` with a `ParentLeaseRef`. Use nested optimization for
periodic architecture refinement, design-philosophy research refresh, or
strategy/blueprint bridge refinement.

Nested optimization runs cannot write `[x]` or escape the parent lease budget;
they produce reward candidates only. They should attach to a looper
`BridgeSurface` with `bridge_level=strategy` or `bridge_level=blueprint`. Output
must change a real decision surface before it can count as reward.

Reusable instrument improvements for skills, scaffolds, validators, prompt/hook
engineering, route policy, or coding-tool adapters should produce `looper_log`
refs. Logs should separate target feedback from instrument feedback so review
can distinguish design-target difficulty from optimization-machinery complexity.

## Local References

Read only the references required by the current task:

- `references/optimization-pattern.md`
- `references/repair-playbook.md`
