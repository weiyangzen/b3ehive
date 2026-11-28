# Multi-Layer Blueprints, Occam Factoring, And Lean 4 Verification

[中文](multi-layer-and-anti-cartesian.zh-CN.md)

b3ehive v3.0.0 adds minimal support for multi-layer blueprint stacks, Occam
anti-Cartesian factoring, and Lean 4 formal certification inside
`formal/b3lean/`.

## Principle: Minimum Generative Complexity

Keep one flat blueprint when it fits cleanly. Factor into layers only when
shared reuse beats abstraction and coordination overhead `k`:

- Evaluate `k + M + N` against `M * N`, not asymptotic `O(M + N)` alone.
- Target **2,000–5,000 LOC** per executable item directly. Avoid both
  monoliths and micro-items whose ceremony costs more than they save.
- Promote a capability into `platform` only when `>= 2` real leaves share it
  and extraction shrinks total description length (Rule-of-Two with net
  compression). Otherwise keep it local.

## Three-Tier Stack (`blueprint_stack.json`)

| Role | Owns | Cross-Blueprint Dependency Rule |
|---|---|---|
| `master` | Global mandates, wave gates, shared canon | May depend on `platform` and `leaf` (wave closure) |
| `platform` | Shared contracts and promoted modules (single writer) | May depend on `master`; `platform -> leaf` requires `harvest: true` |
| `leaf` | One target's source and gates | May depend on `master` and `platform`; never on a sibling `leaf` |

Each blueprint keeps its own read-only same-name Gantt (`<name>_Gantt.<ext>`).

## Six Irreducible Checks

```bash
bin/b3ehive validate stack blueprint_stack.json --repo-root .
bin/b3ehive validate boundaries blueprint_stack.json --repo-root .
bin/b3ehive validate export-ir blueprint_stack.json --repo-root . -o stack_ir.json
```

1. Unique `blueprint_id` and item IDs; globally acyclic DAG (with `topo_witness`).
2. Local `layer` order preserved (`layer(dep) <= layer(item)`).
3. Prefix-aware path non-interference (`dag_ordered` default: overlapping
   `owned_paths` must be ordered in the DAG; or `strict_disjoint`).
4. Transitive `[x]` acceptance closure across local and `other#ID` edges.
5. Boundary direction (`leaf ↛ leaf`; `platform -> leaf` requires `harvest: true`)
   plus source scan for zero sibling and zero reverse imports.
6. Rule-of-Two check on item `capability:` tags across leaves.

## Revisions

- **Minor**: append new IDs and `DECIDE` lines; never edit accepted `[x]` history.
- **Major**: open `<Name>_Rev2_Blueprint.md` with a `keep` (inherits prior
  oracles as non-regression gates) vs `rebuild` table and numeric targets.

## Lean 4 Formal Certification (`formal/b3lean/`)

Pinned to `leanprover/lean4:v4.34.0` with **zero Mathlib** (`Init` / `Std`
only). Proves four irreducible theorem groups once (`B3Lean/Soundness.lean`):
global DAG acyclicity (`topo_acyclic_sound`), antichain path non-interference
(`dag_ordered_noninterference`), boundary and acceptance safety
(`checkBoundaries_sound`, `checkTransitiveAccepted_sound`,
`master_only_acceptance`), and Occam Rule-of-Two plus Major Revision `keep`
non-regression (`occam_no_gain_for_single_leaf`,
`major_revision_non_regression`).

```bash
bin/b3ehive verify-lean self-check
bin/b3ehive verify-lean stack blueprint_stack.json --repo-root . [--cert]
bin/b3ehive verify-lean oracle lean:Module.Theorem --project path/to/lean --spec-dir Specs
```

Anti-gaming guards enforce read-only `Specs/` protection, external
`leanchecker` verification, and a strict axiom allowlist (`propext`,
`Classical.choice`, `Quot.sound` only — rejecting `sorryAx`, custom axioms, and
`native_decide`). Set `B3_FORMAL_VERIFIER=off` when Lean is not installed.
