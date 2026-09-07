import OCMEnvironment.Prepare
namespace OCMEnvironment
open Lean
def checkProof (prepared : Prepared) (candidate : Expr) : IO Json := do
  if candidate.hasFVar || candidate.hasMVar || candidate.hasLooseBVars then
    throw <| IO.userError "OPEN_CANDIDATE"
  let policy := prepared.policy
  let roots := (exprDependencies candidate).toArray ++ (exprDependencies policy.target.type).toArray
  let consumed ← IO.ofExcept <| dependencyClosure prepared.constants roots policy.excluded
  let axioms ← IO.ofExcept <| axiomNames prepared.constants consumed.names policy.axioms
  let freshName := `OCMEnvironment_checked_candidate
  if prepared.constants.contains freshName then throw <| IO.userError "CHECKER_NAME_COLLISION"
  let decl := Declaration.thmDecl {name := freshName, levelParams := policy.target.levelParams, type := policy.target.type, value := candidate, all := [freshName]}
  let checked := prepared.env.toKernelEnv.addDeclCore policy.maxHeartbeats.toUSize policy.maxRecDepth.toUSize decl none
  match checked with
  | .error ex =>
    let (terminal, stage, reason) ← match ex with
      | .deterministicTimeout => pure ("CANNOT_CHECK", "kernel_resource", "DETERMINISTIC_TIMEOUT")
      | .excessiveMemory => pure ("CANNOT_CHECK", "kernel_resource", "EXCESSIVE_MEMORY")
      | .deepRecursion => pure ("CANNOT_CHECK", "kernel_resource", "DEEP_RECURSION")
      | .interrupted => pure ("CANNOT_CHECK", "kernel_resource", "INTERRUPTED")
      | .other message => pure ("CANNOT_CHECK", "kernel_unclassified", message)
      | _ => pure ("REJECTED", "kernel", ← ex.toMessageData {} |>.toString)
    return result "check" terminal stage reason
      (Json.mkObj [("declarations_replayed", toJson prepared.constants.size)]) consumed.names axioms
  | .ok env =>
    let some (.thmInfo actual) := env.find? freshName | throw <| IO.userError "MISSING_CHECKED_THEOREM"
    if !actual.type.equal policy.target.type || actual.levelParams != policy.target.levelParams || !actual.value.equal candidate then
      throw <| IO.userError "CHECKED_THEOREM_IDENTITY"
    let auditedMap := env.constants.fold (fun m n ci => m.insert n ci) ({} : ConstMap)
    let audited ← IO.ofExcept <| dependencyClosure auditedMap #[freshName] policy.excluded
    let actualAxioms ← IO.ofExcept <| axiomNames auditedMap audited.names policy.axioms
    if actualAxioms != axioms then throw <| IO.userError "POST_KERNEL_AXIOM_MISMATCH"
    return result "check" "KERNEL_PASS" "kernel_and_axioms" ""
      (Json.mkObj [("declarations_replayed", toJson prepared.constants.size), ("candidate_constants_touched", toJson consumed.names.size)]) consumed.names axioms
end OCMEnvironment
