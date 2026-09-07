import OCMEnvironment.Config
import Lean.DeclarationRange
namespace OCMCoverage
open Lean
structure Span where
  start : Position
  stop : Position
  deriving Inhabited, BEq
structure Request where
  moduleName : Name
  sourcePath : System.FilePath
  range : Span
  selection : Span

def position (j : Json) : Except String Position := do
  OCMEnvironment.keys j ["line","column"]
  let line ← OCMEnvironment.natural (← OCMEnvironment.field j "line")
  let column ← OCMEnvironment.natural (← OCMEnvironment.field j "column")
  if line == 0 || line > 4294967295 || column > 4294967295 then throw "POSITION_BOUND"
  return {line, column}
def span (j : Json) : Except String Span := do
  OCMEnvironment.keys j ["start","end"]
  let start ← position (← OCMEnvironment.field j "start")
  let stop ← position (← OCMEnvironment.field j "end")
  if !Position.lt start stop then throw "EMPTY_OR_REVERSED_RANGE"
  return {start, stop}
def parseRequest (j : Json) : Except String Request := do
  OCMEnvironment.keys j ["schema","operation","module","source_path","range","selection_range"]
  if (← j.getObjValAs? String "schema") != "ocm.coverage.capture.v1" then throw "REQUEST_SCHEMA"
  if (← j.getObjValAs? String "operation") != "capture" then throw "OPERATION"
  let parts ← j.getObjValAs? (Array String) "module"
  if parts.isEmpty || parts.any (fun s => s.isEmpty || s.contains '.' || s.contains '/' || s.contains '\\' || s.contains '\u0000') then
    throw "MODULE_COMPONENTS"
  let moduleName := parts.foldl Name.str .anonymous
  let range ← span (← OCMEnvironment.field j "range")
  let selection ← span (← OCMEnvironment.field j "selection_range")
  if Position.lt selection.start range.start || Position.lt range.stop selection.stop then throw "SELECTION_OUTSIDE_RANGE"
  return {moduleName, sourcePath := ← j.getObjValAs? String "source_path", range, selection}
def spanJson (s : Span) : Json := Json.mkObj [("start",toJson s.start),("end",toJson s.stop)]
def ofRange (r : DeclarationRange) : Span := {start := r.pos, stop := r.endPos}
def namesJson (ns : Array Name) : Json := toJson (ns.map Name.toString)
end OCMCoverage
