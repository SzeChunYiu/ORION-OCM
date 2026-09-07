import OCMEnvironment.Families
namespace OCMEnvironment
open Lean
def axiomNames (constants : ConstMap) (names : Array Name) (allowed : Array Name) : Except String (Array Name) := do
  let mut axioms := #[]
  for name in names do
    let some ci := constants[name]? | throw s!"MISSING_AXIOM_AUDIT_DEPENDENCY {name}"
    if let .axiomInfo _ := ci then
      if !allowed.contains name || [`sorryAx, `Lean.ofReduceBool, `Lean.trustCompiler].contains name then
        throw s!"UNREGISTERED_AXIOM {name}"
      axioms := axioms.push name
  return axioms.qsort Name.lt
def checkedMap (env : Environment) : ConstMap :=
  env.toKernelEnv.constants.fold (fun m n ci => m.insert n ci) {}
def replayMap (constants : ConstMap) : IO Environment := do
  IO.ofExcept <| validateFamilies constants
  let replayInput := constants.erase `Quot.mk |>.erase `Quot.lift |>.erase `Quot.ind
  let empty ← mkEmptyEnvironment 0
  let env ← empty.replay replayInput
  let actual := checkedMap env
  if actual.size != constants.size then throw <| IO.userError s!"GENERATED_MEMBERSHIP_SIZE {constants.size} {actual.size}"
  for (name, ci) in constants.toList do
    let some generated := actual[name]? | throw <| IO.userError s!"MISSING_GENERATED_DECLARATION {name}"
    if !exactInfo ci generated then throw <| IO.userError s!"GENERATED_DECLARATION_MISMATCH {name}"
  return env
def prepareMap (constants : ConstMap) (policy : Policy) : IO Prepared := do
  if !policy.excluded.contains policy.target.name then throw <| IO.userError "TARGET_NOT_EXCLUDED"
  if policy.target.type.hasMVar || policy.target.type.hasFVar || policy.target.type.hasLooseBVars then
    throw <| IO.userError "OPEN_REGISTERED_TARGET"
  let roots := policy.roots ++ (exprDependencies policy.target.type).toArray.qsort Name.lt
  let closure ← IO.ofExcept <| dependencyClosure constants roots policy.excluded
  let selected := closure.names.foldl (fun m n => m.insert n constants[n]!) ({} : ConstMap)
  let effectiveAxioms ← IO.ofExcept <| axiomNames selected closure.names policy.axioms
  let env ← replayMap selected
  match Kernel.check env {} policy.target.type with
  | .error ex => throw <| IO.userError s!"INVALID_TARGET {← ex.toMessageData {} |>.toString}"
  | .ok ty => if ty != mkSort .zero then throw <| IO.userError "TARGET_NOT_PROPOSITION"
  return {env, constants := selected, policy := {policy with axioms := effectiveAxioms}, closure}
def mergePrimitives (source primitives : ConstMap) : Except String ConstMap := do
  let mut combined := source
  for (n, ci) in primitives.toList do
    if let some supplied := source[n]? then
      if !exactInfo supplied ci then throw s!"PRIMITIVE_IDENTITY_MISMATCH {n}"
    else combined := combined.insert n ci
  return combined
def requireAxiomRegistry (constants registry : ConstMap) (allowed : Array Name) : Except String Unit := do
  for name in allowed do
    let some (.axiomInfo expected) := registry[name]? | throw s!"MISSING_REGISTERED_AXIOM_HEADER {name}"
    let some (.axiomInfo actual) := constants[name]? | throw s!"MISSING_SOURCE_AXIOM_HEADER {name}"
    if !exactInfo (.axiomInfo expected) (.axiomInfo actual) then throw s!"REGISTERED_AXIOM_HEADER_MISMATCH {name}"
end OCMEnvironment
