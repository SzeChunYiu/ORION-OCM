import OCMCoverage.Packets
open Lean OCMCoverage

def rejected (label : String) (action : IO Unit) : IO Unit := do
  let result ← try action; pure false catch _ => pure true
  unless result do throw <| IO.userError s!"EXPECTED_TRANSPORT_REFUSAL {label}"
  IO.println s!"PASS {label}"

def main (args : List String) : IO UInt32 := do
  let [packetPath, requestPath] := args | throw <| IO.userError "usage: transport_tests SOURCE_PACKET REQUEST"
  let some sysroot ← IO.getEnv "LEAN_SYSROOT" | throw <| IO.userError "LEAN_SYSROOT_REQUIRED"
  initSearchPath sysroot
  let env ← importModules #[{module := `Theorems.Thm_authored}] {} (loadExts := false) (level := .private)
  let packet ← OCMEnvironment.readPacket packetPath
  let map := packet.state.constMap
  let names := map.toList.toArray.map (·.1)
  verifySource env names map
  IO.println "PASS exact-original-support"
  let support := `P2MW.S_authored.solution
  let some (.thmInfo ci) := map[support]? | throw <| IO.userError "FIXTURE_SUPPORT_MISSING"
  let normalized ← M.run env <| normalizeInfo (.thmInfo {ci with value := .mdata {} ci.value})
  unless OCMEnvironment.exactInfo normalized (.thmInfo ci) do
    throw <| IO.userError "PARENT_METADATA_NORMALIZATION"
  IO.println "PASS parent-metadata-normalization"
  let altered := #[
    ("body", ConstantInfo.thmInfo {ci with value := mkSort .zero}),
    ("type", ConstantInfo.thmInfo {ci with type := mkSort .zero}),
    ("universe", ConstantInfo.thmInfo {ci with levelParams := [`changed]}),
    ("family-membership", ConstantInfo.thmInfo {ci with all := [`changed]})]
  for (label, bad) in altered do
    rejected label <| verifySource env names (map.insert support bad)
  rejected "missing-support" <| verifySource env names (map.erase support)
  rejected "extra-support" <| verifySource env names (map.insert `unknown (.thmInfo {ci with name := `unknown}))
  let request ← IO.ofExcept <| parseRequest (← OCMEnvironment.readJson requestPath)
  let source ← IO.FS.readFile request.sourcePath
  let stage ← IO.mkRef "association"
  rejected "export-io-failure" <| do
    discard <| capture env request source (System.FilePath.mk packetPath / "not-a-directory") stage.set
  unless (← stage.get) == "export" do throw <| IO.userError "EXPORT_STAGE_NOT_REACHED"
  IO.println "PASS first-failing-export-stage"
  IO.println "TRANSPORT_CONTROLS_PASS 10"
  return 0
