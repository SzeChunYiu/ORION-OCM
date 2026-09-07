import OCMCoverage.Association
import OCMCoverage.Transport
namespace OCMCoverage
open Lean

def constants (env : Environment) : OCMEnvironment.ConstMap :=
  env.constants.fold (fun result name ci => result.insert name ci) {}
def kind (ci : ConstantInfo) : String := match ci with
  | .axiomInfo _ => "axiom" | .defnInfo _ => "definition" | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque" | .quotInfo _ => "quotient" | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor" | .recInfo _ => "recursor"
def writeSource (path : System.FilePath) (env : Environment) (closure : OCMEnvironment.Closure) : IO OCMEnvironment.Packet := do
  let handle ← IO.FS.Handle.mk path .write
  IO.withStdout (.ofHandle handle) <| M.run env do
    initState env
    dumpMetadata
    for n in closure.names.qsort Name.lt do dumpConstant n
  handle.flush
  let restored ← OCMEnvironment.readPacket path
  verifySource env closure.names restored.state.constMap
  return restored

def capture (env : Environment) (r : Request) (source : String) (out : System.FilePath)
    (setStage : String → IO Unit) : IO Json := do
  let matched ← IO.ofExcept <| select env r source
  setStage "export"
  let thm := matched.declaration
  let c := constants env
  let closure ← IO.ofExcept <| OCMEnvironment.dependencyClosure c #[thm.name] {}
  let targetType ← M.run env <| removeMData thm.type
  let reference ← M.run env <| removeMData thm.value
  -- Independent expression packets precede reading the subsequently exported source packet.
  let goal ← OCMEnvironment.writeExpression (out / "goal.ndjson") env thm.name thm.levelParams targetType
  let proof ← OCMEnvironment.writeExpression (out / "reference.ndjson") env thm.name thm.levelParams reference
  let restored ← writeSource (out / "source.ndjson") env closure
  let some (.thmInfo copy) := restored.state.constMap[thm.name]? | throw <| IO.userError "SOURCE_TARGET_MISSING"
  if copy.type != targetType || copy.value != reference || copy.levelParams != thm.levelParams then
    throw <| IO.userError "SOURCE_REFERENCE_TRANSPORT_MISMATCH"
  let dependencies := (OCMEnvironment.exprDependencies reference).toArray.qsort Name.lt
  let members := closure.names.qsort Name.lt |>.map fun n =>
    let ci := restored.state.constMap[n]!
    Json.mkObj [("name",toJson n.toString),("kind",toJson (kind ci)),
      ("module",toJson ((origin? env n).map Name.toString)),
      ("level_params",toJson (ci.levelParams.map Name.toString))]
  let axioms := closure.names.filter (fun n => match c[n]? with | some (.axiomInfo _) => true | _ => false)
  return Json.mkObj [("schema","ocm.coverage.association.v1"),("resolved_name",toJson thm.name.toString),
    ("origin",toJson matched.origin.toString),("range",spanJson (ofRange matched.ranges.range)),
    ("selection_range",spanJson (ofRange matched.ranges.selectionRange)),
    ("source_path",toJson r.sourcePath.toString),("source_bytes",toJson source.utf8ByteSize),
    ("level_params",toJson (thm.levelParams.map Name.toString)),("goal",goal),("reference",proof),
    ("reference_dependencies",namesJson dependencies),("source_membership",toJson members),
    ("source_edges",toJson (closure.edges.map (fun (a,b) => #[a.toString,b.toString]))),
    ("axioms",namesJson (axioms.qsort Name.lt)),("normalization",toJson OCMEnvironment.normalizationVersion),
    ("imported_modules",namesJson env.allImportedModuleNames),("load_extensions",false),
    ("import_level","private"),("kernel_check","NOT_RUN"),("scope","EXPOSED_REFERENCE_COVERAGE_ONLY")]
end OCMCoverage
