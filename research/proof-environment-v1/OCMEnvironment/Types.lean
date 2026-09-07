import Comparator.Compare
import Lean.Replay
namespace OCMEnvironment
open Lean
abbrev ConstMap := Std.HashMap Name ConstantInfo
structure RegisteredTarget where
  name : Name
  levelParams : List Name
  type : Expr
structure Policy where
  target : RegisteredTarget
  roots : Array Name
  excluded : NameHashSet
  axioms : Array Name
  maxHeartbeats : Nat
  maxRecDepth : Nat
structure Closure where
  names : Array Name := #[]
  edges : Array (Name × Name) := #[]
structure Prepared where
  env : Environment
  constants : ConstMap
  policy : Policy
  closure : Closure
-- Equality of full parent-normalized kernel records, not source binder interfaces or packet bytes.
-- Parent Expr interning ignores binder names/annotations; all other ConstantInfo fields remain checked.
def exactInfo (a b : ConstantInfo) : Bool := a == b
def normalizationVersion := "lean4export-3.1.0:metadata-erasure,let-nondep-false,alpha-interning"
def namesJson (names : Array Name) : Json := toJson (names.map Name.toString)
def result (operation terminal stage reason : String) (stats := Json.mkObj [])
    (dependencies : Array Name := #[]) (axioms : Array Name := #[])
    (files : Array String := #["result.json"]) : Json := Json.mkObj [
  ("schema", "ocm.proof-environment.result.v1"), ("operation", operation),
  ("terminal", terminal), ("stage", stage), ("reason", reason), ("stats", stats),
  ("dependencies", namesJson dependencies), ("axioms", namesJson axioms), ("files", toJson files)]
end OCMEnvironment
