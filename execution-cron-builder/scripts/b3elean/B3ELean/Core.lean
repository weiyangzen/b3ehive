/-
  B3ELean.Core — Pure Init-only specification types and invariants for b3ehive
  multi-layer blueprint stacks and Occam anti-Cartesian factoring.
-/
namespace B3ELean

inductive Role where
  | master
  | platform
  | leaf
  deriving DecidableEq, Repr

inductive Mark where
  | open_
  | submitted
  | accepted
  deriving DecidableEq, Repr

inductive EdgeKind where
  | local_
  | cross
  | harvest
  deriving DecidableEq, Repr

inductive PathPolicy where
  | dagOrdered
  | strictDisjoint
  deriving DecidableEq, Repr

inductive Actor where
  | worker
  | reviewer
  | steward
  | master
  | looper
  deriving DecidableEq, Repr

structure NodeId where
  bp   : String
  item : String
  deriving DecidableEq, Repr

abbrev PathSegs := List String

def isPrefixOf (a b : PathSegs) : Bool :=
  a.length ≤ b.length && a == b.take a.length

def pathOverlaps (a b : PathSegs) : Bool :=
  isPrefixOf a b || isPrefixOf b a

structure ItemNode where
  id           : NodeId
  role         : Role
  mark         : Mark
  layerRank    : Nat
  budgetLoc    : Nat
  hasOracle    : Bool
  isHarvest    : Bool
  ownedPaths   : List PathSegs
  capabilities : List String
  deriving DecidableEq, Repr

structure Edge where
  src  : NodeId   -- prerequisite ("from")
  dst  : NodeId   -- dependent ("to")
  kind : EdgeKind
  deriving DecidableEq, Repr

structure StackIR where
  budgetCap     : Nat
  pathPolicy    : PathPolicy
  nodes         : List ItemNode
  edges         : List Edge
  topoWitness   : List NodeId
  mandatoryDeps : List NodeId
  promotedCaps  : List String
  deriving DecidableEq, Repr

/-- Directed reachability along one or more dependency edges. -/
inductive EdgePath (edges : List Edge) : NodeId → NodeId → Prop where
  | step {u v : NodeId} {k : EdgeKind} :
      Edge.mk u v k ∈ edges → EdgePath edges u v
  | trans {u v w : NodeId} :
      EdgePath edges u v → EdgePath edges v w → EdgePath edges u w

/-- A dependency graph is globally acyclic iff no node reaches itself. -/
def IsAcyclic (edges : List Edge) : Prop :=
  ∀ u : NodeId, ¬ EdgePath edges u u

/-- Two nodes have overlapping or prefix-nested owned_paths. -/
def NodePathsOverlap (u v : ItemNode) : Prop :=
  ∃ pa ∈ u.ownedPaths, ∃ pb ∈ v.ownedPaths, pathOverlaps pa pb = true

def findNode (nodes : List ItemNode) (nid : NodeId) : Option ItemNode :=
  nodes.find? (fun n => n.id == nid)

/-- Transitive acceptance closure: no accepted [x] item depends on a non-accepted item. -/
def TransitiveAccepted (ir : StackIR) : Prop :=
  ∀ e ∈ ir.edges, ∀ src dst,
    findNode ir.nodes e.src = some src →
    findNode ir.nodes e.dst = some dst →
    dst.mark = .accepted → src.mark = .accepted

/-- Boundary law: zero leaf->leaf edges; platform->leaf requires harvest edge. -/
def BoundaryClean (ir : StackIR) : Prop :=
  ∀ e ∈ ir.edges, ∀ src dst,
    findNode ir.nodes e.src = some src →
    findNode ir.nodes e.dst = some dst →
    (dst.role = .leaf → src.role = .leaf → dst.id.bp = src.id.bp) ∧
    (dst.role = .platform → src.role = .leaf → e.kind = .harvest ∧ dst.isHarvest = true)

/-- Local layer monotonicity: local edges never invert layer rank. -/
def LocalLayersMonotonic (ir : StackIR) : Prop :=
  ∀ e ∈ ir.edges, e.kind = .local_ → ∀ src dst,
    findNode ir.nodes e.src = some src →
    findNode ir.nodes e.dst = some dst →
    src.layerRank ≤ dst.layerRank

