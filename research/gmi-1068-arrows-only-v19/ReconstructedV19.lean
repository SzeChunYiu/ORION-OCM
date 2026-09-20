import PartialUnitsV19
import TypedPathsV11
namespace ReconstructedV19
open PartialUnitsV19
universe u
variable {A : Type u} (P : Algebra A)
abbrev Hom (e f : P.Unit) := {x : A // P.left x = e ∧ P.right x = f}
noncomputable def identity (e : P.Unit) : Hom P e e :=
  ⟨e.val, P.left_unit e, P.right_unit e⟩
noncomputable def compose {e f g : P.Unit}
    (x : Hom P e f) (y : Hom P f g) : Hom P e g := by
  have hm : P.right x.val = P.left y.val := x.property.2.trans y.property.1.symm
  let z := Classical.choose (P.product_of_matched hm)
  have hz : P.mul x.val y.val = some z := Classical.choose_spec (P.product_of_matched hm)
  exact ⟨z, (P.left_product hz).trans x.property.1,
    (P.right_product hz).trans y.property.2⟩
theorem compose_binding {e f g : P.Unit}
    (x : Hom P e f) (y : Hom P f g) :
    P.mul x.val y.val = some (compose P x y).val :=
  Classical.choose_spec (P.product_of_matched (x.property.2.trans y.property.1.symm))
theorem compose_value {e f g : P.Unit} (x : Hom P e f) (y : Hom P f g)
    {z : A} (h : P.mul x.val y.val = some z) : (compose P x y).val = z :=
  Option.some.inj ((compose_binding P x y).symm.trans h)
theorem compose_assoc {e f g h : P.Unit}
    (x : Hom P e f) (y : Hom P f g) (z : Hom P g h) :
    compose P (compose P x y) z = compose P x (compose P y z) := by
  apply Subtype.ext
  have hh := P.assoc x.val y.val z.val
  rw [compose_binding P x y, compose_binding P y z] at hh
  simp only [Option.some_bind] at hh
  rw [compose_binding, compose_binding] at hh
  exact Option.some.inj hh
theorem identity_left {e f : P.Unit} (x : Hom P e f) :
    compose P (identity P e) x = x := by
  apply Subtype.ext
  apply compose_value
  have h := P.left_mul x.val
  rw [x.property.1] at h
  exact h
theorem identity_right {e f : P.Unit} (x : Hom P e f) :
    compose P x (identity P f) = x := by
  apply Subtype.ext
  apply compose_value
  have h := P.mul_right x.val
  rw [x.property.2] at h
  exact h
noncomputable def category : TypedPathsV11.Category P.Unit where
  Hom := Hom P
  id := identity P
  comp := compose P
  assoc := compose_assoc P
  left_id := identity_left P
  right_id := identity_right P
theorem category_hom (e f : P.Unit) :
    (category P).Hom e f = {x : A // P.left x = e ∧ P.right x = f} := rfl
theorem category_identity (e : P.Unit) : ((category P).id e).val = e.val := rfl
theorem category_composition {e f g : P.Unit}
    (x : (category P).Hom e f) (y : (category P).Hom f g) :
    P.mul x.val y.val = some ((category P).comp x y).val := compose_binding P x y
end ReconstructedV19
