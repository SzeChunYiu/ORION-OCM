import CandidateContextsV24
namespace PriceContextsV24
open PartialContextV15 ImageTransportV24 FrontierOrderV20 ScalarV12 CandidateContextsV24
universe u v
variable {I : Type u} {α : Type v} [Scalar α] {n : Nat}
def scalarOrder : PreorderSpec (I × α) where
  le a b := b.2≤a.2
  refl _ := Scalar.le_refl _
  trans h k := Scalar.le_trans k h
def context (r : I → Fin n → α) (w : Fin n → α) : Context I (I × α) :=
  ProfileContextsV24.context (fun _ => True) scalarOrder (fun i => (i,dot w (r i)))
def Argmin (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α) (i : I) :=
  P i ∧ ∀ j, P j → dot w (r i)≤dot w (r j)
theorem image_pair (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α)
    (i : I) (v : α) :
    Image P (context r w) (i,v) ↔ P i ∧ dot w (r i)=v := by
  simp only [context,ProfileContextsV24.decoded_image,true_and,Prod.mk.injEq]
  constructor
  · rintro ⟨j,hj,he,hv⟩; subst j; exact ⟨hj,hv⟩
  · rintro ⟨hp,hv⟩; exact ⟨i,hp,rfl,hv⟩
theorem maximal_pair (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α) (i : I) :
    Maximal scalarOrder (Image P (context r w)) (i,dot w (r i)) ↔ Argmin P r w i := by
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨((image_pair P r w i _).mp hi).1,?_⟩
    intro j hj
    rcases Scalar.le_total (dot w (r i)) (dot w (r j)) with h | h
    · exact h
    · exact hm (j,dot w (r j)) ((image_pair P r w j _).mpr ⟨hj,rfl⟩) h
  · rintro ⟨hi,hm⟩
    refine ⟨(image_pair P r w i _).mpr ⟨hi,rfl⟩,?_⟩
    rintro ⟨j,v⟩ hj _
    obtain ⟨hp,hv⟩ := (image_pair P r w j v).mp hj
    subst v
    exact hm j hp
theorem maximal_ids (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α) (i : I) :
    (∃ v, Maximal scalarOrder (Image P (context r w)) (i,v)) ↔ Argmin P r w i := by
  constructor
  · rintro ⟨v,hv⟩
    have he := ((image_pair P r w i v).mp hv.1).2
    subst v
    exact (maximal_pair P r w i).mp hv
  · intro h; exact ⟨dot w (r i),(maximal_pair P r w i).mpr h⟩
theorem positive_price_pareto (P : I → Prop) (r : I → Fin n → α)
    (w : Fin n → α) (positive : Positive w) (i : I) (hi : Argmin P r w i) :
    Pareto P r i := by
  apply (pareto_nondominated P r i).mpr
  refine ⟨hi.1,?_⟩
  rintro ⟨j,hj,hji,k,hk⟩
  have hs := dot_strict (fun k => le_of_lt (positive k)) hji k hk (positive k)
  exact not_le_of_lt hs (hi.2 j hj)
theorem tied_argmin (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α)
    (i j : I) (hi : Argmin P r w i) (hj : P j) (he : dot w (r j)=dot w (r i)) :
    Argmin P r w j := by
  refine ⟨hj,?_⟩
  intro k hk
  rw [he]
  exact hi.2 k hk
theorem context_binding (r : I → Fin n → α) (w : Fin n → α) :
    (context r w).defined=(fun _ => True) ∧
    (context r w).eval=(fun h => (h.val,dot w (r h.val))) ∧
    (context r w).order=scalarOrder := ⟨rfl,rfl,rfl⟩
theorem scalar_order_binding (a b : I × α) : scalarOrder.le a b ↔ b.2≤a.2 := Iff.rfl
end PriceContextsV24