/-- Path non-interference under the stack's declared policy. -/
def PathsNonInterfering (ir : StackIR) : Prop :=
  ∀ u ∈ ir.nodes, ∀ v ∈ ir.nodes, u.id ≠ v.id → NodePathsOverlap u v →
    match ir.pathPolicy with
    | .strictDisjoint => False
    | .dagOrdered     => EdgePath ir.edges u.id v.id ∨ EdgePath ir.edges v.id u.id

/-- Distinct leaf blueprint IDs claiming a given capability. -/
def leafClaimants (nodes : List ItemNode) (cap : String) : List String :=
  (nodes.filter (fun n => n.role == .leaf && n.capabilities.contains cap)).map (fun n => n.id.bp)
    |>.eraseDups

/-- Rule-of-Two: any unpromoted capability is claimed by at most one leaf blueprint. -/
def RuleOfTwoClean (ir : StackIR) : Prop :=
  ∀ n ∈ ir.nodes, n.role = .leaf → ∀ cap ∈ n.capabilities,
    cap ∈ ir.promotedCaps ∨ (leafClaimants ir.nodes cap).length ≤ 1

/-- Every item has an oracle and stays within the stack budget cap. -/
def ItemsBounded (ir : StackIR) : Prop :=
  ∀ n ∈ ir.nodes, n.hasOracle = true ∧ n.budgetLoc ≤ ir.budgetCap

/-- Small-step state transitions enforcing Master-only [x] acceptance (Law 1 & Law 4). -/
inductive Action where
  | claim  (who : Actor) (target : NodeId)
  | submit (who : Actor) (target : NodeId)
  | accept (who : Actor) (target : NodeId)
  | reject (who : Actor) (target : NodeId)
  deriving DecidableEq, Repr

def setMark (nodes : List ItemNode) (target : NodeId) (m : Mark) : List ItemNode :=
  nodes.map (fun n => if n.id == target then { n with mark := m } else n)

inductive ValidStep : StackIR → Action → StackIR → Prop where
  | workerSubmit {ir : StackIR} {nid : NodeId} {n : ItemNode} :
      findNode ir.nodes nid = some n →
      n.mark = .open_ →
      ValidStep ir (.submit .worker nid) { ir with nodes := setMark ir.nodes nid .submitted }
  | masterAccept {ir : StackIR} {nid : NodeId} {n : ItemNode} :
      findNode ir.nodes nid = some n →
      n.mark = .submitted →
      (∀ e ∈ ir.edges, e.dst = nid → ∀ src, findNode ir.nodes e.src = some src → src.mark = .accepted) →
      ValidStep ir (.accept .master nid) { ir with nodes := setMark ir.nodes nid .accepted }
  | masterReject {ir : StackIR} {nid : NodeId} {n : ItemNode} :
      findNode ir.nodes nid = some n →
      n.mark = .submitted →
      ValidStep ir (.reject .master nid) { ir with nodes := setMark ir.nodes nid .open_ }

/-- Major revision non-regression: every kept module retains all prior oracles. -/
structure RevisionSpec (Mod Oracle : Type) where
  oracles : Mod → List Oracle

def KeepsPriorOracles {Mod Oracle : Type}
    (rev1 rev2 : RevisionSpec Mod Oracle) (kept : List Mod) : Prop :=
  ∀ m ∈ kept, ∀ o ∈ rev1.oracles m, o ∈ rev2.oracles m

/-- Combined stack invariants certified by B3ELean. -/
structure StackCertified (ir : StackIR) : Prop where
  acyclic         : IsAcyclic ir.edges
  localLayers     : LocalLayersMonotonic ir
  boundaries      : BoundaryClean ir
  transitiveAcc   : TransitiveAccepted ir
  nonInterfering  : PathsNonInterfering ir
  ruleOfTwo       : RuleOfTwoClean ir
  itemsBounded    : ItemsBounded ir

end B3ELean
