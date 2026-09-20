import AffineWinnersV23
namespace FiniteWinnersV23
open ScalarV12 PartialContextV15 FrontierOrderV20 AffineContextsV23
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
noncomputable def activeList (P E : I→Prop) (xs : List I) : List I := by
  classical
  exact xs.filter (fun i => decide (active P E i))
noncomputable def winnerList (P E : I→Prop) (a b : I→α) (t : α) (xs : List I) : List I := by
  classical
  exact frontier (codedOrder a b t) (activeList P E xs)
theorem active_mem (P E : I→Prop) (xs : List I) (i : I) :
    i∈activeList P E xs ↔ i∈xs ∧ active P E i := by
  simp only [activeList,List.mem_filter,decide_eq_true_eq]
theorem winner_mem (P E : I→Prop) (a b : I→α) (t : α) (xs : List I)
    (complete : ∀i,active P E i→i∈xs) (i : I) :
    i∈winnerList P E a b t xs ↔ Winner P E a b t i := by
  classical
  rw [winnerList,frontier_mem]
  constructor
  · rintro ⟨hi,hm⟩
    refine ⟨((active_mem P E xs i).mp hi).2,?_⟩
    intro j hj
    have hj' := (active_mem P E xs j).mpr ⟨complete j hj,hj⟩
    rcases Scalar.le_total (score a b t j) (score a b t i) with hji|hij
    · exact hm j hj' hji
    · exact hij
  · rintro ⟨hi,hw⟩
    exact ⟨(active_mem P E xs i).mpr ⟨complete i hi,hi⟩,
      fun j hj _ => hw j ((active_mem P E xs j).mp hj).2⟩
theorem finite_winner (P E : I→Prop) (a b : I→α) (t : α) (xs : List I)
    (complete : ∀i,active P E i→i∈xs) (h : ∃i,active P E i) :
    ∃i,Winner P E a b t i := by
  classical
  obtain ⟨i,hi⟩ := h
  have hm := (active_mem P E xs i).mpr ⟨complete i hi,hi⟩
  obtain ⟨j,hj,_⟩ := (frontier_cofinal (codedOrder a b t) (activeList P E xs)).2 i hm
  exact ⟨j,(winner_mem P E a b t xs complete j).mp hj⟩
theorem finite_empty (P E : I→Prop) (a b : I→α) (t : α) (xs : List I)
    (h : ∀i,i∈xs→¬active P E i) : winnerList P E a b t xs=[] := by
  classical
  have he : activeList P E xs=[] := by
    apply List.eq_nil_iff_forall_not_mem.mpr
    intro i hi
    obtain ⟨him,hia⟩ := (active_mem P E xs i).mp hi
    exact h i him hia
  simp only [winnerList,he,frontier_empty]
end FiniteWinnersV23
