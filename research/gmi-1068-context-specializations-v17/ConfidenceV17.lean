import SpecializationsV17
namespace ConfidenceV17
open PartialContextV15 SpecializationsV17
universe u v
def Region (X : Type v) := {A : X → Prop // ∃ x, A x}
def precision {X : Type v} : PreorderSpec (Region X) where
  le a b := ∀ x, b.val x → a.val x
  refl _ _ h := h
  trans h k x hx := h x (k x hx)

theorem precision_iff {X : Type v} (a b : Region X) :
    precision.le a b ↔ ∀ x, b.val x → a.val x := Iff.rfl
theorem precision_antisymm {X : Type v} {a b : Region X}
    (hab : precision.le a b) (hba : precision.le b a) : a=b := by
  apply Subtype.ext
  funext x
  exact propext ⟨hba x,hab x⟩

def confidence {H : Type u} {X : Type v} (E : H → Prop)
    (f : {h // E h} → Region X) : Context H (Region X) := utility E precision f
theorem confidence_defined {H : Type u} {X : Type v} (E : H → Prop)
    (f : {h // E h} → Region X) : (confidence E f).defined = E := rfl
theorem confidence_value {H : Type u} {X : Type v} (E : H → Prop)
    (f : {h // E h} → Region X) (h : {h // E h}) : (confidence E f).eval h = f h := rfl
theorem confidence_nonempty {H : Type u} {X : Type v} (E : H → Prop)
    (f : {h // E h} → Region X) (h : {h // E h}) :
    ∃ x, ((confidence E f).eval h).val x := (f h).property
theorem confidence_comparison {H : Type u} {X : Type v} (P E : H → Prop)
    (f : {h // E h} → Region X) (a b : Active P (confidence E f)) :
    (activeOrder P (confidence E f)).le a b ↔ ∀ x,
      (f ⟨b.val,b.property.2⟩).val x → (f ⟨a.val,a.property.2⟩).val x := Iff.rfl
end ConfidenceV17
