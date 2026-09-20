import Std
namespace PartialUnitsV19
universe u
def IsUnit (m : A → A → Option A) (e : A) : Prop :=
  m e e = some e ∧ (∀ x y, m e x = some y → y = x) ∧
  (∀ x y, m x e = some y → y = x)
theorem unit_definition (m : A → A → Option A) (e : A) :
    IsUnit m e ↔ m e e = some e ∧ (∀ x y, m e x = some y → y = x) ∧
      (∀ x y, m x e = some y → y = x) := Iff.rfl
structure Algebra (A : Type u) where
  mul : A → A → Option A
  assoc : ∀ x y z, (mul x y).bind (fun v => mul v z) =
    (mul y z).bind (fun v => mul x v)
  localUnits : ∀ x, ∃ e f, IsUnit mul e ∧ IsUnit mul f ∧
    mul e x = some x ∧ mul x f = some x
  coherent : ∀ x y z u v, mul x y = some u → mul y z = some v →
    ∃ w, mul u z = some w
namespace Algebra
variable {A : Type u} (P : Algebra A)
abbrev Unit := {e : A // IsUnit P.mul e}
theorem units_equal {e f z : A} (he : IsUnit P.mul e)
    (hf : IsUnit P.mul f) (h : P.mul e f = some z) : e = f :=
  (hf.2.2 e z h).symm.trans (he.2.1 f z h)
theorem left_unique {e f x : A} (he : IsUnit P.mul e)
    (hf : IsUnit P.mul f) (hx : P.mul e x = some x)
    (hy : P.mul f x = some x) : e = f := by
  have h := P.assoc e f x
  simp only [hy, hx, Option.some_bind] at h
  cases hm : P.mul e f with
  | none => simp [hm, hx, hy] at h
  | some z => exact P.units_equal he hf hm
theorem right_unique {e f x : A} (he : IsUnit P.mul e)
    (hf : IsUnit P.mul f) (hx : P.mul x e = some x)
    (hy : P.mul x f = some x) : e = f := by
  have h := P.assoc x e f
  simp only [hx, hy, Option.some_bind] at h
  cases hm : P.mul e f with
  | none => simp [hm, hx, hy] at h
  | some z => exact P.units_equal he hf hm
noncomputable def left (x : A) : P.Unit :=
  ⟨Classical.choose (P.localUnits x),
    (Classical.choose_spec (Classical.choose_spec (P.localUnits x))).1⟩
noncomputable def right (x : A) : P.Unit :=
  ⟨Classical.choose (Classical.choose_spec (P.localUnits x)),
    (Classical.choose_spec (Classical.choose_spec (P.localUnits x))).2.1⟩
theorem left_mul (x : A) : P.mul (P.left x).val x = some x :=
  (Classical.choose_spec (Classical.choose_spec (P.localUnits x))).2.2.1
theorem mul_right (x : A) : P.mul x (P.right x).val = some x :=
  (Classical.choose_spec (Classical.choose_spec (P.localUnits x))).2.2.2
theorem left_of {e x : A} (he : IsUnit P.mul e)
    (h : P.mul e x = some x) : (P.left x).val = e :=
  P.left_unique (P.left x).property he (P.left_mul x) h
theorem right_of {e x : A} (he : IsUnit P.mul e)
    (h : P.mul x e = some x) : (P.right x).val = e :=
  P.right_unique (P.right x).property he (P.mul_right x) h
theorem left_unit (e : P.Unit) : P.left e.val = e :=
  Subtype.ext (P.left_of e.property e.property.1)
theorem right_unit (e : P.Unit) : P.right e.val = e :=
  Subtype.ext (P.right_of e.property e.property.1)
theorem left_product {x y z : A} (h : P.mul x y = some z) :
    P.left z = P.left x := by
  apply Subtype.ext
  apply P.left_of (P.left x).property
  have hh := P.assoc (P.left x).val x y
  simp only [P.left_mul, Option.some_bind, h] at hh
  simpa only [Option.some_bind, h] using hh.symm
theorem right_product {x y z : A} (h : P.mul x y = some z) :
    P.right z = P.right y := by
  apply Subtype.ext
  apply P.right_of (P.right y).property
  have hh := P.assoc x y (P.right y).val
  rw [P.mul_right, h] at hh
  simpa only [Option.some_bind, h] using hh
theorem matched_of_product {x y z : A} (h : P.mul x y = some z) :
    P.right x = P.left y := by
  have hh := P.assoc x (P.left y).val y
  simp only [P.left_mul, Option.some_bind, h] at hh
  cases hm : P.mul x (P.left y).val with
  | none => simp [hm] at hh
  | some v =>
    have hv := (P.left y).property.2.2 x v hm
    subst v
    exact Subtype.ext (P.right_of (P.left y).property hm)
theorem product_of_matched {x y : A} (h : P.right x = P.left y) :
    ∃ z, P.mul x y = some z := by
  have hy := P.left_mul y
  rw [← h] at hy
  exact P.coherent x (P.right x).val y x y (P.mul_right x) hy
theorem defined_iff_matched (x y : A) :
    (∃ z, P.mul x y = some z) ↔ P.right x = P.left y :=
  ⟨fun ⟨_, h⟩ => P.matched_of_product h, P.product_of_matched⟩
theorem matching_contract (x y : A) :
    (∃ z, P.mul x y = some z) ↔ P.right x = P.left y := P.defined_iff_matched x y
end Algebra
end PartialUnitsV19
