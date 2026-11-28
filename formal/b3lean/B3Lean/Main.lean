/-
  B3Lean.Main — CLI entry point for `b3lean check` and `b3lean cert`.
  Decodes `b3ehive-stack-ir/v1` JSON emitted by `validate_blueprint_stack.py export-ir`.
-/
import Lean.Data.Json
import B3Lean.Core
import B3Lean.Soundness

open Lean (Json)
open B3Lean

namespace B3Lean.CLI

def splitNodeId (s : String) : Except String NodeId :=
  match s.splitOn "#" with
  | [bp, item] => .ok { bp := bp, item := item }
  | _          => .error s!"invalid NodeId '{s}' (expected '<bp>#<item>')"

def parseRole : String → Except String Role
  | "master"   => .ok .master
  | "platform" => .ok .platform
  | "leaf"     => .ok .leaf
  | other      => .error s!"invalid role '{other}'"

def parseMark : String → Except String Mark
  | "open"      => .ok .open_
  | "submitted" => .ok .submitted
  | "accepted"  => .ok .accepted
  | other       => .error s!"invalid state '{other}'"

def parseEdgeKind : String → Except String EdgeKind
  | "local"   => .ok .local_
  | "cross"   => .ok .cross
  | "harvest" => .ok .harvest
  | other     => .error s!"invalid edge kind '{other}'"

def parsePathPolicy : String → Except String PathPolicy
  | "dag_ordered"     => .ok .dagOrdered
  | "strict_disjoint" => .ok .strictDisjoint
  | other             => .error s!"invalid owned_paths_policy '{other}'"

def getStrArr (j : Json) (key : String) : Except String (List String) :=
  match j.getObjVal? key with
  | .error _ => .ok []
  | .ok arr  => do
    let items ← arr.getArr?
    items.toList.mapM (·.getStr?)

def layerIdx (layers : List String) (name : String) : Nat :=
  (layers.findIdx? (· == name)).getD 0

def parseNode (layers : List String) (j : Json) : Except String ItemNode := do
  let bp ← (← j.getObjVal? "blueprint_id").getStr?
  let item ← (← j.getObjVal? "item_id").getStr?
  let role ← parseRole (← (← j.getObjVal? "role").getStr?)
  let mark ← parseMark (← (← j.getObjVal? "state").getStr?)
  let layerStr := match j.getObjVal? "layer" with
    | .ok (.str s) => s
    | _            => ""
  let budgetLoc := match j.getObjVal? "budget_loc" with
    | .ok (.num n) => n.mantissa.toNat
    | _            => 0
  let hasOracle := match j.getObjVal? "has_oracle" with
    | .ok (.bool b) => b
    | _             => false
  let isHarvest := match j.getObjVal? "harvest" with
    | .ok (.bool b) => b
    | _             => false
  let ownedPaths ← match j.getObjVal? "owned_paths" with
    | .error _ => pure []
    | .ok arr  => do
      let outer ← arr.getArr?
      outer.toList.mapM fun p => do
        let segs ← p.getArr?
        segs.toList.mapM (·.getStr?)
  let caps ← getStrArr j "capabilities"
  return {
    id           := { bp := bp, item := item }
    role         := role
    mark         := mark
    layerRank    := layerIdx layers layerStr
    budgetLoc    := budgetLoc
    hasOracle    := hasOracle
    isHarvest    := isHarvest
    ownedPaths   := ownedPaths
    capabilities := caps
  }

def parseEdge (j : Json) : Except String Edge := do
  let src ← splitNodeId (← (← j.getObjVal? "from").getStr?)
  let dst ← splitNodeId (← (← j.getObjVal? "to").getStr?)
  let kind ← parseEdgeKind (← (← j.getObjVal? "kind").getStr?)
  return { src := src, dst := dst, kind := kind }

def parseStackIR (content : String) : Except String StackIR := do
  let j ← Json.parse content
  let layers ← getStrArr j "layers"
  let budgetCap := match j.getObjVal? "default_budget_loc_cap" with
    | .ok (.num n) => n.mantissa.toNat
    | _            => 5000
  let policyStr := match j.getObjVal? "owned_paths_policy" with
    | .ok (.str s) => s
    | _            => "dag_ordered"
  let pathPolicy ← parsePathPolicy policyStr
  let nodesArr ← (← j.getObjVal? "nodes").getArr?
  let nodes ← nodesArr.toList.mapM (parseNode layers)
  let edgesArr ← (← j.getObjVal? "edges").getArr?
  let edges ← edgesArr.toList.mapM parseEdge
  let topoStrs ← getStrArr j "topo_witness"
  let topo ← topoStrs.mapM splitNodeId
  let mandStrs ← getStrArr j "mandatory_leaf_deps"
  let mand ← mandStrs.mapM splitNodeId
  let promoted ← getStrArr j "promoted_capabilities"
  -- Include any capability declared on a platform node as promoted.
  let platformCaps := nodes.foldl (fun acc n => if n.role == .platform then acc ++ n.capabilities else acc) []
  return {
    budgetCap     := budgetCap
    pathPolicy    := pathPolicy
    nodes         := nodes
    edges         := edges
    topoWitness   := topo
    mandatoryDeps := mand
    promotedCaps  := (promoted ++ platformCaps).eraseDups
  }

def reportFailures (ir : StackIR) : List String :=
  let checks : List (String × Bool) := [
    ("topo_acyclic", checkTopo ir),
    ("local_layers_monotonic", checkLocalLayers ir),
    ("boundary_clean", checkBoundaries ir),
    ("transitive_accepted", checkTransitiveAccepted ir),
    ("paths_non_interfering", checkPaths ir),
    ("rule_of_two_clean", checkRuleOfTwo ir),
    ("items_bounded", checkItemsBounded ir)
  ]
  (checks.filter (fun p => !p.2)).map (·.1)

