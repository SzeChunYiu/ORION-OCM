import OCMEnvironment.Dependencies
open Lean OCMEnvironment
private def require (b : Bool) (msg : String) : IO Unit :=
  unless b do throw (IO.userError msg)
def main : IO Unit := do
  require ((exprDependencies (.proj `Box 0 (.bvar 0))).contains `Box) "projection type missing"
  require ((exprDependencies (.lit (.strVal "x"))).contains `String.ofList) "string primitive missing"
  require ((exprDependencies (.lit (.natVal 3))).contains `Nat) "Nat primitive missing"
  let a : ConstantInfo := .axiomInfo {name := `A, levelParams := [], type := .sort .zero, isUnsafe := false}
  let o : ConstantInfo := .opaqueInfo {name := `O, levelParams := [], type := .sort .zero, value := .const `A [], isUnsafe := false}
  require ((constantDependencies o).contains `A) "opaque body missing"
  let constants : OCMEnvironment.ConstMap := ({} : OCMEnvironment.ConstMap) |>.insert `A a |>.insert `O o
  require (dependencyClosure constants #[`O] {}).isOk "valid closure refused"
  require (dependencyClosure constants #[`O] (({} : NameHashSet).insert `A)).isOk.not "excluded opaque body accepted"
  require (dependencyClosure (constants.erase `A) #[`O] {}).isOk.not "missing body dependency accepted"
  let grouped : ConstantInfo := .opaqueInfo {name := `O, levelParams := [], type := .sort .zero, value := .const `A [], isUnsafe := false, all := [`O, `B]}
  require ((constantDependencies grouped).contains `B) "declared mutual metadata dependency missing"
  IO.println "DEPENDENCY_CONTROLS_PASS 8"
