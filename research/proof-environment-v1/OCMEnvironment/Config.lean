import OCMEnvironment.Packet
import OCMEnvironment.Prepare
namespace OCMEnvironment
open Lean
def readJson (path : System.FilePath) : IO Json := do
  let text ← IO.FS.readFile path
  let j ← IO.ofExcept <| Json.parse text
  if text != j.compress && text != j.compress ++ "\n" then throw <| IO.userError "NONCANONICAL_JSON"
  return j
def getString (j : Json) (k : String) : IO String := IO.ofExcept <| j.getObjValAs? String k
def getNat (j : Json) (k : String) : IO Nat := IO.ofExcept do natural (← field j k)
def getStrings (j : Json) (k : String) : IO (Array String) := IO.ofExcept do
  (← (← field j k).getArr?).mapM Json.getStr?
def lookupName (constants : ConstMap) (s : String) : Except String Name := do
  let names := constants.toList.filterMap fun (n,_) => if n.toString == s then some n else none
  let [name] := names | throw s!"UNKNOWN_OR_AMBIGUOUS_NAME {s}"
  return name
def packetName (p : Packet) (id : Nat) : IO Name := do
  let some n := p.state.nameMap[id]? | throw <| IO.userError s!"TARGET_NAME_INDEX {id}"
  return n
def packetExpr (p : Packet) (id : Nat) : IO Expr := do
  let some e := p.state.exprMap[id]? | throw <| IO.userError s!"EXPRESSION_ROOT_INDEX {id}"
  return e
def targetFrom (j : Json) (p : Packet) (name : Name) : IO RegisteredTarget := do
  let type ← packetExpr p (← getNat j "target_root")
  let params ← IO.ofExcept do (← (← field j "target_level_params").getArr?).mapM natural
  let levelParams ← params.toList.mapM (packetName p)
  if levelParams.contains .anonymous || levelParams.length != (({} : NameHashSet).insertMany levelParams).size then
    throw <| IO.userError "TARGET_UNIVERSE_PARAMETERS"
  return {name, levelParams, type}
def kernelLimits (j : Json) : IO (Nat × Nat) := do
  let hb ← getNat j "max_heartbeats"; let depth ← getNat j "max_rec_depth"
  if hb == 0 || depth == 0 || hb > 18446744073709551615 || depth > 18446744073709551615 then
    throw <| IO.userError "KERNEL_LIMIT_RANGE"
  return (hb,depth)
def preparationPolicy (j : Json) (goal : Packet) (source : ConstMap) : IO Policy := do
  IO.ofExcept <| keys j ["schema", "target", "target_root", "target_level_params", "roots", "excluded", "axioms", "max_heartbeats", "max_rec_depth"]
  if (← getString j "schema") != "ocm.proof-environment.policy.v1" then throw <| IO.userError "POLICY_SCHEMA"
  let name ← IO.ofExcept <| lookupName source (← getString j "target")
  let target ← targetFrom j goal name
  let some (.thmInfo original) := source[name]? | throw <| IO.userError "SOURCE_TARGET_NOT_THEOREM"
  if original.type != target.type || original.levelParams != target.levelParams then
    throw <| IO.userError "INDEPENDENT_TARGET_MISMATCH"
  let roots ← (← getStrings j "roots").mapM (fun s => IO.ofExcept (lookupName source s))
  let excluded ← (← getStrings j "excluded").mapM (fun s => IO.ofExcept (lookupName source s))
  let axioms ← (← getStrings j "axioms").mapM (fun s => IO.ofExcept (lookupName source s))
  let (maxHeartbeats,maxRecDepth) ← kernelLimits j
  return {target, roots, excluded := ({} : NameHashSet).insertMany excluded, axioms, maxHeartbeats, maxRecDepth}
def restorePolicy (j : Json) (goal : Packet) (constants : ConstMap) : IO Policy := do
  IO.ofExcept <| keys j ["schema", "target", "target_name_index", "target_root", "target_level_params", "allowed", "axioms", "max_heartbeats", "max_rec_depth", "normalization"]
  if (← getString j "schema") != "ocm.proof-environment.registration.v1" then throw <| IO.userError "REGISTRATION_SCHEMA"
  if (← getString j "normalization") != normalizationVersion then throw <| IO.userError "NORMALIZATION_VERSION"
  let name ← packetName goal (← getNat j "target_name_index")
  if name.toString != (← getString j "target") then throw <| IO.userError "REGISTERED_NAME_MISMATCH"
  let target ← targetFrom j goal name
  let roots ← (← getStrings j "allowed").mapM (fun s => IO.ofExcept (lookupName constants s))
  if roots.size != constants.size || (({} : NameHashSet).insertMany roots).size != constants.size then
    throw <| IO.userError "REGISTERED_MEMBERSHIP_MISMATCH"
  let axioms ← (← getStrings j "axioms").mapM (fun s => IO.ofExcept (lookupName constants s))
  let (maxHeartbeats,maxRecDepth) ← kernelLimits j
  return {target, roots, excluded := ({} : NameHashSet).insert name, axioms, maxHeartbeats, maxRecDepth}
end OCMEnvironment
