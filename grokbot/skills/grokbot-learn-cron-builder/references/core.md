# b3ehive core v2

Seven laws bind compete, execution, learn, optimization, and looper. Each law is
stated here once; a skill adds only its local rules.

## Laws

1. One authority. A run has one blueprint. States: `[ ]` open, `[_]` submitted,
   `[x]` accepted. Runtime words such as paused, done, or blocked are telemetry.
2. Oracle first. Each item names its judge before work: a gate when one can
   exist, else a non-author reviewer with a written protocol. A missing oracle is
   the first item to build. Workers never touch oracles, fixtures, baselines, or
   thresholds.
3. Cite before you claim. A decision resting on an external fact cites a pinned
   canon entry. An `[I]` fact is confirmed by a gate before any dependent item
   is accepted.
4. Accept only what you re-run. Every submission carries a receipt: argv, exit
   code, output hashes, tree SHA, clean tree before and after. The master
   re-runs it and recomputes metrics from raw rows; where results can be gamed,
   on fresh or held-out inputs. Evidence below the item's tier stops at `[_]`.
5. Lease before you spend. Every attempt runs on a lease of tokens, time, money,
   and disk. Attempts without reward accrue toward pause.
6. Isolate honestly. One worker, one workspace, one state. Count every model
   process and request; nested agents are declared and counted. Prove liveness
   by identity, never by process names. Materialize the least the oracle needs.
7. Observe instruments; change them apart. Log friction with skills, scripts,
   validators, and routes apart from task progress. An instrument change is its
   own item, revertible, and weakens no law.

## Lexicon

Each verb has one meaning and fixed subjects. A sentence that pairs a verb with
another subject is an error.

| Verb | Meaning | Subjects |
|---|---|---|
| claim | take an open item | worker |
| submit | hand over a candidate and its receipt; the item becomes `[_]` | worker, nested run |
| measure | produce numbers | oracle |
| judge | return a typed verdict | non-author reviewer |
| accept | move `[_]` to `[x]` after a re-run | master |
| reject | return an item to `[ ]` with notes | master |
| revert | restore the last accepted state | master, ratchet |
| lease | grant budget | looper |
| pause, retire | stop granting budget; end a loop | looper, operator |
| cite | reference a canon entry by id | any |
| log | record instrument friction | any |
| decide | write a `DECIDE` line | whoever chooses |

## Practice

- Decide: log each nontrivial choice as
  `DECIDE <param>=<value> because <reason>; else <fallback>`. Fixed numbers serve
  only safety, budget, external reality, or compatibility.
- Compose: a skill calls another inside the caller's lease. The callee submits.
  Depth stays at most 3 unless the blueprint says otherwise.
- Mechanize: a rule that must never break becomes a generated check (gate, hook,
  CI job, lint), not a repeated sentence.
- Bind instruments: probe a profiler, analyzer, or MCP server before use; record
  it in `instruments.tsv` with its playbook.
- Write: one fact per sentence; judgment lives in the verb. Code, commands,
  paths, schemas, enums, state marks, numbers, and quotes stay exact. No
  narration, preview, or recap.
