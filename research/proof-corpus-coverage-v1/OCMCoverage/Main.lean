import OCMCoverage.Packets
namespace OCMCoverage
open Lean

def result (terminal stage reason : String) (files : Array String) : Json :=
  Json.mkObj [("schema","ocm.coverage.result.v1"),("operation","capture"),
    ("terminal",toJson terminal),("stage",toJson stage),("reason",toJson reason),("files",toJson files),
    ("kernel_check","NOT_RUN"),("scope","EXPOSED_REFERENCE_COVERAGE_ONLY")]
def main (args : List String) : IO UInt32 := do
  let [requestPath, outputPath] := args | IO.eprintln "usage: ocm_coverage REQUEST_JSON NEW_OUTPUT_DIR"; return 2
  let out : System.FilePath := outputPath
  try IO.FS.createDir out catch e => IO.eprintln e.toString; return 2
  let stageRef ← IO.mkRef "request"
  let mut terminal := "CANNOT_CHECK"; let mut reason := ""
  try
    let r ← IO.ofExcept <| parseRequest (← OCMEnvironment.readJson requestPath)
    let bytes ← IO.FS.readBinFile r.sourcePath
    let some source := String.fromUTF8? bytes | throw <| IO.userError "SOURCE_UTF8"
    stageRef.set "import"
    let some sysroot ← IO.getEnv "LEAN_SYSROOT" | throw <| IO.userError "LEAN_SYSROOT_REQUIRED"
    let some _ ← IO.getEnv "LEAN_PATH" | throw <| IO.userError "LEAN_PATH_REQUIRED"
    initSearchPath sysroot
    let env ← importModules #[{module := r.moduleName}] {} (loadExts := false) (level := .private)
    stageRef.set "association"
    let association ← capture env r source out stageRef.set
    OCMEnvironment.writeJson (out / "association.json") association
    terminal := "REFERENCE_CAPTURED"; stageRef.set "capture"; reason := "EXPOSED_REFERENCE_CAPTURE_NO_KERNEL_CHECK"
  catch e => reason := e.toString
  let entries ← out.readDir
  let files := (entries.map (·.fileName)).push "result.json" |>.qsort (· < ·)
  let payload := result terminal (← stageRef.get) reason files
  OCMEnvironment.writeJson (out / "result.json") payload
  IO.println payload.compress
  return 0
end OCMCoverage

def main := OCMCoverage.main
