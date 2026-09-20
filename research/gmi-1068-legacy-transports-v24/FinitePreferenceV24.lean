import PriceContextsV24
namespace FinitePreferenceV24
open PartialContextV15 FrontierOrderV20 CandidateContextsV24 ScalarV12
universe u v
variable {I : Type u} {α : Type v} [Scalar α] {n : Nat}
noncomputable def retained (P : I → Prop) (xs : List I) : List I := by
  classical
  exact xs.filter (fun i => decide (P i))
def codeOrder (r : I → Fin n → α) : PreorderSpec I :=
  pullback vectorOrder (fun i => (i,r i))
noncomputable def paretoList (P : I → Prop) (r : I → Fin n → α) (xs : List I) : List I := by
  classical
  exact frontier (codeOrder r) (retained P xs)
theorem retained_mem (P : I → Prop) (xs : List I) (i : I) :
    i∈retained P xs ↔ i∈xs ∧ P i := by
  classical
  simp [retained]
theorem paretoList_mem (P : I → Prop) (r : I → Fin n → α) (xs : List I)
    (complete : ∀ i, P i → i∈xs) (i : I) :
    i∈paretoList P r xs ↔ Pareto P r i := by
  classical
  rw [paretoList,frontier_mem]
  constructor
  · rintro ⟨hi,hm⟩
    exact ⟨((retained_mem P xs i).mp hi).2,
      fun j hj hji => hm j ((retained_mem P xs j).mpr ⟨complete j hj,hj⟩) hji⟩
  · rintro ⟨hi,hm⟩
    exact ⟨(retained_mem P xs i).mpr ⟨complete i hi,hi⟩,
      fun j hj hji => hm j ((retained_mem P xs j).mp hj).2 hji⟩
theorem empty_pareto (r : I → Fin n → α) (i : I) :
    ¬Pareto (fun _ => False) r i := fun h => h.1
theorem empty_argmin (r : I → Fin n → α) (w : Fin n → α) (i : I) :
    ¬PriceContextsV24.Argmin (fun _ => False) r w i := fun h => h.1
theorem retained_binding (P : I → Prop) (xs : List I) :
    retained P xs=xs.filter (fun i => @decide (P i) (Classical.propDecidable _)) := rfl
theorem paretoList_binding (P : I → Prop) (r : I → Fin n → α) (xs : List I) :
    paretoList P r xs=@frontier I (codeOrder r)
      (fun _ _ => Classical.propDecidable _) (retained P xs) := rfl
end FinitePreferenceV24
