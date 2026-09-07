import OCMEnvironment.PacketSchema
import Export
namespace OCMEnvironment
open Lean
def metadata : Json := exportMetadata
structure Packet where
  state : Export.Parse.State
  rows : Nat
private def checkMeta (j : Json) : Validation Unit := do
  if j != metadata then throw "METADATA_MISMATCH"
def validateText (text : String) (candidateOnly : Bool) : Validation Unit := do
  let lines := text.splitOn "\n"
  let head :: tail := lines | throw "EMPTY_PACKET"
  let header ← Json.parse head
  if header.compress != head then throw "NONCANONICAL_JSON"
  checkMeta header
  if !text.endsWith "\n" then throw "FINAL_NEWLINE_REQUIRED"
  let mut names := 1; let mut levels := 1; let mut exprs := 0
  for line in tail.dropLast do
    let j ← Json.parse line
    if j.compress != line then throw "NONCANONICAL_JSON"
    itemSchema j
    references j names levels exprs
    let .obj o := j | throw "OBJECT_REQUIRED"
    if let some id := o["in"]? then
      if (← natural id) != names then throw "NAME_INDEX_IDENTITY"
      names := names + 1
    else if let some id := o["il"]? then
      if (← natural id) != levels then throw "LEVEL_INDEX_IDENTITY"
      levels := levels + 1
    else if let some id := o["ie"]? then
      if (← natural id) != exprs then throw "EXPR_INDEX_IDENTITY"
      exprs := exprs + 1
    else if candidateOnly then throw "CANDIDATE_DECLARATION"
def readPacket (path : System.FilePath) (candidateOnly := false) : IO Packet := do
  let text ← IO.FS.readFile path
  IO.ofExcept <| validateText text candidateOnly
  let handle ← IO.FS.Handle.mk path .read
  let (_, state) ← Export.Parse.M.run Export.Parse.parseFile (.ofHandle handle)
  if candidateOnly && (!state.constMap.isEmpty || !state.constOrder.isEmpty) then
    throw <| IO.userError "CANDIDATE_DECLARATION"
  return {state, rows := (text.splitOn "\n").length - 1}
end OCMEnvironment
