import OCMEnvironment.Types
open Lean OCMEnvironment
private def require (b : Bool) (msg : String) : IO Unit := unless b do throw (IO.userError msg)
def main : IO Unit := do
  let ty := Expr.forallE `x (.sort (.succ .zero)) (.sort (.succ .zero)) .default
  let value := Expr.lam `x (.sort (.succ .zero)) (.bvar 0) .default
  let a : DefinitionVal := {name := `identity, levelParams := [], type := ty, value, hints := .abbrev, safety := .safe}
  let renamed := {a with type := .forallE `y (.sort (.succ .zero)) (.sort (.succ .zero)) .default, value := .lam `z (.sort (.succ .zero)) (.bvar 0) .default}
  require (exactInfo (.defnInfo a) (.defnInfo renamed)) "binder-name-only difference refused"
  for b in [{a with name := `other}, {a with levelParams := [`u]}, {a with type := .sort .zero},
            {a with value := .const `other []}, {a with safety := .unsafe}, {a with hints := .opaque}] do
    require (!(exactInfo (.defnInfo a) (.defnInfo b))) "semantic/retained annotation mutation accepted"
  require (exactInfo (.defnInfo a) (.defnInfo {a with type := .forallE `x (.sort (.succ .zero)) (.sort (.succ .zero)) .implicit})) "parent-normalized binder annotation refused"
  IO.println "NORMALIZATION_CONTROLS_PASS 8"
