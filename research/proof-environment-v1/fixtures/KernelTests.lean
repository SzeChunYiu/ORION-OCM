import OCMEnvironment.Prepare
import OCMEnvironment.Check
open Lean OCMEnvironment
private def require (b : Bool) (msg : String) : IO Unit :=
  unless b do throw (IO.userError msg)
def main : IO Unit := do
  let target : RegisteredTarget := {name := `original, levelParams := [], type := .forallE `p (.sort .zero) (.forallE `h (.bvar 0) (.bvar 1) .default) .default}
  let policy : Policy := {target, roots := #[], excluded := ({} : NameHashSet).insert `original, axioms := #[], maxHeartbeats := 1000000, maxRecDepth := 10000}
  let prepared ← prepareMap {} policy
  let proof := Expr.lam `p (.sort .zero) (.lam `h (.bvar 0) (.bvar 0) .default) .default
  let ok ← checkProof prepared proof
  require ((ok.getObjValAs? String "terminal").toOption == some "KERNEL_PASS") "identity proof failed"
  let bad ← checkProof prepared (.sort .zero)
  require ((bad.getObjValAs? String "terminal").toOption == some "REJECTED") "ill typed proof accepted"
  let mut refused := false
  try discard <| checkProof prepared (.const `original [])
  catch _ => refused := true
  require refused "target reference accepted"
  let ax : ConstantInfo := .axiomInfo {name := `A, levelParams := [], type := .sort .zero, isUnsafe := false}
  let pol := {policy with target := {target with type := .const `A []}, roots := #[`A]}
  let mut denied := false
  try discard <| prepareMap (({} : OCMEnvironment.ConstMap).insert `A ax) pol
  catch _ => denied := true
  require denied "unregistered axiom accepted"
  let mut complex := proof
  for _ in [:2000] do complex := .app (.lam `h target.type (.bvar 0) .default) complex
  let validComplex ← checkProof prepared complex
  require ((validComplex.getObjValAs? String "terminal").toOption == some "KERNEL_PASS") "resource control baseline is invalid"
  let limited ← checkProof {prepared with policy := {policy with maxHeartbeats := 1, maxRecDepth := 10}} complex
  IO.println limited.compress
  require ((limited.getObjValAs? String "terminal").toOption == some "CANNOT_CHECK") "resource exhaustion reported as invalid proof"
  require ((limited.getObjValAs? String "stage").toOption == some "kernel_resource") "resource stage missing"
  IO.println "KERNEL_CONTROLS_PASS 7"
