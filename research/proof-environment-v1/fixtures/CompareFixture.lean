import OCMEnvironment.Config
open Lean OCMEnvironment
def main (args : List String) : IO Unit := do
  let [aPath,bPath,n] := args | throw <| IO.userError "args"
  let a ← readPacket aPath; let b ← readPacket bPath
  let name ← IO.ofExcept <| lookupName a.state.constMap n
  let x := a.state.constMap[name]!; let y := b.state.constMap[name]!
  IO.println <| (Json.mkObj [("parent_info_equal", toJson (x == y)),
    ("type_alpha_equal", toJson (x.type == y.type)), ("type_exact", toJson (x.type.equal y.type)),
    ("value_alpha_equal", toJson (x.value? true == y.value? true)),
    ("x_type", toJson (reprStr x.type)), ("y_type", toJson (reprStr y.type)),
    ("x_value", toJson (reprStr (x.value? true))), ("y_value", toJson (reprStr (y.value? true)))]).compress
