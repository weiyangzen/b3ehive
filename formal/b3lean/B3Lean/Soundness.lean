/-
  B3Lean.Soundness — Executable witness checkers + kernel-verified soundness
  and meta-theorems (Init-only, zero sorry, standard axioms only).
-/
import B3Lean.Core

namespace B3Lean

/-! ### 1. Topological Witness Checker & Acyclicity Proof (T1) -/

def topoRank (topo : List NodeId) (nid : NodeId) : Option Nat :=
  topo.findIdx? (· == nid)

def checkTopoEdge (topo : List NodeId) (e : Edge) : Bool :=
  match topoRank topo e.src, topoRank topo e.dst with
  | some r1, some r2 => decide (r1 < r2)
  | _, _             => false

def checkTopo (ir : StackIR) : Bool :=
  ir.edges.all (checkTopoEdge ir.topoWitness)

theorem checkTopoEdge_lt {topo : List NodeId} {e : Edge}
    (h : checkTopoEdge topo e = true) :
    ∃ r1 r2, topoRank topo e.src = some r1 ∧ topoRank topo e.dst = some r2 ∧ r1 < r2 := by
  unfold checkTopoEdge at h
  cases h1 : topoRank topo e.src with
  | none => simp [h1] at h
  | some r1 =>
    cases h2 : topoRank topo e.dst with
    | none => simp [h1, h2] at h
    | some r2 =>
      simp [h1, h2] at h
      exact ⟨r1, r2, rfl, rfl, h⟩

theorem edgePath_topoRank_lt {topo : List NodeId} {edges : List Edge}
    (hall : ∀ e ∈ edges, checkTopoEdge topo e = true)
    {u v : NodeId} (hp : EdgePath edges u v) :
    ∃ r1 r2, topoRank topo u = some r1 ∧ topoRank topo v = some r2 ∧ r1 < r2 := by
  induction hp with
  | step he => exact checkTopoEdge_lt (hall _ he)
  | trans _ _ ih1 ih2 =>
    rcases ih1 with ⟨r1, r2, h1, h2, hlt1⟩
    rcases ih2 with ⟨r2', r3, h2', h3, hlt2⟩
    rw [h2] at h2'
    cases h2'
    exact ⟨r1, r3, h1, h3, Nat.lt_trans hlt1 hlt2⟩

/-- T1: A verified linear topological witness proves global DAG acyclicity. -/
theorem topo_acyclic_sound (ir : StackIR) (h : checkTopo ir = true) :
    IsAcyclic ir.edges := by
  intro u hcyc
  have hall : ∀ e ∈ ir.edges, checkTopoEdge ir.topoWitness e = true :=
    List.all_eq_true.mp h
  rcases edgePath_topoRank_lt hall hcyc with ⟨r1, r2, h1, h2, hlt⟩
  rw [h1] at h2
  cases h2
  exact Nat.lt_irrefl r1 hlt

/-! ### 2. Bounded-Fuel Reachability & Path Non-Interference (T2) -/

def hasPathFuel (edges : List Edge) : Nat → NodeId → NodeId → Bool
  | 0, _, _ => false
  | fuel + 1, u, target =>
    edges.any fun e =>
      e.src == u && (e.dst == target || hasPathFuel edges fuel e.dst target)

theorem hasPathFuel_sound (edges : List Edge) (fuel : Nat) (u target : NodeId)
    (h : hasPathFuel edges fuel u target = true) : EdgePath edges u target := by
  induction fuel generalizing u with
  | zero => simp [hasPathFuel] at h
  | succ n ih =>
    simp [hasPathFuel, List.any_eq_true] at h
    rcases h with ⟨e, he, hsrc, hrest⟩
    have hu : e.src = u := by simpa using hsrc
    cases hrest with
    | inl hdst =>
      have ht : e.dst = target := by simpa using hdst
      cases e with
      | mk s d k =>
        simp at hu ht
        subst hu; subst ht
        exact EdgePath.step he
    | inr hrec =>
      cases e with
      | mk s d k =>
        simp at hu
        subst hu
        exact EdgePath.trans (EdgePath.step he) (ih d hrec)

def nodesOverlapBool (u v : ItemNode) : Bool :=
  u.ownedPaths.any (fun pa => v.ownedPaths.any (fun pb => pathOverlaps pa pb))

theorem nodesOverlapBool_of_overlap {u v : ItemNode} (h : NodePathsOverlap u v) :
    nodesOverlapBool u v = true := by
  rcases h with ⟨pa, hpa, pb, hpb, hov⟩
  unfold nodesOverlapBool
  rw [List.any_eq_true]
  exact ⟨pa, hpa, List.any_eq_true.mpr ⟨pb, hpb, hov⟩⟩

