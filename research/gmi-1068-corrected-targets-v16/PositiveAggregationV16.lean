import LinearBasisV16
namespace PositiveAggregationV16
open ScalarV12 LinearBasisV16
universe u
variable {α : Type u} [Scalar α]

def Monotone {n : Nat} (F : (Fin n → α) → α) : Prop :=
  ∀ x y, CoordLE x y → F x ≤ F y

theorem basis_nonnegative {n : Nat} (k : Fin n) : Nonnegative (basis (α:=α) k) := by
  intro i
  unfold basis
  split
  · exact le_of_lt Scalar.zero_lt_one
  · exact Scalar.le_refl _

theorem monotone_iff_nonnegative {n : Nat} {F : (Fin n → α) → α}
    (h : IsLinear F) : Monotone F ↔ Nonnegative (weights F) := by
  constructor
  · intro hm i
    have hh := hm (fun _ => 0) (basis i) (basis_nonnegative i)
    rw [linear_zero h] at hh
    exact hh
  · intro hw x y hxy
    rw [linear_basis_representation h x, linear_basis_representation h y]
    exact dot_monotone hw hxy

theorem dot_ones {n : Nat} (w : Fin n → α) :
    dot w (fun _ => 1) = sum w := by
  unfold dot
  simp only [mul_one]

theorem normalized_iff_sum_one {n : Nat} {F : (Fin n → α) → α}
    (h : IsLinear F) :
    F (fun _ => 1) = 1 ↔ sum (weights F) = 1 := by
  rw [linear_basis_representation h, dot_ones]

theorem probability_coefficients {n : Nat} (w : Fin n → α)
    (hp : Nonnegative w) (hn : sum w = 1) :
    IsLinear (dot w) ∧ Monotone (dot w) ∧ dot w (fun _ => 1) = 1 :=
  ⟨dot_linear w, (fun _ _ h => dot_monotone hp h), (dot_ones w).trans hn⟩

theorem probability_representation_iff {n : Nat} (F : (Fin n → α) → α) :
    (IsLinear F ∧ Monotone F ∧ F (fun _ => 1) = 1) ↔
    ∃ w : Fin n → α, Nonnegative w ∧ sum w = 1 ∧ ∀ x, F x = dot w x := by
  constructor
  · rintro ⟨hl, hm, hn⟩
    exact ⟨weights F, (monotone_iff_nonnegative hl).mp hm,
      (normalized_iff_sum_one hl).mp hn, linear_basis_representation hl⟩
  · rintro ⟨w, hp, hn, he⟩
    have hf : F = dot w := funext he
    rw [hf]
    exact probability_coefficients w hp hn

theorem probability_representation_unique {n : Nat} (F : (Fin n → α) → α)
    (h : IsLinear F ∧ Monotone F ∧ F (fun _ => 1) = 1) :
    ∃ w : Fin n → α, (Nonnegative w ∧ sum w = 1 ∧ ∀ x, F x = dot w x) ∧
      ∀ v : Fin n → α, (∀ x, F x = dot v x) → v = w := by
  exact ⟨weights F, ⟨
    (monotone_iff_nonnegative h.1).mp h.2.1,
    (normalized_iff_sum_one h.1).mp h.2.2,
    linear_basis_representation h.1⟩,
    fun v hv => representation_unique v hv⟩

theorem zero_ne_one : (0 : α) ≠ 1 := (Scalar.lt_iff _ _).mp Scalar.zero_lt_one |>.2

theorem zero_dimension_not_normalized (F : (Fin 0 → α) → α) (h : IsLinear F) :
    F (fun _ => 1) ≠ 1 := by
  have he : (fun _ : Fin 0 => (1 : α)) = (fun _ => (0 : α)) := by
    funext i
    exact Fin.elim0 i
  rw [he, linear_zero h]
  exact zero_ne_one

def intProjection (x : Fin 2 → Int) : Int := x 0

theorem int_projection_consistency :
    IsLinear intProjection ∧ Monotone intProjection ∧
      intProjection (fun _ => 1) = 1 := by
  refine ⟨⟨?_, ?_⟩, ?_, rfl⟩
  · intro x y
    rfl
  · intro c x
    rfl
  · intro x y h
    exact h 0
end PositiveAggregationV16
