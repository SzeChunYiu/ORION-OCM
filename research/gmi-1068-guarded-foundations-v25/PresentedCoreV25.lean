import OptionFoldV25
import PartialUnitsV19
namespace PresentedCoreV25
open PartialUnitsV19
universe u
attribute [local instance] Classical.propDecidable
structure Presented (L : Type u) where
  carrier : L → Prop
  algebra : Algebra {x : L // carrier x}
noncomputable def lookup (p : Presented L) (x : L) : Option {x // p.carrier x} :=
  if h : p.carrier x then some ⟨x,h⟩ else none
noncomputable def padded (p : Presented L) (x y : L) : Option L :=
  if hx : p.carrier x then
    if hy : p.carrier y then
      (p.algebra.mul ⟨x,hx⟩ ⟨y,hy⟩).map Subtype.val
    else none
  else none
theorem padded_lookup (p : Presented L) (x y : L) :
    padded p x y = (lookup p x).bind (fun a =>
      (lookup p y).bind (fun b => (p.algebra.mul a b).map Subtype.val)) := by
  by_cases hx : p.carrier x <;> by_cases hy : p.carrier y <;>
    simp [padded,lookup,hx,hy]
theorem padded_present (p : Presented L) (x y : {x // p.carrier x}) :
    padded p x.val y.val = (p.algebra.mul x y).map Subtype.val := by
  simp [padded,x.property,y.property]
theorem padded_absent_left (p : Presented L) (x y : L) (h : ¬p.carrier x) :
    padded p x y = none := by simp [padded,h]
theorem padded_absent_right (p : Presented L) (x y : L) (h : ¬p.carrier y) :
    padded p x y = none := by simp [padded,h]
theorem padded_some (p : Presented L) (x y z : L) :
    padded p x y = some z ↔
    ∃ hx : p.carrier x, ∃ hy : p.carrier y, ∃ hz : p.carrier z,
      p.algebra.mul ⟨x,hx⟩ ⟨y,hy⟩ = some ⟨z,hz⟩ := by
  by_cases hx : p.carrier x
  · by_cases hy : p.carrier y
    · simp only [padded,dif_pos hx,dif_pos hy]
      cases hm : p.algebra.mul ⟨x,hx⟩ ⟨y,hy⟩ with
      | none => simp [hm]
      | some a =>
        constructor
        · intro h
          have e : a.val = z := Option.some.inj h
          subst z
          exact ⟨hx,hy,a.property,hm⟩
        · rintro ⟨_,_,hz,h⟩
          have e := Option.some.inj (hm.symm.trans h)
          exact congrArg (fun q => some q.val) e
    · simp [padded,hx,hy]
  · simp [padded,hx]
theorem result_membership (p : Presented L) (x y z : L)
    (h : padded p x y = some z) : p.carrier x ∧ p.carrier y ∧ p.carrier z := by
  obtain ⟨hx,hy,hz,_⟩ := (padded_some p x y z).mp h
  exact ⟨hx,hy,hz⟩
theorem carrier_from_row (p : Presented L) (x : L) :
    p.carrier x ↔ ∃ y z, padded p x y = some z := by
  constructor
  · intro hx
    let a : {x // p.carrier x} := ⟨x,hx⟩
    refine ⟨(p.algebra.right a).val.val,x,?_⟩
    rw [padded_present p a (p.algebra.right a).val,p.algebra.mul_right]
    rfl
  · rintro ⟨y,z,h⟩
    exact (result_membership p x y z h).1
theorem table_determines_carrier (p q : Presented L)
    (h : padded p = padded q) : p.carrier = q.carrier := by
  funext x
  apply propext
  rw [carrier_from_row,carrier_from_row,h]
theorem left_bind (p : Presented L) (q : Option {x // p.carrier x})
    (z : {x // p.carrier x}) :
    (q.map Subtype.val).bind (fun x => padded p x z.val) =
      (q.bind (fun x => p.algebra.mul x z)).map Subtype.val := by
  cases q with
  | none => rfl
  | some x => exact padded_present p x z
theorem right_bind (p : Presented L) (x : {x // p.carrier x})
    (q : Option {x // p.carrier x}) :
    (q.map Subtype.val).bind (fun z => padded p x.val z) =
      (q.bind (fun z => p.algebra.mul x z)).map Subtype.val := by
  cases q with
  | none => rfl
  | some z => exact padded_present p x z
theorem padded_assoc (p : Presented L) : OptionFoldV25.Strong (padded p) := by
  intro x y z
  by_cases hx : p.carrier x
  · by_cases hy : p.carrier y
    · by_cases hz : p.carrier z
      · rw [padded_present p ⟨x,hx⟩ ⟨y,hy⟩, padded_present p ⟨y,hy⟩ ⟨z,hz⟩]
        rw [left_bind p _ ⟨z,hz⟩,right_bind p ⟨x,hx⟩]
        exact congrArg (Option.map Subtype.val) (p.algebra.assoc _ _ _)
      · simp [padded_absent_right p _ _ hz]
    · simp [padded_absent_right p _ _ hy,padded_absent_left p _ _ hy]
  · simp [padded_absent_left p _ _ hx]
end PresentedCoreV25
