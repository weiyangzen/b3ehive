# Multi-Layer Blueprints And Occam Factoring (Experimental)

[中文](multi-layer-and-anti-cartesian.zh-CN.md)

Branch `exp/multilayer-anticartesian` adds minimal support for multi-layer
blueprint stacks and anti-Cartesian factoring.

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