def checkPathPair (ir : StackIR) (u v : ItemNode) : Bool :=
  if u.id == v.id then true
  else if !nodesOverlapBool u v then true
  else match ir.pathPolicy with
    | .strictDisjoint => false
    | .dagOrdered =>
      let fuel := ir.nodes.length
      hasPathFuel ir.edges fuel u.id v.id || hasPathFuel ir.edges fuel v.id u.id

def checkPaths (ir : StackIR) : Bool :=
  ir.nodes.all (fun u => ir.nodes.all (fun v => checkPathPair ir u v))

/-- T2: Verified path check guarantees zero concurrent write overlap (antichain non-interference). -/
theorem dag_ordered_noninterference (ir : StackIR) (h : checkPaths ir = true) :
    PathsNonInterfering ir := by
  intro u hu v hv hne hov
  have h1 := List.all_eq_true.mp h u hu
  have hpair := List.all_eq_true.mp h1 v hv
  have hneq_b : (u.id == v.id) = false := beq_false_of_ne hne
  have hov_b : nodesOverlapBool u v = true := nodesOverlapBool_of_overlap hov
  unfold checkPathPair at hpair
  simp [hneq_b, hov_b] at hpair
  cases hpol : ir.pathPolicy with
  | strictDisjoint => simp [hpol] at hpair
  | dagOrdered =>
    simp [hpol] at hpair
    cases hpair with
    | inl h1 => exact Or.inl (hasPathFuel_sound ir.edges ir.nodes.length u.id v.id h1)
    | inr h2 => exact Or.inr (hasPathFuel_sound ir.edges ir.nodes.length v.id u.id h2)

/-! ### 3. Local Layers, Boundaries, Acceptance Closure & Rule-of-Two (T3) -/

def checkLocalLayerEdge (nodes : List ItemNode) (e : Edge) : Bool :=
  if e.kind != .local_ then true
  else match findNode nodes e.src, findNode nodes e.dst with
    | some src, some dst => decide (src.layerRank ≤ dst.layerRank)
    | _, _               => false

def checkLocalLayers (ir : StackIR) : Bool :=
  ir.edges.all (checkLocalLayerEdge ir.nodes)

theorem checkLocalLayers_sound (ir : StackIR) (h : checkLocalLayers ir = true) :
    LocalLayersMonotonic ir := by
  intro e he hloc src dst hsrc hdst
  have h1 := List.all_eq_true.mp h e he
  unfold checkLocalLayerEdge at h1
  simp [hloc, hsrc, hdst] at h1
  exact h1

def checkBoundaryEdge (nodes : List ItemNode) (e : Edge) : Bool :=
  match findNode nodes e.src, findNode nodes e.dst with
  | some src, some dst =>
    let leafOk := !(dst.role == .leaf && src.role == .leaf) || (dst.id.bp == src.id.bp)
    let platOk := !(dst.role == .platform && src.role == .leaf) || (e.kind == .harvest && dst.isHarvest)
    leafOk && platOk
  | _, _ => false

def checkBoundaries (ir : StackIR) : Bool :=
  ir.edges.all (checkBoundaryEdge ir.nodes)

theorem checkBoundaries_sound (ir : StackIR) (h : checkBoundaries ir = true) :
    BoundaryClean ir := by
  intro e he src dst hsrc hdst
  have h1 := List.all_eq_true.mp h e he
  unfold checkBoundaryEdge at h1
  simp [hsrc, hdst] at h1
  rcases h1 with ⟨hleaf, hplat⟩
  constructor
  · intro hd hs
    simp [hd, hs] at hleaf
    exact hleaf
  · intro hd hs
    simp [hd, hs] at hplat
    exact hplat

def checkTransitiveEdge (nodes : List ItemNode) (e : Edge) : Bool :=
  match findNode nodes e.src, findNode nodes e.dst with
  | some src, some dst => !(dst.mark == .accepted) || (src.mark == .accepted)
  | _, _               => false

def checkTransitiveAccepted (ir : StackIR) : Bool :=
  ir.edges.all (checkTransitiveEdge ir.nodes)

theorem checkTransitiveAccepted_sound (ir : StackIR) (h : checkTransitiveAccepted ir = true) :
    TransitiveAccepted ir := by
  intro e he src dst hsrc hdst hacc
  have h1 := List.all_eq_true.mp h e he
  unfold checkTransitiveEdge at h1
  simp [hsrc, hdst, hacc] at h1
  exact h1

