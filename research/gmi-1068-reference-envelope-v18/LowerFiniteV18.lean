import ScalarLawsV12
namespace LowerFiniteV18
open ScalarV12
universe u
variable {α : Type u} [Scalar α]
noncomputable def meet (a b : α) : α := by
  classical
  exact if a≤b then a else b
theorem meet_le_left (a b : α) : meet a b≤a := by
  classical
  by_cases h : a≤b
  · simp only [meet,if_pos h]; exact Scalar.le_refl _
  · simp only [meet,if_neg h]; exact (Scalar.le_total a b).resolve_left h
theorem meet_le_right (a b : α) : meet a b≤b := by
  classical
  by_cases h : a≤b
  · simpa only [meet,if_pos h] using h
  · simp only [meet,if_neg h]; exact Scalar.le_refl _
theorem le_meet {a b c : α} (ha : c≤a) (hb : c≤b) : c≤meet a b := by
  classical
  unfold meet
  split <;> assumption
noncomputable def lower : {m : Nat} → (Fin (m+1) → α) → α
  | 0, f => f 0
  | m+1, f => meet (f 0) (lower (fun i : Fin (m+1) => f i.succ))
theorem lower_le {m : Nat} (f : Fin (m+1) → α) (i : Fin (m+1)) :
    lower f≤f i := by
  induction m with
  | zero =>
    have hi : i=0 := Fin.ext (by omega)
    subst i
    exact Scalar.le_refl _
  | succ m ih =>
    induction i using Fin.cases with
    | zero => exact meet_le_left _ _
    | succ i =>
      exact Scalar.le_trans (meet_le_right _ _) (ih (fun j => f j.succ) i)
theorem le_lower {m : Nat} (f : Fin (m+1) → α) (c : α)
    (h : ∀ i, c≤f i) : c≤lower f := by
  induction m with
  | zero => exact h 0
  | succ m ih => exact le_meet (h 0) (ih (fun j => f j.succ) (fun j => h j.succ))
theorem lower_monotone {m : Nat} (f g : Fin (m+1) → α)
    (h : ∀ i, f i≤g i) : lower f≤lower g :=
  le_lower g _ (fun i => Scalar.le_trans (lower_le f i) (h i))
theorem lower_constant (m : Nat) (c : α) : lower (fun _ : Fin (m+1) => c)=c := by
  apply Scalar.le_antisymm
  · exact lower_le _ 0
  · exact le_lower _ c (fun _ => Scalar.le_refl _)
theorem lower_singleton (f : Fin 1 → α) : lower f=f 0 := rfl
theorem lower_attained {m : Nat} (f : Fin (m+1) → α) :
    ∃ i, lower f=f i := by
  classical
  induction m with
  | zero => exact ⟨0,rfl⟩
  | succ m ih =>
    obtain ⟨i,hi⟩ := ih (fun j => f j.succ)
    by_cases h : f 0≤lower (fun j => f j.succ)
    · exact ⟨0,by simp only [lower,meet,if_pos h]⟩
    · exact ⟨i.succ,by simp only [lower,meet,if_neg h]; exact hi⟩
end LowerFiniteV18
