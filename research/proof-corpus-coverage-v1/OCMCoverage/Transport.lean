import OCMEnvironment.Write
namespace OCMCoverage
open Lean

-- Only the pinned parent's expression normalization; every other record field is retained.
def normalizeInfo (ci : ConstantInfo) : M ConstantInfo := do
  let type ← removeMData ci.type
  match ci with
  | .axiomInfo v => return .axiomInfo {v with type}
  | .defnInfo v => return .defnInfo {v with type, value := ← removeMData v.value}
  | .thmInfo v => return .thmInfo {v with type, value := ← removeMData v.value}
  | .opaqueInfo v => return .opaqueInfo {v with type, value := ← removeMData v.value}
  | .quotInfo v => return .quotInfo {v with type}
  | .inductInfo v => return .inductInfo {v with type}
  | .ctorInfo v => return .ctorInfo {v with type}
  | .recInfo v =>
    let rules ← v.rules.mapM fun rule => do
      return {rule with rhs := ← removeMData rule.rhs}
    return .recInfo {v with type, rules}

def verifySource (env : Environment) (names : Array Name)
    (restored : OCMEnvironment.ConstMap) : IO Unit := do
  if restored.size != names.size then throw <| IO.userError "SOURCE_MEMBERSHIP_SIZE"
  for n in names do
    let some actual := restored[n]? | throw <| IO.userError s!"SOURCE_MEMBERSHIP_MISSING {n}"
    let some original := env.find? n | throw <| IO.userError s!"SOURCE_ORIGINAL_MISSING {n}"
    let expected ← M.run env <| normalizeInfo original
    unless OCMEnvironment.exactInfo expected actual do
      throw <| IO.userError s!"SOURCE_DECLARATION_TRANSPORT_MISMATCH {n}"
end OCMCoverage
