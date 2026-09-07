import OCMEnvironment.Config
import OCMEnvironment.Write
import OCMEnvironment.Check
import OCMEnvironment.Registry
import OCMEnvironment.Outcomes
namespace OCMEnvironment
open Lean
private def pathField (j : Json) (k : String) : IO System.FilePath := return ⟨← getString j k⟩
private def operation (request : Json) (out : System.FilePath) (phase : IO.Ref String) : IO Json := do
  if (← getString request "schema") != "ocm.proof-environment.request.v1" then throw <| IO.userError "REQUEST_SCHEMA"
  let op ← getString request "operation"
  if op == "inspect" then
    IO.ofExcept <| keys request ["schema", "operation", "source_packet"]
    phase.set "source_packet"
    let source ← readPacket (← pathField request "source_packet")
    let names := source.state.constOrder
    return result op "INSPECTED" "parsed_inventory" "NO_KERNEL_CHECK"
      (Json.mkObj [("declarations", toJson names.size), ("expressions", toJson source.state.exprMap.size), ("rows", toJson source.rows)]) names
  if op == "prepare" then
    IO.ofExcept <| keys request ["schema", "operation", "source_packet", "policy", "primitive_packet", "registered_target_packet"]
    phase.set "source_packet"
    let source ← readPacket (← pathField request "source_packet")
    phase.set "primitive_packet"
    let primitive ← readPacket (← pathField request "primitive_packet")
    phase.set "registered_target"
    let independent ← readPacket (← pathField request "registered_target_packet") true
    phase.set "primitive_identity"
    let combined ← IO.ofExcept <| mergePrimitives source.state.constMap primitive.state.constMap
    phase.set "independent_target_and_policy"
    let policy ← preparationPolicy (← readJson (← pathField request "policy")) independent combined
    phase.set "axiom_registry"
    IO.ofExcept <| requireAxiomRegistry combined primitive.state.constMap policy.axioms
    phase.set "closure_and_replay"
    let prepared ← prepareMap combined policy
    phase.set "primitive_coverage"
    IO.ofExcept <| requireKnownPrimitives prepared.constants primitive.state.constMap
    phase.set "serialization"
    writeEnvironment (out / "permitted.ndjson") prepared.env prepared.closure.names
    let target ← writeExpression (out / "target.ndjson") prepared.env policy.target.name policy.target.levelParams policy.target.type
    writeJson (out / "registration.json") (registration prepared target)
    writeJson (out / "inventory.json") (inventory prepared)
    return result op "PREPARED" "replay_and_independent_target" ""
      (Json.mkObj [("source_declarations", toJson source.state.constMap.size), ("declarations_replayed", toJson prepared.constants.size), ("dependency_edges", toJson prepared.closure.edges.size)])
      prepared.closure.names prepared.policy.axioms #["permitted.ndjson", "target.ndjson", "registration.json", "inventory.json", "result.json"]
  if op == "check" then
    IO.ofExcept <| keys request ["schema", "operation", "permitted_packet", "target_packet", "registration", "primitive_packet", "candidate_packet", "candidate_root"]
    phase.set "permitted_packet"
    let permitted ← readPacket (← pathField request "permitted_packet")
    phase.set "registered_target"
    let goal ← readPacket (← pathField request "target_packet") true
    phase.set "primitive_packet"
    let primitive ← readPacket (← pathField request "primitive_packet")
    phase.set "primitive_identity"
    discard <| IO.ofExcept <| mergePrimitives permitted.state.constMap primitive.state.constMap
    phase.set "registration"
    let policy ← restorePolicy (← readJson (← pathField request "registration")) goal permitted.state.constMap
    phase.set "axiom_registry"
    IO.ofExcept <| requireAxiomRegistry permitted.state.constMap primitive.state.constMap policy.axioms
    phase.set "closure_and_replay"
    let prepared ← prepareMap permitted.state.constMap policy
    phase.set "primitive_coverage"
    IO.ofExcept <| requireKnownPrimitives prepared.constants primitive.state.constMap
    phase.set "candidate_packet"
    let packet ← readPacket (← pathField request "candidate_packet") true
    let candidate ← packetExpr packet (← getNat request "candidate_root")
    phase.set "candidate_dependencies_and_kernel"
    return ← checkProof prepared candidate
  throw <| IO.userError "UNKNOWN_OPERATION"
end OCMEnvironment
open OCMEnvironment in
def main (args : List String) : IO UInt32 := do
  let [requestPath, outPath] := args | do IO.eprintln "usage: ocm_environment REQUEST.json OUTDIR"; return 2
  let out := System.FilePath.mk outPath
  if ← out.pathExists then IO.eprintln "OUTPUT_EXISTS"; return 2
  IO.FS.createDir out
  let op ← IO.mkRef "unknown"
  let phase ← IO.mkRef "request"
  let response ← try
    let request ← readJson requestPath
    op.set (← getString request "operation")
    operation request out phase
  catch ex => do
    let files := ((← out.readDir).map (·.fileName)).qsort (· < ·)
    pure <| result (← op.get) (refusalTerminal ex.toString) (← phase.get) ex.toString (Lean.Json.mkObj []) #[] #[] (files.push "result.json")
  writeJson (out / "result.json") response
  IO.println response.compress
  return 0
