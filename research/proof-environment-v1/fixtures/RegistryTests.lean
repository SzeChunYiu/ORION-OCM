import OCMEnvironment.Registry
open Lean OCMEnvironment
def main : IO Unit := do
  let ax : ConstantInfo := .axiomInfo {name := `A, levelParams := [], type := mkSort .zero, isUnsafe := false}
  let m := ({} : OCMEnvironment.ConstMap).insert `A ax
  unless (requireAxiomRegistry m m #[`A]).isOk do throw <| IO.userError "correct registry refused"
  if (requireAxiomRegistry m {} #[`A]).isOk then throw <| IO.userError "missing header accepted"
  let nat : ConstantInfo := .axiomInfo {name := `Nat, levelParams := [], type := mkSort (.succ .zero), isUnsafe := false}
  let n := ({} : OCMEnvironment.ConstMap).insert `Nat nat
  if (requireKnownPrimitives n {}).isOk then throw <| IO.userError "missing primitive accepted"
  unless (requireKnownPrimitives n n).isOk do throw <| IO.userError "registered primitive refused"
  unless (requireKnownPrimitives {} {}).isOk do throw <| IO.userError "unreached registry demanded"
  IO.println "5 registry controls PASS"
