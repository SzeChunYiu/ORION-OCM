import PartialUnitsV19
namespace TableTransportV19
open PartialUnitsV19
universe u v
structure TableIso {A : Type u} {B : Type v}
    (m : A → A → Option A) (n : B → B → Option B) where
  forward : A → B
  backward : B → A
  backward_forward : ∀ x, backward (forward x) = x
  forward_backward : ∀ x, forward (backward x) = x
  mul : ∀ x y, n (forward x) (forward y) = (m x y).map forward
namespace TableIso
variable {A : Type u} {B : Type v} {m : A → A → Option A} {n : B → B → Option B}
variable (I : TableIso m n)
theorem forward_injective {x y : A} (h : I.forward x = I.forward y) : x = y := by
  have hh := congrArg I.backward h
  simpa only [I.backward_forward] using hh
theorem backward_mul (x y : B) :
    m (I.backward x) (I.backward y) = (n x y).map I.backward := by
  have h := congrArg (Option.map I.backward) (I.mul (I.backward x) (I.backward y))
  rw [I.forward_backward,I.forward_backward] at h
  rw [h]
  cases m (I.backward x) (I.backward y) <;> simp [I.backward_forward]
def symm : TableIso n m where
  forward := I.backward
  backward := I.forward
  backward_forward := I.forward_backward
  forward_backward := I.backward_forward
  mul := I.backward_mul
theorem reflect_product {x y z : A}
    (h : n (I.forward x) (I.forward y) = some (I.forward z)) : m x y = some z := by
  rw [I.mul] at h
  cases hm : m x y with
  | none => simp [hm] at h
  | some w =>
    rw [hm] at h
    rw [I.forward_injective (Option.some.inj h)]
theorem unit_forward {e : A} (he : IsUnit m e) : IsUnit n (I.forward e) := by
  refine ⟨?_,?_,?_⟩
  · rw [I.mul,he.1]
    rfl
  · intro x y h
    have hh := h
    rw [← I.forward_backward x, ← I.forward_backward y] at hh
    have hy := he.2.1 _ _ (I.reflect_product hh)
    calc
      y = I.forward (I.backward y) := (I.forward_backward y).symm
      _ = I.forward (I.backward x) := congrArg I.forward hy
      _ = x := I.forward_backward x
  · intro x y h
    have hh := h
    rw [← I.forward_backward x, ← I.forward_backward y] at hh
    have hy := he.2.2 _ _ (I.reflect_product hh)
    calc
      y = I.forward (I.backward y) := (I.forward_backward y).symm
      _ = I.forward (I.backward x) := congrArg I.forward hy
      _ = x := I.forward_backward x
theorem unit_iff (e : A) : IsUnit n (I.forward e) ↔ IsUnit m e := by
  constructor
  · intro h
    have hh := I.symm.unit_forward h
    simpa only [symm,I.backward_forward] using hh
  · exact I.unit_forward
end TableIso
end TableTransportV19
