import Lean
namespace RefAlpha
universe u
theorem same_name {α : Sort u} (x : α) : x = x := rfl
end RefAlpha
namespace RenamedScope
universe v
theorem renamed {β : Sort v} (y : β) : y = y := rfl
end RenamedScope
namespace Other
 theorem same_name (p : Prop) (h : p) : p := h
end Other
namespace UnicodeScope
 theorem lemma₂ {α : Type} (x : α) : x = x := rfl
end UnicodeScope

namespace Attributed
/-- Registered documentation is a modifier, not a target selector. -/
@[simp] theorem decorated (p : Prop) : (True ∧ p) ↔ p := ⟨fun h => h.2, fun h => ⟨True.intro, h⟩⟩
end Attributed
namespace PrivateScope
private theorem hidden (p : Prop) (h : p) : p := h
end PrivateScope
namespace Ambiguous
theorem first (p : Prop) (h : p) : p := h
theorem second (p : Prop) (h : p) : p := h
run_cmd do
  let some r ← Lean.findDeclarationRangesCore? `Ambiguous.first | throwError "missing fixture range"
  Lean.addDeclarationRanges `Ambiguous.second r
end Ambiguous
initialize do
  if let some path ← IO.getEnv "OCM_COVERAGE_INITIALIZER_SENTINEL" then
    IO.FS.writeFile path "SOURCE_INITIALIZER_RAN"

namespace Swapped
theorem original_target (p : Prop) (h : p) : p := h
theorem different_target : True := True.intro
run_cmd do
  let some a ← Lean.findDeclarationRangesCore? `Swapped.original_target | throwError "range a"
  let some b ← Lean.findDeclarationRangesCore? `Swapped.different_target | throwError "range b"
  Lean.addDeclarationRanges `Swapped.original_target b
  Lean.addDeclarationRanges `Swapped.different_target a
end Swapped

namespace UniverseOrder
universe u v
theorem universes {α : Sort u} {β : Sort v} (a : α) (_b : β) : a = a := rfl
end UniverseOrder
namespace UnregisteredSupport
axiom premise : False
theorem dependent : False := premise
end UnregisteredSupport
