# Execution Lessons

v2 moved rules out of the SKILL.md body; nothing was dropped. This table shows
where each v1 section lives and the commit that introduced it.

| v1 section | v2 location | Origin |
|---|---|---|
| Non-Negotiable Invariants 1–3, 9–10 | `core.md` laws 1, 4, 6; SKILL.md Acceptance | 761967f, 9e39564 |
| Non-Negotiable Invariants 4–8 | `transport-codex-tui.md` Transport Invariants | 22dfb3a, c25824b, c563ee9 |
| Portability Hard Gate, Repository Discovery | SKILL.md Specification; `execution-pattern.md` §1 | 22dfb3a |
| Blueprint Protocol, same-name Gantt | SKILL.md Blueprint; `execution-pattern.md` §2 | fb060cf |
| Task Isolation | SKILL.md Claims And Workspaces; `execution-pattern.md` §3 | 9e39564 |
| Codex Transport, Launch, Goal Handshake, Startup, Liveness | `transport-codex-tui.md` | 22dfb3a |
| Other Agent Platforms | `transport-codex-tui.md`; `substrate-cron.md` | 76cb266 |
| Claims And Handoff | `execution-pattern.md` §4 | 04dbbc1 |
| Concurrency And Admission | SKILL.md Admission; `execution-pattern.md` §6 | bafab03, c25824b |
| Scheduler Tick | SKILL.md Scheduler Tick; `execution-pattern.md` §7 | 52e4ff0 |
| Master Integration | SKILL.md Acceptance; `execution-pattern.md` §8 | 669ca7b |
| Budgets And Cleanup | `execution-pattern.md` §9; `substrate-cron.md` | a90ad1a |
| Generated Validation | `gate-rules.md` Generated Validation | c563ee9, d967f08 |
| Output Discipline (other skills) | `core.md` Practice: Write | d04c918 |

New in v2: item grammar (`oracle`, `tier`, `budget`, `canon`, `other#ID`),
receipts, fresh re-runs, the checkbox and oracle guards, family rotation on
rejection, substrate choice, and controller version stamps.

## 2.2.0

Effects and retries: intent and readback, retry table by failure kind, revision fence at every admission, receipt fingerprint over untracked content, typed item closure.
