import OCMEnvironment.Dependencies
namespace OCMEnvironment
open Lean
private def unique (xs : List Name) : Bool := xs.length == (xs.toArray.foldl (fun s n => s.insert n) ({} : NameHashSet)).size
def validateFamilies (constants : ConstMap) : Except String Unit := do
  for (n, ci) in constants.toList do
    if n != ci.name then throw s!"NAME_RECORD_MISMATCH {n}"
    if ci.isUnsafe || ci.isPartial then throw s!"UNSAFE_OR_PARTIAL {n}"
    if !unique ci.levelParams || ci.levelParams.contains .anonymous then throw s!"UNIVERSE_PARAMETERS {n}"
    if ci.type.hasFVar || ci.type.hasMVar || ci.type.hasLooseBVars then throw s!"OPEN_DECLARATION_TYPE {n}"
    if let some value := ci.value? true then
      if value.hasFVar || value.hasMVar || value.hasLooseBVars then throw s!"OPEN_DECLARATION_VALUE {n}"
    match ci with
    | .inductInfo v =>
      if !unique v.all || !unique v.ctors || !v.all.contains n then throw s!"INDUCTIVE_MEMBERSHIP {n}"
      for member in v.all do
        let some (.inductInfo other) := constants[member]? | throw s!"MISSING_INDUCTIVE_MEMBER {n} {member}"
        if other.all != v.all || other.levelParams != v.levelParams || other.numParams != v.numParams then
          throw s!"INCONSISTENT_INDUCTIVE_FAMILY {n} {member}"
      for i in [:v.ctors.length] do
        let ctor := v.ctors[i]!
        let some (.ctorInfo c) := constants[ctor]? | throw s!"MISSING_CONSTRUCTOR {n} {ctor}"
        if c.induct != n || c.cidx != i || c.numParams != v.numParams then throw s!"CONSTRUCTOR_MEMBERSHIP {ctor}"
      let primary := n ++ `rec
      let some (.recInfo _) := constants[primary]? | throw s!"MISSING_PRIMARY_RECURSOR {n}"
    | .ctorInfo v =>
      let some (.inductInfo parent) := constants[v.induct]? | throw s!"MISSING_CONSTRUCTOR_PARENT {n}"
      if parent.ctors[v.cidx]? != some n then throw s!"EXTRA_CONSTRUCTOR {n}"
    | .recInfo v =>
      if v.all.isEmpty || !unique v.all then throw s!"RECURSOR_MEMBERSHIP {n}"
      for parent in v.all do
        let some (.inductInfo _) := constants[parent]? | throw s!"MISSING_RECURSOR_FAMILY {n} {parent}"
      for rule in v.rules do
        let some (.ctorInfo _) := constants[rule.ctor]? | throw s!"MISSING_RULE_CONSTRUCTOR {n} {rule.ctor}"
        if rule.rhs.hasFVar || rule.rhs.hasMVar || rule.rhs.hasLooseBVars then throw s!"OPEN_RECURSOR_RULE {n}"
    | .quotInfo _ =>
      for q in [`Quot, `Quot.mk, `Quot.lift, `Quot.ind] do
        let some (.quotInfo _) := constants[q]? | throw s!"INCOMPLETE_QUOTIENT {q}"
    | _ => pure ()
end OCMEnvironment