def quoteStr (s : String) : String :=
  let esc := s.replace "\\" "\\\\" |>.replace "\"" "\\\""
  s!"\"{esc}\""

def renderStrList (xs : List String) : String :=
  "[" ++ String.intercalate ", " (xs.map quoteStr) ++ "]"

def renderNodeId (n : NodeId) : String :=
  s!"⟨{quoteStr n.bp}, {quoteStr n.item}⟩"

def renderRole : Role → String
  | .master   => ".master"
  | .platform => ".platform"
  | .leaf     => ".leaf"

def renderMark : Mark → String
  | .open_     => ".open_"
  | .submitted => ".submitted"
  | .accepted  => ".accepted"

def renderEdgeKind : EdgeKind → String
  | .local_  => ".local_"
  | .cross   => ".cross"
  | .harvest => ".harvest"

def renderPathPolicy : PathPolicy → String
  | .dagOrdered     => ".dagOrdered"
  | .strictDisjoint => ".strictDisjoint"

def renderNode (n : ItemNode) : String :=
  let paths := "[" ++ String.intercalate ", " (n.ownedPaths.map renderStrList) ++ "]"
  s!"\{ id := {renderNodeId n.id}, role := {renderRole n.role}, mark := {renderMark n.mark}, layerRank := {n.layerRank}, budgetLoc := {n.budgetLoc}, hasOracle := {n.hasOracle}, isHarvest := {n.isHarvest}, ownedPaths := {paths}, capabilities := {renderStrList n.capabilities} }"

def renderEdge (e : Edge) : String :=
  s!"\{ src := {renderNodeId e.src}, dst := {renderNodeId e.dst}, kind := {renderEdgeKind e.kind} }"

def renderStackIR (ir : StackIR) : String :=
  let nodesStr := "[\n    " ++ String.intercalate ",\n    " (ir.nodes.map renderNode) ++ "\n  ]"
  let edgesStr := "[\n    " ++ String.intercalate ",\n    " (ir.edges.map renderEdge) ++ "\n  ]"
  let topoStr := "[" ++ String.intercalate ", " (ir.topoWitness.map renderNodeId) ++ "]"
  let mandStr := "[" ++ String.intercalate ", " (ir.mandatoryDeps.map renderNodeId) ++ "]"
  String.intercalate "\n" [
    "{",
    s!"  budgetCap := {ir.budgetCap},",
    s!"  pathPolicy := {renderPathPolicy ir.pathPolicy},",
    s!"  nodes := {nodesStr},",
    s!"  edges := {edgesStr},",
    s!"  topoWitness := {topoStr},",
    s!"  mandatoryDeps := {mandStr},",
    s!"  promotedCaps := {renderStrList ir.promotedCaps}",
    "}"
  ]

def emitCertLean (ir : StackIR) : String :=
  String.intercalate "\n" [
    "import B3Lean.Core",
    "import B3Lean.Soundness",
    "",
    "open B3Lean",
    "",
    s!"def certIR : StackIR :=\n{renderStackIR ir}",
    "",
    "theorem cert_stack_certified : StackCertified certIR :=",
    "  checkStack_sound certIR rfl",
    "",
    "#print axioms cert_stack_certified",
    ""
  ]

def usage : String :=
  "Usage:\n  b3lean check <stack_ir.json>\n  b3lean cert <stack_ir.json> [-o <StackCert.lean>]"

end B3Lean.CLI

def main (args : List String) : IO UInt32 := do
  match args with
  | ["check", path] =>
    let txt ← IO.FS.readFile path
    match B3Lean.CLI.parseStackIR txt with
    | .error e =>
      IO.eprintln s!"ERROR: {e}"
      return 2
    | .ok ir =>
      if B3Lean.checkStack ir then
        IO.println s!"b3lean CERTIFIED: {ir.nodes.length} nodes, {ir.edges.length} edges (checkStack_sound)."
        return 0
      else
        let fails := B3Lean.CLI.reportFailures ir
        IO.eprintln s!"b3lean FAILED invariants: {String.intercalate ", " fails}"
        return 1
  | ["cert", path] =>
    let txt ← IO.FS.readFile path
    match B3Lean.CLI.parseStackIR txt with
    | .error e =>
      IO.eprintln s!"ERROR: {e}"
      return 2
    | .ok ir =>
      if !B3Lean.checkStack ir then
        let fails := B3Lean.CLI.reportFailures ir
        IO.eprintln s!"b3lean FAILED invariants before cert emission: {String.intercalate ", " fails}"
        return 1
      IO.print (B3Lean.CLI.emitCertLean ir)
      return 0
  | ["cert", path, "-o", outPath] =>
    let txt ← IO.FS.readFile path
    match B3Lean.CLI.parseStackIR txt with
    | .error e =>
      IO.eprintln s!"ERROR: {e}"
      return 2
    | .ok ir =>
      if !B3Lean.checkStack ir then
        let fails := B3Lean.CLI.reportFailures ir
        IO.eprintln s!"b3lean FAILED invariants before cert emission: {String.intercalate ", " fails}"
        return 1
      IO.FS.writeFile outPath (B3Lean.CLI.emitCertLean ir)
      IO.println s!"b3lean wrote kernel certificate: {outPath}"
      return 0
  | _ =>
    IO.eprintln B3Lean.CLI.usage
    return 2
