# Compete Lessons

| v1 rule | v2 location | Change |
|---|---|---|
| Competition contract, inputs table | SKILL.md Decide | `auto` question type removed; the caller decides |
| m/k policy table | SKILL.md Decide starting points | unchanged values |
| Three-way challenge, old layout | `three-way-layout.md` | selection now oracle-first |
| `best_one`, `top_k`, `repair_queue` | SKILL.md Select | v1 picked the first ids; v2 ranks by oracle, blind review, votes |
| `vote_then_tiebreak` | SKILL.md Select step 3 | self-votes void; only explicit `selected_candidate_id:` lines count |
| `coverage_union`, `risk_union` | SKILL.md Select, Coverage | v1 concatenated; v2 dedupes findings with reproductions and ranks by severity |
| All-settled runtime rule | script `run_stage` | v1 aborted on any later-stage failure; v2 drops only the failed candidate |
| Execution and looper handoff | SKILL.md Hand Off; `core.md` Compose | `--parent-lease-ref` is enforced |
| Output discipline | `core.md` Practice: Write | — |

Origin: 3d4fa0a (compete replaces debate), f054d11 (contract upgrade).

## 2.2.0

Guard-set regressions, `OBSERVED_ONLY`, integrity suspicion with two-channel confirmation, shadow mode.
