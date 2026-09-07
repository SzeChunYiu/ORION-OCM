import OCMEnvironment.Types
namespace OCMEnvironment
open Lean
def exprDependencies (expr : Expr) : NameHashSet := Id.run do
  let mut todo := #[expr]; let mut seen : Std.HashSet Expr := {}; let mut names : NameHashSet := {}
  while !todo.isEmpty do
    let e := todo.back!; todo := todo.pop
    if seen.contains e then continue
    seen := seen.insert e
    match e with
    | .const n _ => names := names.insert n
    | .app f a => todo := todo.push f |>.push a
    | .lam _ t b _ | .forallE _ t b _ => todo := todo.push t |>.push b
    | .letE _ t v b _ => todo := todo.push t |>.push v |>.push b
    | .mdata _ e => todo := todo.push e
    | .proj n _ e => names := names.insert n; todo := todo.push e
    | .lit (.natVal _) => names := names.insert `Nat
    | .lit (.strVal _) => names := names.insert `String |>.insert `Char.ofNat |>.insert `String.ofList
    | _ => pure ()
  return names
def constantDependencies (ci : ConstantInfo) : NameHashSet := Id.run do
  let mut names := exprDependencies ci.type
  if let some value := ci.value? true then names := names.insertMany (exprDependencies value).toArray
  match ci with
  | .defnInfo v => names := names.insertMany v.all
  | .thmInfo v => names := names.insertMany v.all
  | .opaqueInfo v => names := names.insertMany v.all
  | .inductInfo v => names := names.insertMany v.all |>.insertMany v.ctors
  | .ctorInfo v => names := names.insert v.induct
  | .recInfo v =>
    names := names.insertMany v.all
    for rule in v.rules do
      names := names.insert rule.ctor |>.insertMany (exprDependencies rule.rhs).toArray
  | .quotInfo _ => names := names.insertMany [`Eq, `Quot, `Quot.mk, `Quot.lift, `Quot.ind]
  | _ => pure ()
  return names
def dependencyClosure (constants : ConstMap) (roots : Array Name) (excluded : NameHashSet) : Except String Closure := do
  let mut recursors : Std.HashMap Name (Array Name) := {}
  for (n, ci) in constants.toList do
    if let .recInfo v := ci then
      for ind in v.all do recursors := recursors.insert ind ((recursors[ind]?.getD #[]).push n)
  let mut queue := roots.map (fun n => (n, [n])); let mut cursor := 0
  let mut seen : NameHashSet := {}; let mut result : Closure := {}
  while cursor < queue.size do
    let (n,path) := queue[cursor]!; cursor := cursor + 1
    if excluded.contains n then throw s!"EXCLUDED_DEPENDENCY {path.reverse.map Name.toString}"
    if seen.contains n then continue
    let some ci := constants[n]? | throw s!"MISSING_DEPENDENCY {path.reverse.map Name.toString}"
    if ci.isUnsafe || ci.isPartial then throw s!"UNSAFE_OR_PARTIAL {n}"
    seen := seen.insert n; result := {result with names := result.names.push n}
    let deps := match ci with
      | .inductInfo _ => (constantDependencies ci).insertMany (recursors[n]?.getD #[])
      | _ => constantDependencies ci
    for next in deps.toArray.qsort Name.lt do
      result := {result with edges := result.edges.push (n,next)}
      if !seen.contains next then queue := queue.push (next,next::path)
  return result
end OCMEnvironment
