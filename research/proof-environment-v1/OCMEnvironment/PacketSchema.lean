import Export.Parse
namespace OCMEnvironment
open Lean
abbrev Validation := Except String
def keys (j : Json) (expected : List String) : Validation Unit := do
  let .obj o := j | throw "OBJECT_REQUIRED"
  if o.toList.map Prod.fst != expected.mergeSort then throw s!"FIELDS {o.keys} expected {expected}"
def field (j : Json) (k : String) : Validation Json := j.getObjVal? k
def natural (j : Json) : Validation Nat := do
  let .num n := j | throw "NAT_REQUIRED"
  if n.exponent != 0 || n.mantissa < 0 then throw "EXACT_NAT_REQUIRED"
  return n.mantissa.toNat
def index (j : Json) (bound : Nat) : Validation Unit := do
  if (← natural j) >= bound then throw "REFERENCE_OUT_OF_RANGE"
private def baseFields := ["name", "levelParams", "type"]
def declarationSchema (tag : String) (j : Json) : Validation Unit := do
  let extra ← match tag with
    | "axiom" => pure ["isUnsafe"]
    | "def" => pure ["value", "hints", "safety", "all"]
    | "thm" => pure ["value", "all"]
    | "opaque" => pure ["value", "all", "isUnsafe"]
    | "quot" => pure ["kind"]
    | "typeInfo" => pure ["numParams", "numIndices", "all", "ctors", "numNested", "isRec", "isUnsafe", "isReflexive"]
    | "ctorInfo" => pure ["induct", "cidx", "numParams", "numFields", "isUnsafe"]
    | "recInfo" => pure ["all", "numParams", "numIndices", "numMotives", "numMinors", "rules", "k", "isUnsafe"]
    | _ => throw "DECLARATION_TAG"
  keys j (baseFields ++ extra)
  if tag == "def" then
    let hints ← field j "hints"
    if let .obj _ := hints then
      keys hints ["regular"]
      if (← natural (← field hints "regular")) > 4294967295 then throw "HINT_UINT32_OVERFLOW"
  if tag == "recInfo" then
    for x in (← (← field j "rules").getArr?) do keys x ["ctor", "nfields", "rhs"]
def itemSchema (j : Json) : Validation Unit := do
  let .obj o := j | throw "OBJECT_REQUIRED"
  if o.contains "in" then
    if o.contains "str" then
      keys j ["in", "str"]; keys (← field j "str") ["pre", "str"]
    else
      keys j ["in", "num"]; keys (← field j "num") ["pre", "i"]
  else if o.contains "il" then
    let tags := ["succ", "max", "imax", "param"].filter o.contains
    let [tag] := tags | throw "LEVEL_TAG"
    keys j ["il", tag]
  else if o.contains "ie" then
    let tags := ["bvar", "sort", "const", "app", "lam", "forallE", "letE", "proj", "natVal", "strVal", "mdata"].filter o.contains
    let [tag] := tags | throw "EXPR_TAG"
    keys j ["ie", tag]
    let v ← field j tag
    match tag with
    | "const" => keys v ["name", "us"]
    | "app" => keys v ["fn", "arg"]
    | "lam" | "forallE" => keys v ["name", "type", "body", "binderInfo"]
    | "letE" => keys v ["name", "type", "value", "body", "nondep"]
    | "proj" => keys v ["typeName", "idx", "struct"]
    | "mdata" => keys v ["expr", "data"]
    | _ => pure ()
  else
    let [(tag, v)] := o.toList | throw "DECLARATION_TAG"
    if tag == "inductive" then
      keys v ["types", "ctors", "recs"]
      for (k, t) in [("types", "typeInfo"), ("ctors", "ctorInfo"), ("recs", "recInfo")] do
        for x in (← (← field v k).getArr?) do declarationSchema t x
    else declarationSchema tag v
partial def references (j : Json) (names levels exprs : Nat) : Validation Unit := do
  match j with
  | .obj o =>
    for (k, v) in o.toList do
      if ["pre", "name", "typeName", "induct", "ctor", "param"].contains k then index v names
      else if ["type", "value", "fn", "arg", "body", "struct", "rhs", "expr"].contains k then index v exprs
      else if k == "sort" || k == "succ" then index v levels
      else if k == "max" || k == "imax" || k == "us" then
        for x in (← v.getArr?) do index x levels
      else if k == "levelParams" || k == "all" then
        for x in (← v.getArr?) do index x names
      else if k == "ctors" then
        for x in (← v.getArr?) do
          if let .obj _ := x then references x names levels exprs else index x names
      else if k != "data" then references v names levels exprs
  | .arr a => for x in a do references x names levels exprs
  | .num _ => discard <| natural j
  | _ => pure ()
end OCMEnvironment
