import OCMCoverage.Types
namespace OCMCoverage
open Lean
structure Match where
  declaration : TheoremVal
  ranges : DeclarationRanges
  origin : Name

def origin? (env : Environment) (name : Name) : Option Name := do
  let i ← env.getModuleIdxFor? name
  env.allImportedModuleNames[i]?
def ranges? (env : Environment) (name : Name) : Option DeclarationRanges :=
  declRangeExt.find? env name (level := .exported) <|>
  declRangeExt.find? env name (level := .server)
def sourceSlice (source : String) (s : Span) : Except String String := do
  let fm := source.toFileMap
  let a := fm.ofPosition s.start; let b := fm.ofPosition s.stop
  if fm.toPosition a != s.start || fm.toPosition b != s.stop then throw "SOURCE_POSITION_MISMATCH"
  return source.extract (source.pos! a) (source.pos! b)

def rangeMatches (env : Environment) (source : String) (actual requested : Span) : Except String Bool := do
  if actual.stop != requested.stop || Position.lt requested.start actual.start then return false
  if actual.start == requested.start then return true
  let leading ← sourceSlice source {start := actual.start, stop := requested.start}
  let parsed ← Parser.runParserCategory env `command (leading ++ "theorem ocm_range_probe : True := True.intro")
  if parsed.getKind != `Lean.Parser.Command.declaration then throw "UNSUPPORTED_MODIFIER_PREFIX"
  return true

def select (env : Environment) (request : Request) (source : String) : Except String Match := do
  let _ ← sourceSlice source request.range
  let selection ← sourceSlice source request.selection
  if selection.isEmpty then throw "EMPTY_SOURCE_SELECTION"
  let mut found : Array Match := #[]
  for (name, ci) in env.constants do
    if origin? env name != some request.moduleName then continue
    let some ranges := ranges? env name | continue
    if ofRange ranges.selectionRange != request.selection then continue
    if !(← rangeMatches env source (ofRange ranges.range) request.range) then continue
    let .thmInfo declaration := ci | throw "ASSOCIATED_DECLARATION_NOT_THEOREM"
    found := found.push {declaration, ranges, origin := request.moduleName}
  if found.isEmpty then throw "NO_EXACT_ASSOCIATION"
  if found.size != 1 then throw "AMBIGUOUS_ASSOCIATION"
  let some answer := found[0]? | throw "NO_EXACT_ASSOCIATION"
  let some sourceName := Syntax.decodeNameLit ("`" ++ selection) | throw "SOURCE_HEADER_NAME_LAYOUT"
  if sourceName.isAnonymous || !sourceName.isSuffixOf (privateToUserName answer.declaration.name).eraseMacroScopes then
    throw "SOURCE_HEADER_NAME_MISMATCH"
  return answer
end OCMCoverage
