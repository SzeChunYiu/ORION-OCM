import ReconstructedV19
import BundledCategoryV19
namespace ArrowRoundtripV19
open PartialUnitsV19
universe u
variable {A : Type u} (P : Algebra A)
abbrev Bundled := BundledCategoryV19.Arrow (ReconstructedV19.category P)
def unpack (x : Bundled P) : A := x.2.2.val
noncomputable def pack (x : A) : Bundled P :=
  ⟨P.left x, P.right x, ⟨x,rfl,rfl⟩⟩
theorem unpack_pack (x : A) : unpack P (pack P x) = x := rfl
theorem pack_unpack (x : Bundled P) : pack P (unpack P x) = x := by
  rcases x with ⟨e,f,x,hleft,hright⟩
  dsimp [pack,unpack]
  cases hleft
  cases hright
  rfl
theorem unpack_injective {x y : Bundled P} (h : unpack P x = unpack P y) : x = y := by
  rw [← pack_unpack P x, ← pack_unpack P y, h]
theorem unpack_product {x y z : Bundled P}
    (h : BundledCategoryV19.mul (ReconstructedV19.category P) x y = some z) :
    P.mul (unpack P x) (unpack P y) = some (unpack P z) := by
  have hm := (BundledCategoryV19.defined_iff _ x y).mp ⟨z,h⟩
  rcases x with ⟨e,f,x⟩
  rcases y with ⟨g,k,y⟩
  dsimp at hm
  subst g
  rw [BundledCategoryV19.aligned] at h
  cases h
  exact ReconstructedV19.category_composition P x y
theorem packed_mul (x y : A) :
    BundledCategoryV19.mul (ReconstructedV19.category P) (pack P x) (pack P y) =
      (P.mul x y).map (pack P) := by
  cases hm : P.mul x y with
  | none =>
    cases hb : BundledCategoryV19.mul (ReconstructedV19.category P) (pack P x) (pack P y) with
    | none => rfl
    | some z =>
      have hh := unpack_product P hb
      simp only [unpack_pack, hm] at hh
      cases hh
  | some z =>
    have hmatch := P.matched_of_product hm
    have hd : (pack P x).2.1 = (pack P y).1 := hmatch
    obtain ⟨w,hw⟩ := (BundledCategoryV19.defined_iff
      (ReconstructedV19.category P) (pack P x) (pack P y)).mpr hd
    rw [hw]
    congr 1
    apply unpack_injective P
    have hh := unpack_product P hw
    simp only [unpack_pack,hm] at hh
    exact (Option.some.inj hh).symm
theorem unpacked_mul (x y : Bundled P) :
    (BundledCategoryV19.mul (ReconstructedV19.category P) x y).map (unpack P) =
      P.mul (unpack P x) (unpack P y) := by
  rw [← pack_unpack P x, ← pack_unpack P y, packed_mul]
  simp only [unpack_pack, Option.map_map]
  cases P.mul (unpack P x) (unpack P y) <;> rfl
end ArrowRoundtripV19
