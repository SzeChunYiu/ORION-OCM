-- Development-only extraction of exposed authored proofs; never a proposer.
import OCMEnvironment.Config
import OCMEnvironment.Write
open Lean OCMEnvironment
def main (args : List String) : IO UInt32 := do
  let [sourcePath, targetName, outPath] := args | return 2
  let out := System.FilePath.mk outPath
  if ← out.pathExists then return 2
  IO.FS.createDir out
  let packet ← readPacket sourcePath
  let name ← IO.ofExcept <| lookupName packet.state.constMap targetName
  let some (.thmInfo target) := packet.state.constMap[name]? | throw <| IO.userError "THEOREM_REQUIRED"
  let env ← mkEmptyEnvironment 0
  let goal ← writeExpression (out / "goal.ndjson") env name target.levelParams target.type
  let proof ← writeExpression (out / "candidate.ndjson") env .anonymous target.levelParams target.value
  writeJson (out / "goal.json") goal
  writeJson (out / "candidate.json") proof
  -- Registered stress control: known identity applications, not proof discovery.
  let mut stress := target.value
  for _ in [:2000] do stress := .app (.lam `h target.type (.bvar 0) .default) stress
  let stressData ← writeExpression (out / "stress.ndjson") env .anonymous target.levelParams stress
  writeJson (out / "stress.json") stressData
  IO.println "EXPOSED_FIXTURE_EXTRACTED"
  return 0
