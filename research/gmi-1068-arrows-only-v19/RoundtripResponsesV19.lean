import CategoryRoundtripV19
import ResponsesV19
namespace RoundtripResponsesV19
open PartialUnitsV19 TableTransportV19 ResponsesV19
universe u v
variable {A : Type u} (P : Algebra A)
noncomputable def arrowIso :
    TableIso P.mul (BundledCategoryV19.mul (ReconstructedV19.category P)) where
  forward := ArrowRoundtripV19.pack P
  backward := ArrowRoundtripV19.unpack P
  backward_forward := ArrowRoundtripV19.unpack_pack P
  forward_backward := ArrowRoundtripV19.pack_unpack P
  mul := ArrowRoundtripV19.packed_mul P
theorem pack_response (q : Query A) :
    response (BundledCategoryV19.mul (ReconstructedV19.category P))
      (q.map (ArrowRoundtripV19.pack P)) =
    (response P.mul q).map (ArrowRoundtripV19.pack P) := response_transport (arrowIso P) q
theorem unpack_response (q : Query (ArrowRoundtripV19.Bundled P)) :
    response P.mul (q.map (ArrowRoundtripV19.unpack P)) =
    (response (BundledCategoryV19.mul (ReconstructedV19.category P)) q).map
      (ArrowRoundtripV19.unpack P) := response_transport (arrowIso P).symm q
variable {V : Type u} (C : TypedPathsV11.Category.{u,v} V)
noncomputable def categoryForward :
    BundledCategoryV19.Arrow C →
      BundledCategoryV19.Arrow (CategoryRoundtripV19.Rebuilt C)
  | ⟨a,b,f⟩ => ⟨CategoryRoundtripV19.objectForward C a,
    CategoryRoundtripV19.objectForward C b,CategoryRoundtripV19.homForward C f⟩
def categoryBackward :
    BundledCategoryV19.Arrow (CategoryRoundtripV19.Rebuilt C) →
      BundledCategoryV19.Arrow C := ArrowRoundtripV19.unpack (BundledCategoryV19.algebra C)
theorem categoryForward_eq_pack (x : BundledCategoryV19.Arrow C) :
    categoryForward C x = ArrowRoundtripV19.pack (BundledCategoryV19.algebra C) x := by
  apply ArrowRoundtripV19.unpack_injective
  rcases x with ⟨a,b,f⟩
  rfl
theorem category_backward_forward (x : BundledCategoryV19.Arrow C) :
    categoryBackward C (categoryForward C x) = x := by
  rw [categoryForward_eq_pack]
  rfl
theorem category_forward_backward
    (x : BundledCategoryV19.Arrow (CategoryRoundtripV19.Rebuilt C)) :
    categoryForward C (categoryBackward C x) = x := by
  rw [categoryForward_eq_pack]
  exact ArrowRoundtripV19.pack_unpack _ x
noncomputable def categoryIso :
    TableIso (BundledCategoryV19.mul C)
      (BundledCategoryV19.mul (CategoryRoundtripV19.Rebuilt C)) where
  forward := categoryForward C
  backward := categoryBackward C
  backward_forward := category_backward_forward C
  forward_backward := category_forward_backward C
  mul := by
    intro x y
    have hf : categoryForward C = ArrowRoundtripV19.pack (BundledCategoryV19.algebra C) :=
      funext (categoryForward_eq_pack C)
    rw [hf]
    exact ArrowRoundtripV19.packed_mul _ x y
theorem category_forward_response (q : Query (BundledCategoryV19.Arrow C)) :
    response (BundledCategoryV19.mul (CategoryRoundtripV19.Rebuilt C))
      (q.map (categoryForward C)) =
      (response (BundledCategoryV19.mul C) q).map (categoryForward C) :=
  response_transport (categoryIso C) q
theorem category_backward_response
    (q : Query (BundledCategoryV19.Arrow (CategoryRoundtripV19.Rebuilt C))) :
    response (BundledCategoryV19.mul C) (q.map (categoryBackward C)) =
      (response (BundledCategoryV19.mul (CategoryRoundtripV19.Rebuilt C)) q).map
        (categoryBackward C) := response_transport (categoryIso C).symm q
end RoundtripResponsesV19
