import FiniteSumsV12
namespace LinearBasisV16
open ScalarV12
universe u
variable {α : Type u} [Scalar α]

def IsLinear {n : Nat} (F : (Fin n → α) → α) : Prop :=
  (∀ x y, F (fun i => x i + y i) = F x + F y) ∧
  (∀ c x, F (fun i => c * x i) = c * F x)

def basis {n : Nat} (k : Fin n) (j : Fin n) : α := if j=k then 1 else 0
def weights {n : Nat} (F : (Fin n → α) → α) (i : Fin n) : α := F (basis i)

theorem linear_zero {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F) :
    F (fun _ => 0) = 0 := by
  have hh := h.2 0 (fun _ => 0)
  simpa only [zero_mul] using hh

theorem sum_pick {n : Nat} (f : Fin n → α) (k : Fin n) :
    sum (fun i => if i=k then f i else 0) = f k := by
  induction n with
  | zero => exact Fin.elim0 k
  | succ n ih =>
    induction k using Fin.cases with
    | zero =>
      simp only [sum, Fin.succ_ne_zero, ↓reduceIte, sum_zero, add_zero]
    | succ k =>
      have hz : (0 : Fin (n+1)) ≠ k.succ := Ne.symm (Fin.succ_ne_zero k)
      simp only [sum, hz, Fin.succ_inj, ↓reduceIte, Scalar.zero_add]
      exact ih (fun i => f i.succ) k

theorem basis_expansion {n : Nat} (x : Fin n → α) :
    (fun j => sum (fun i => x i * basis i j)) = x := by
  funext j
  have he : (fun i => x i * basis i j) = (fun i => if i=j then x i else 0) := by
    funext i
    by_cases h : i=j
    · subst i
      simp only [basis, ↓reduceIte, mul_one]
    · simp only [basis, Ne.symm h, ↓reduceIte, mul_zero, h]
  rw [he, sum_pick]

theorem linear_map_sum {n : Nat} {F : (Fin n → α) → α} (h : IsLinear F)
    {m : Nat} (x : Fin m → Fin n → α) :
    F (fun j => sum (fun i => x i j)) = sum (fun i => F (x i)) := by
  induction m with
  | zero => exact linear_zero h
  | succ m ih =>
    change F (fun j => x 0 j + sum (fun i => x i.succ j)) =
      F (x 0) + sum (fun i => F (x i.succ))
    rw [h.1, ih]

theorem linear_basis_representation {n : Nat} {F : (Fin n → α) → α}
    (h : IsLinear F) (x : Fin n → α) : F x = dot (weights F) x := by
  calc
    F x = F (fun j => sum (fun i => x i * basis i j)) :=
      congrArg F (basis_expansion x).symm
    _ = sum (fun i => F (fun j => x i * basis i j)) := linear_map_sum h _
    _ = sum (fun i => x i * weights F i) := by
      congr 1
      funext i
      exact h.2 (x i) (basis i)
    _ = dot (weights F) x := by
      unfold dot
      congr 1
      funext i
      exact Scalar.mul_comm _ _

theorem dot_basis {n : Nat} (w : Fin n → α) (k : Fin n) :
    dot w (basis k) = w k := by
  unfold dot
  have he : (fun i => w i * basis k i) = (fun i => if i=k then w i else 0) := by
    funext i
    by_cases h : i=k <;> simp only [basis, h, ↓reduceIte, mul_one, mul_zero]
  rw [he, sum_pick]

theorem representation_unique {n : Nat} {F : (Fin n → α) → α}
    (w : Fin n → α) (h : ∀ x, F x = dot w x) : w = weights F := by
  funext i
  exact (dot_basis w i).symm.trans (h (basis i)).symm

theorem dot_linear {n : Nat} (w : Fin n → α) : IsLinear (dot w) := by
  constructor
  · intro x y
    unfold dot
    simp only [Scalar.mul_add, sum_add]
  · intro c x
    unfold dot
    have he : (fun i => w i * (c * x i)) = (fun i => c * (w i * x i)) := by
      funext i
      rw [← Scalar.mul_assoc, Scalar.mul_comm (w i) c, Scalar.mul_assoc]
    rw [he, sum_mul]

theorem unique_linear_representation {n : Nat} {F : (Fin n → α) → α}
    (h : IsLinear F) :
    ∃ w, (∀ x, F x = dot w x) ∧ ∀ v, (∀ x, F x = dot v x) → v=w :=
  ⟨weights F, linear_basis_representation h, fun v hv => representation_unique v hv⟩
end LinearBasisV16
