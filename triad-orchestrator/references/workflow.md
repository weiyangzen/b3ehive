# Triad Workflow Reference

## Stages

1. `implementation`: three agents run in parallel and produce first-pass results.
2. `verification`: a verifier checks that each result is non-empty, task-aligned, and not obviously blocked.
3. `critique_round_1`: each agent critiques the other two results sharply.
4. `update_round_1`: each agent updates its own result using critiques received from peers.
5. `critique_round_2`: each agent critiques the updated peer results and writes an explicit best-run vote.
6. `final_repair`: each agent summarizes issues found and its assigned repair work.

## Prompt Pattern

Implementation prompt:

```text
You are one of three parallel implementation agents.
Your run id is run_a.
Your writable output directory is: <output>/run_a/implementation.
Do not write outside that directory.
Return a concrete result with implementation details, validation steps, risks, and next actions.
```

Verifier prompt:

```text
You are the initial verifier.
Do not implement.
Check run_a/run_b/run_c for non-empty output, task alignment, blockers, warnings, and likely tests.
```

Critique prompt:

```text
Critique the other two runs sharply.
Prioritize correctness, missing tests, maintainability, integration risk, and task fit.
Do not reward verbosity.
```

Best-selection prompt:

```text
Pick one best run.
Write best_run_id: run_a/run_b/run_c.
Explain the decision briefly.
```

## Real Agent Runner Advice

- Use unique sessions per `run_id + stage`.
- Capture stdout/stderr into files even when the runner fails.
- Pass large artifacts by file path when possible instead of embedding entire long outputs.
- Keep the default round count bounded. Two critique passes is enough for most work.
- Prefer patches under `run_x/implementation` over direct source edits when agents run in parallel.
