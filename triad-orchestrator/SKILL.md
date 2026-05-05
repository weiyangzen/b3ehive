---
name: triad-orchestrator
description: Run a three-agent tournament workflow for coding, research, planning, or evaluation tasks. Use when the user asks to launch three agents in parallel, compare multiple agent outputs, write results under run_a/run_b/run_c/implementation, perform verifier checks, cross-critique, update, select a best solution, or synthesize repair assignments.
---

# Triad Orchestrator

Use this skill to turn one task into a structured three-agent workflow:

1. Create `run_a/implementation`, `run_b/implementation`, and `run_c/implementation`.
2. Run three implementation agents in parallel.
3. Run an initial verifier over the three outputs.
4. Ask each implementation agent to critique the other two.
5. Feed critiques back to each agent for one update.
6. Repeat critique, select the best run, and synthesize repair assignments.

## Quick Start

Prefer the bundled script:

```bash
python3 scripts/triad_orchestrator.py \
  --task "Improve this module and test the result" \
  --output ./triad-runs/manual-test \
  --runner mock
```

Use `--runner mock` for dry runs and directory validation. Use `--runner command --command '<your agent command template>'` when wiring a real local agent runner.

Template variables available to `--command`:

- `{agent_id}`: `run_a`, `run_b`, or `run_c` implementation agent id, or `verifier`
- `{run_id}`: `run_a`, `run_b`, `run_c`, or `verifier`
- `{stage}`: workflow stage
- `{prompt_file}`: file containing the generated prompt
- `{output_file}`: file where stdout should be captured by the script

Example:

```bash
python3 scripts/triad_orchestrator.py \
  --task "Refactor the scheduler" \
  --output ./triad-runs/scheduler \
  --runner command \
  --command 'my-agent --agent {agent_id} --prompt-file {prompt_file}'
```

## Output Contract

Always preserve these paths:

```text
<output>/
  run_a/implementation/
  run_b/implementation/
  run_c/implementation/
```

Each run directory receives:

- `result.md`: first implementation
- `verification.md`: verifier report copied into the run
- `critique_round_1.md`: critique of the other two runs
- `update_round_1.md`: updated implementation after feedback
- `critique_round_2.md`: second critique and best-run vote
- `final_repair.md`: final repair assignment from that agent

Top-level outputs:

- `verification.md`: initial verifier report
- `best_run.txt`: selected best run id
- `final_repairs.md`: combined repair assignments
- `summary.md`: concise orchestration summary

## Operating Rules

- Keep each implementation isolated under its own `run_x/implementation` directory.
- Do not let parallel agents mutate the same source tree directly. Ask them to produce patches, plans, diffs, or artifacts under their run directory.
- Use `Promise.allSettled` / equivalent behavior when implementing in another language: one failed implementation agent should not kill the tournament if another run succeeded.
- If all three implementation agents fail, stop and write a failure summary.
- Select the best run by explicit `run_a`, `run_b`, or `run_c` votes in round two; tie-break deterministically by run id.

## References

Read `references/workflow.md` when adapting the workflow to another codebase or agent runtime.
