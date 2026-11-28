# Multi-Layer Stacks, Occam Factoring, And Lean 4 Verification

On-demand detail for `execution-cron-builder/SKILL.md`. Names and paths are
placeholders.

## 1. When To Split (Occam & Constant `k`)

Stay on one flat blueprint until multiple targets share a real platform.
Factoring obeys minimum generative (Kolmogorov) complexity:

- Optimize `k + M + N` vs `M * N`, not asymptotic `O(M + N)` alone. If
  abstraction, glue, and coordination overhead `k` exceed the duplication it
  removes, keep code local.
- Target **2,000–5,000 LOC** per executable item directly. Do not split into
  ceremonial micro-items (<500 LOC) or build speculative empty middle platforms.

## 2. Three Roles And Stack Manifest (`blueprint_stack.json`)

| Role | Owns | Allowed Cross-Blueprint Edges |
|---|---|---|
| `master` | Global mandates, wave gates, shared canon | `platform`, `leaf` (wave closure) |
| `platform` | Shared contracts and promoted modules (single writer: `master` or `steward`) | `master`; `leaf` only on `harvest: true` items |
| `leaf` | One target's code and gates | `master`, `platform` — **never a sibling `leaf`** |

Minimal manifest (`templates/blueprint-stack.json`):

```json
{
  "schema_version": "b3ehive-blueprint-stack/v1",
  "stack_id": "<id>",
  "owned_paths_policy": "dag_ordered",
  "default_budget_loc_cap": 5000,
  "layers": ["L0", "L1", "L2", "L3", "L4"],
  "blueprints": [
    {"blueprint_id": "top", "role": "master", "path": "docs/00_Master_Blueprint.md"},
    {"blueprint_id": "plt", "role": "platform", "path": "docs/01_Platform_Blueprint.md"},
    {"blueprint_id": "a", "role": "leaf", "path": "docs/TargetA_Blueprint.md"}
  ],
  "mandatory_leaf_deps": ["plt#PLT-001"],
  "boundaries": {"platform_root": "platform", "leaf_roots": {"a": "targets/a"}}
}
```

## 3. Six Irreducible Invariants

Checked by `scripts/validate_blueprint_stack.py`:

1. **Global uniqueness & acyclicity**: unique `blueprint_id` and item IDs; the
   union of local and `other#ID` edges is acyclic (with `topo_witness`).
2. **Concurrent path non-interference**: under `dag_ordered` (recommended for
   multi-layer repos), two items with overlapping/nested `owned_paths` must be
   ordered in the DAG (`u <* v`); under `strict_disjoint`, no overlap is allowed.
3. **Transitive `[x]` closure**: no `[x]` item depends on `[ ]` or `[_]`.
4. **Strict layer & boundary direction**: local `layer(dep) <= layer(item)`;
   zero `leaf -> leaf`; `platform -> leaf` requires `harvest: true`.
5. **Rule-of-Two factoring**: when `>= 2` leaves tag the same `capability:`
   without a corresponding `platform` item/module, promote only if net
   compression holds; otherwise split or keep distinct.
6. **Source boundary isolation (`boundaries`)**: zero sibling imports
   (`leaf_i -> leaf_j`) and zero reverse imports (`platform -> leaf`).

## 4. Revisions And IR Export

- **Minor**: append new IDs + `DECIDE`; never mutate `[x]` history.
- **Major**: open `<Name>_Rev2_Blueprint.md` with a `keep` (inherits prior
  oracles as non-regression gates) vs `rebuild` (delete old code only after new
  gates pass) table and numeric Baseline → Target thresholds.
- **IR Export**: `scripts/validate_blueprint_stack.py export-ir <manifest>`
  emits canonical `stack_ir.json` (+ `topo_witness`) for formal verification.

## 5. Lean 4 Formal Certification (`formal/b3elean/`)

When Lean `v4.34.0` (`lake`, `lean`, `leanchecker`) is present, certify the
stack with zero Mathlib overhead:

- **Per-tick native check**: `scripts/verify_lean.py stack <manifest>` runs
  the compiled `b3elean` binary whose `checkStack_sound` theorem is kernel-proved
  (`topo_acyclic_sound`, `dag_ordered_noninterference`, `checkBoundaries_sound`,
  `checkTransitiveAccepted_sound`, `checkRuleOfTwo_sound`,
  `occam_no_gain_for_single_leaf`, `major_revision_non_regression`).
- **Release / layer kernel witness**: add `--cert` to emit `StackCert.lean`,
  prove `StackCertified certIR` by kernel `rfl`, and audit `#print axioms`.
- **High-value contract oracles (`oracle: lean:<Module>.<Theorem>`)**: use only
  when formal assurance beats constant `k`. Keep theorem signatures in
  read-only `Specs/*.lean` outside worker `owned_paths`, and verify with
  `scripts/verify_lean.py oracle` (`lake build` + external `leanchecker` +
  allowlist `{propext, Classical.choice, Quot.sound}`; rejects `sorryAx`,
  custom `axiom`, and `native_decide`).
- **Degradation**: set `B3_FORMAL_VERIFIER=off` (or omit Lean) to run purely on
  `validate_blueprint_stack.py`.
