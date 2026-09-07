import OCMEnvironment.Prepare
namespace OCMEnvironment
open Lean
-- Parent Comparator.Main.primitiveTargets plus explicitly represented kernel families/literals.
-- Only reached records need coverage; complete record identity uses the declared parent normalization.
def knownPrimitives : Array Name := #[`Nat, `Nat.zero, `Nat.succ, `Nat.add, `Nat.sub,
  `Nat.mul, `Nat.pow, `Nat.gcd, `Nat.div, `Nat.mod, `Nat.beq, `Nat.ble, `Nat.land,
  `Nat.lor, `Nat.xor, `Nat.shiftLeft, `Nat.shiftRight, `String, `String.ofList,
  `Char, `Char.ofNat, `List, `eagerReduce, `Eq, `Quot, `Quot.mk, `Quot.lift, `Quot.ind]
def requireKnownPrimitives (constants registry : ConstMap) : Except String Unit := do
  for name in knownPrimitives do
    if let some actual := constants[name]? then
      let some expected := registry[name]? | throw s!"MISSING_REGISTERED_PRIMITIVE {name}"
      if !exactInfo expected actual then throw s!"REGISTERED_PRIMITIVE_MISMATCH {name}"
end OCMEnvironment