def checkRuleOfTwo (ir : StackIR) : Bool :=
  ir.nodes.all fun n =>
    if n.role != .leaf then true
    else n.capabilities.all fun cap =>
      ir.promotedCaps.contains cap || decide ((leafClaimants ir.nodes cap).length ≤ 1)

theorem checkRuleOfTwo_sound (ir : StackIR) (h : checkRuleOfTwo ir = true) :
    RuleOfTwoClean ir := by
  intro n hn hleaf cap hcap
  have h1 := List.all_eq_true.mp h n hn
  simp [hleaf] at h1
  have h2 := h1 cap hcap
  cases h2 with
  | inl hp => exact Or.inl hp
  | inr hl => exact Or.inr hl

def checkItemsBounded (ir : StackIR) : Bool :=
  ir.nodes.all (fun n => n.hasOracle && decide (n.budgetLoc ≤ ir.budgetCap))

theorem checkItemsBounded_sound (ir : StackIR) (h : checkItemsBounded ir = true) :
    ItemsBounded ir := by
  intro n hn
  have h1 := List.all_eq_true.mp h n hn
  simp at h1
  exact h1

/-- Master-only acceptance law: no ValidStep by a non-master produces an accept action. -/
theorem master_only_acceptance {ir ir' : StackIR} {who : Actor} {nid : NodeId}
    (hstep : ValidStep ir (.accept who nid) ir') : who = .master := by
  cases hstep
  rfl

/-! ### 4. Occam Constant-k Kolmogorov Bound & Major Revision Non-Regression (T4) -/

/--
  T4a (Occam / Kolmogorov Necessary Condition — Rule-of-Two):
  If a shared platform module costs at least as much as one local copy (`c ≤ p`),
  promoting a capability used by at most one leaf (`n ≤ 1`) can NEVER reduce
  total generative complexity (`n * c ≤ k + p + n * g`).
-/
theorem occam_no_gain_for_single_leaf (k c p g n : Nat)
    (hn : n ≤ 1) (hp : c ≤ p) :
    n * c ≤ k + p + n * g := by
  cases n with
  | zero => omega
  | succ m =>
    have hm : m = 0 := by omega
    subst hm
    omega

/--
  T4b (Occam / Kolmogorov Net-Compression):
  Replacing duplicated cost `dupCost` with shared cost `k + sharedCost` strictly
  reduces total stack description length iff `k + sharedCost < dupCost`.
-/
theorem occam_factoring_strict_saving (base k dupCost sharedCost : Nat) :
    base + (k + sharedCost) < base + dupCost ↔ k + sharedCost < dupCost := by
  omega

/--
  T4b (Major Revision Non-Regression):
  If Rev2 preserves all Rev1 oracles for every `keep` module, any verification
  passing all Rev2 oracles automatically satisfies every Rev1 oracle on kept modules.
-/
theorem major_revision_non_regression {Mod Oracle : Type}
    (rev1 rev2 : RevisionSpec Mod Oracle) (kept : List Mod)
    (hkeep : KeepsPriorOracles rev1 rev2 kept)
    (passes : Oracle → Prop)
    (hrev2 : ∀ m ∈ kept, ∀ o ∈ rev2.oracles m, passes o) :
    ∀ m ∈ kept, ∀ o ∈ rev1.oracles m, passes o := by
  intro m hm o ho
  exact hrev2 m hm o (hkeep m hm o ho)

/-! ### 5. Master Unified Certified Checker -/

def checkStack (ir : StackIR) : Bool :=
  checkTopo ir &&
  checkLocalLayers ir &&
  checkBoundaries ir &&
  checkTransitiveAccepted ir &&
  checkPaths ir &&
  checkRuleOfTwo ir &&
  checkItemsBounded ir

/-- Master Soundness Theorem: `checkStack ir = true` implies all 7 certified stack invariants. -/
theorem checkStack_sound (ir : StackIR) (h : checkStack ir = true) :
    StackCertified ir := by
  unfold checkStack at h
  simp only [Bool.and_eq_true] at h
  rcases h with ⟨⟨⟨⟨⟨⟨hTopo, hLayers⟩, hBound⟩, hTrans⟩, hPaths⟩, hRoT⟩, hItems⟩
  exact {
    acyclic        := topo_acyclic_sound ir hTopo
    localLayers    := checkLocalLayers_sound ir hLayers
    boundaries     := checkBoundaries_sound ir hBound
    transitiveAcc  := checkTransitiveAccepted_sound ir hTrans
    nonInterfering := dag_ordered_noninterference ir hPaths
    ruleOfTwo      := checkRuleOfTwo_sound ir hRoT
    itemsBounded   := checkItemsBounded_sound ir hItems
  }

end B3Lean
