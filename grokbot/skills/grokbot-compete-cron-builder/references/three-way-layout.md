# Three-Way Challenge Layout

`--shape three_way_challenge` fixes `run_a`, `run_b`, `run_c`, choose 1, one
review round. Moved from v1 `SKILL.md` and `competition-pattern.md`.

`competition_shape=three_way_challenge` resolves to:

```text
candidate_ids = run_a, run_b, run_c
selected_count = 1
selection = oracle, then blind review, then votes without self-votes, then stable id
```

Stages:

1. `proposal`: three candidates produce first results.
2. `initial_verification`: each candidate's `verification.md` records whether
   the oracle measures it at selection or selection relies on review.
3. `peer_review_round_1`: each candidate critiques the other two.
4. `revision_round_1`: each candidate revises its own result.
5. `peer_review_round_2`: each candidate critiques revised peers and votes.
6. `repair_synthesis`: each candidate writes final repair assignments.

`artifact_layout=old_three_way` preserves:

```text
<output>/
  run_a/implementation/
  run_b/implementation/
  run_c/implementation/
  verification.md
  best_run.txt
  final_repairs.md
  summary.md
```

Each candidate directory contains:

- `result.md`
- `verification.md`
- `critique_round_1.md`
- `update_round_1.md`
- `critique_round_2.md`
- `final_repair.md`

Native manifests and JSON summaries may supplement these artifacts. Under
`old_three_way`, they do not replace them.

## Shapes Before v2

```text
three_way_challenge
  run_a/run_b/run_c, verifier, peer reviews, revision, vote, repair synthesis.

parallel_proposals
  N independent candidates, choose best or top-k.

coverage_sweep
  Candidates search for findings. Select all valid findings after dedupe.

repair_search
  Candidates propose repair paths. Select primary repair and fallback.

top_k_synthesis
  Candidates produce diverse plans. Select 2-3 and synthesize.
```

v2 maps `parallel_proposals`, `coverage_sweep`, `repair_search`, and
`top_k_synthesis` onto `lanes` with an explicit question type and k.
