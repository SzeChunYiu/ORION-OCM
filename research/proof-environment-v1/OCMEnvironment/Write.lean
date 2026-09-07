import CheckedExport
import OCMEnvironment.Packet
import OCMEnvironment.Prepare
namespace OCMEnvironment
open Lean
def writeJson (path : System.FilePath) (j : Json) : IO Unit := IO.FS.writeFile path (j.compress ++ "\n")
def writeEnvironment (path : System.FilePath) (env : Environment) (names : Array Name) : IO Unit := do
  let handle ← IO.FS.Handle.mk path .write
  IO.withStdout (.ofHandle handle) <| CheckedExport.M.run env.toKernelEnv do
    CheckedExport.initState env.toKernelEnv
    CheckedExport.dumpMetadata
    for n in names.qsort Name.lt do CheckedExport.dumpConstant n
  handle.flush
  let restored ← readPacket path
  let expected := checkedMap env
  if restored.state.constMap.size != expected.size then
    throw <| IO.userError "SERIALIZED_MEMBERSHIP_SIZE"
  for (name, ci) in expected.toList do
    let some actual := restored.state.constMap[name]? | throw <| IO.userError s!"SERIALIZED_MISSING {name}"
    unless exactInfo ci actual do throw <| IO.userError s!"SERIALIZED_DECLARATION_MISMATCH {name}"
def writeExpression (path : System.FilePath) (env : Environment) (name : Name)
    (params : List Name) (expr : Expr) : IO Json := do
  let handle ← IO.FS.Handle.mk path .write
  let descriptor ← IO.withStdout (.ofHandle handle) <| M.run env do
    initState env
    modify fun s => {s with visitedConstants := env.constants.fold (fun ns n _ => ns.insert n) ({} : NameHashSet)}
    dumpMetadata
    let nidx ← dumpName name
    let levelParams ← dumpUparams params
    let root ← dumpExpr expr
    return Json.mkObj [("target", toJson name.toString), ("target_name_index", toJson nidx),
      ("target_level_params", levelParams), ("target_root", toJson root)]
  handle.flush
  let restored ← readPacket path true
  let root ← IO.ofExcept <| descriptor.getObjValAs? Nat "target_root"
  let some restoredExpr := restored.state.exprMap[root]? | throw <| IO.userError "SERIALIZED_TARGET_ROOT"
  if restoredExpr != expr then throw <| IO.userError "SERIALIZED_TARGET_MISMATCH"
  let indices ← IO.ofExcept <| descriptor.getObjValAs? (Array Nat) "target_level_params"
  let restoredParams ← indices.toList.mapM fun i => do
    let some n := restored.state.nameMap[i]? | throw <| IO.userError "SERIALIZED_UNIVERSE_INDEX"
    pure n
  if restoredParams != params then throw <| IO.userError "SERIALIZED_UNIVERSES"
  let nameIndex ← IO.ofExcept <| descriptor.getObjValAs? Nat "target_name_index"
  if restored.state.nameMap[nameIndex]? != some name then throw <| IO.userError "SERIALIZED_TARGET_NAME"
  return descriptor
def registration (p : Prepared) (target : Json) : Json :=
  target.setObjVal! "schema" "ocm.proof-environment.registration.v1"
    |>.setObjVal! "allowed" (namesJson (p.closure.names.qsort Name.lt))
    |>.setObjVal! "axioms" (namesJson p.policy.axioms)
    |>.setObjVal! "max_heartbeats" (toJson p.policy.maxHeartbeats)
    |>.setObjVal! "max_rec_depth" (toJson p.policy.maxRecDepth)
    |>.setObjVal! "normalization" normalizationVersion
def inventory (p : Prepared) : Json := Json.mkObj [
  ("schema", "ocm.proof-environment.inventory.v1"),
  ("names", namesJson (p.closure.names.qsort Name.lt)),
  ("edges", toJson (p.closure.edges.map (fun (a,b) => #[a.toString,b.toString])))]
end OCMEnvironment
