import PartialUnitsV19
import TypedPathsV11
namespace BundledCategoryV19
open PartialUnitsV19
universe u v
variable {V : Type u} (C : TypedPathsV11.Category.{u,v} V)
abbrev Arrow := (a : V) × (b : V) × C.Hom a b
def identity (a : V) : Arrow C := ⟨a, a, C.id a⟩
noncomputable def mul : Arrow C → Arrow C → Option (Arrow C) := by
  classical
  exact fun ⟨a,b,f⟩ ⟨c,d,g⟩ =>
    if h : b = c then some ⟨a,d,C.comp f (h.symm ▸ g)⟩ else none
theorem aligned {a b c : V} (f : C.Hom a b) (g : C.Hom b c) :
    mul C ⟨a,b,f⟩ ⟨b,c,g⟩ = some ⟨a,c,C.comp f g⟩ := by simp [mul]
theorem not_aligned {a b c d : V} (f : C.Hom a b) (g : C.Hom c d)
    (h : b ≠ c) : mul C ⟨a,b,f⟩ ⟨c,d,g⟩ = none := by simp [mul,h]
theorem defined_iff (x y : Arrow C) :
    (∃ z, mul C x y = some z) ↔ x.2.1 = y.1 := by
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  by_cases h : b = c
  · subst c
    simp [mul]
  · simp [mul,h]
theorem associative (x y z : Arrow C) :
    (mul C x y).bind (fun p => mul C p z) =
      (mul C y z).bind (fun p => mul C x p) := by
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  rcases z with ⟨e,k,h⟩
  by_cases hbc : b = c <;> by_cases hde : d = e
  · subst c; subst e
    simp [mul,C.assoc]
  · subst c
    simp [mul,hde]
  · subst e
    simp [mul,hbc]
  · simp [mul,hbc,hde]
theorem coherent (x y z p q : Arrow C)
    (hxy : mul C x y = some p) (hyz : mul C y z = some q) :
    ∃ w, mul C p z = some w := by
  have hbc := (defined_iff C x y).mp ⟨p,hxy⟩
  have hde := (defined_iff C y z).mp ⟨q,hyz⟩
  rcases x with ⟨a,b,f⟩
  rcases y with ⟨c,d,g⟩
  rcases z with ⟨e,k,h⟩
  dsimp at hbc hde
  subst c; subst e
  rw [aligned] at hxy
  cases hxy
  exact ⟨_, aligned C _ _⟩
theorem left_identity (x : Arrow C) :
    mul C (identity C x.1) x = some x := by
  rcases x with ⟨a,b,f⟩
  simp [identity,mul,C.left_id]
theorem right_identity (x : Arrow C) :
    mul C x (identity C x.2.1) = some x := by
  rcases x with ⟨a,b,f⟩
  simp [identity,mul,C.right_id]
theorem identity_unit (a : V) : IsUnit (mul C) (identity C a) := by
  refine ⟨left_identity C (identity C a), ?_, ?_⟩
  · intro x y h
    rcases x with ⟨b,c,f⟩
    by_cases hab : a = b
    · subst b
      have hh := left_identity C (⟨a,c,f⟩ : Arrow C)
      rw [hh] at h
      exact (Option.some.inj h).symm
    · simp [mul,identity,hab] at h
  · intro x y h
    rcases x with ⟨b,c,f⟩
    by_cases hca : c = a
    · subst c
      have hh := right_identity C (⟨b,a,f⟩ : Arrow C)
      rw [hh] at h
      exact (Option.some.inj h).symm
    · simp [mul,identity,hca] at h
noncomputable def algebra : Algebra (Arrow C) where
  mul := mul C
  assoc := associative C
  localUnits := fun x => ⟨identity C x.1, identity C x.2.1,
    identity_unit C x.1, identity_unit C x.2.1, left_identity C x, right_identity C x⟩
  coherent := coherent C
theorem algebra_mul (x y : Arrow C) : (algebra C).mul x y = mul C x y := rfl
theorem identity_binding (a : V) : identity C a = ⟨a,a,C.id a⟩ := rfl
theorem unit_iff_identity (x : Arrow C) :
    IsUnit (mul C) x ↔ ∃ a, x = identity C a := by
  constructor
  · intro hx
    exact ⟨x.1, (hx.2.2 (identity C x.1) x (left_identity C x))⟩
  · rintro ⟨a,rfl⟩
    exact identity_unit C a
theorem left_binding (x : Arrow C) :
    ((algebra C).left x).val = identity C x.1 :=
  (algebra C).left_of (identity_unit C x.1) (left_identity C x)
theorem right_binding (x : Arrow C) :
    ((algebra C).right x).val = identity C x.2.1 :=
  (algebra C).right_of (identity_unit C x.2.1) (right_identity C x)
end BundledCategoryV19
