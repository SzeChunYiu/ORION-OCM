import ScalarLawsV12
namespace ScalarV12
universe u
variable {α : Type u} [Scalar α]

def sum : {n : Nat} → (Fin n → α) → α
  | 0, _ => 0
  | _+1, f => f 0 + sum (fun i => f i.succ)

theorem sum_zero (n : Nat) : sum (fun _ : Fin n => (0 : α)) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [sum, ih, Scalar.zero_add]

theorem sum_add {n : Nat} (f g : Fin n → α) :
    sum (fun i => f i+g i) = sum f+sum g := by
  induction n with
  | zero => exact (Scalar.zero_add _).symm
  | succ n ih =>
    simp only [sum, ih]
    ac_rfl

theorem sum_neg {n : Nat} (f : Fin n → α) :
    sum (fun i => -f i) = -(sum f) := by
  induction n with
  | zero => exact neg_zero.symm
  | succ n ih => simp only [sum, ih, neg_sum]

theorem sum_mul {n : Nat} (a : α) (f : Fin n → α) :
    sum (fun i => a*f i) = a*sum f := by
  induction n with
  | zero => exact (mul_zero a).symm
  | succ n ih => simp only [sum, ih, Scalar.mul_add]

theorem sum_le {n : Nat} {f g : Fin n → α} (h : ∀ i, f i ≤ g i) :
    sum f ≤ sum g := by
  induction n with
  | zero => exact Scalar.le_refl _
  | succ n ih => exact add_le_add (h 0) (ih (fun i => h i.succ))

theorem sum_nonneg {n : Nat} {f : Fin n → α} (h : ∀ i, 0 ≤ f i) :
    0 ≤ sum f := by
  have hh := sum_le h
  rw [sum_zero] at hh
  exact hh

theorem sum_strict {n : Nat} {f g : Fin n → α} (h : ∀ i, f i ≤ g i)
    (k : Fin n) (hk : f k < g k) : sum f < sum g := by
  induction n with
  | zero => exact Fin.elim0 k
  | succ n ih =>
    induction k using Fin.cases with
    | zero => exact add_lt_add hk (sum_le (fun i => h i.succ))
    | succ k =>
      have ht := ih (fun i => h i.succ) k hk
      simpa only [sum, Scalar.add_comm] using add_lt_add ht (h 0)

def except {n : Nat} (f : Fin n → α) (k : Fin n) : α :=
  sum (fun i => if i=k then 0 else f i)

theorem except_nonneg {n : Nat} {f : Fin n → α} (h : ∀ i, 0 ≤ f i) (k : Fin n) :
    0 ≤ except f k := by
  apply sum_nonneg
  intro i
  split
  · exact Scalar.le_refl _
  · exact h i

theorem except_add {n : Nat} (f g : Fin n → α) (k : Fin n) :
    except (fun i => f i+g i) k = except f k+except g k := by
  rw [except, except, except, ← sum_add]
  congr 1
  funext i
  by_cases h : i=k <;> simp [h, Scalar.zero_add]

theorem except_mul {n : Nat} (a : α) (f : Fin n → α) (k : Fin n) :
    except (fun i => a*f i) k = a*except f k := by
  rw [except, except, ← sum_mul]
  congr 1
  funext i
  by_cases h : i=k <;> simp [h, mul_zero]

theorem sum_split {n : Nat} (f : Fin n → α) (k : Fin n) :
    sum f = f k+except f k := by
  induction n with
  | zero => exact Fin.elim0 k
  | succ n ih =>
    induction k using Fin.cases with
    | zero =>
      simp only [sum, except, Fin.succ_ne_zero, ↓reduceIte, Scalar.zero_add]
    | succ k =>
      have hz : (0 : Fin (n+1)) ≠ k.succ := Ne.symm (Fin.succ_ne_zero k)
      simp only [sum, except, hz, Fin.succ_inj, ↓reduceIte]
      have ht := ih (fun i => f i.succ) k
      unfold except at ht
      rw [ht]
      ac_rfl

def dot {n : Nat} (w x : Fin n → α) := sum (fun i => w i*x i)
def CoordLE {n : Nat} (x y : Fin n → α) := ∀ i, x i ≤ y i
def Positive {n : Nat} (w : Fin n → α) := ∀ i, 0 < w i
def Nonnegative {n : Nat} (w : Fin n → α) := ∀ i, 0 ≤ w i

theorem mul_le {a x y : α} (ha : 0 ≤ a) (h : x ≤ y) : a*x ≤ a*y := by
  apply (diff_nonneg (a*y) (a*x)).mp
  have hh := Scalar.mul_nonneg ha ((diff_nonneg y x).mpr h)
  simpa only [Scalar.mul_add, mul_neg] using hh

theorem mul_strict {a x y : α} (ha : 0 < a) (h : x < y) : a*x < a*y := by
  apply (diff_pos (a*y) (a*x)).mp
  have hh := Scalar.mul_pos ha ((diff_pos y x).mpr h)
  simpa only [Scalar.mul_add, mul_neg] using hh

theorem dot_difference {n : Nat} (w x y : Fin n → α) :
    dot w (fun i => x i + -y i) = dot w x + -(dot w y) := by
  unfold dot
  simp only [Scalar.mul_add, mul_neg, sum_add, sum_neg]

theorem dot_monotone {n : Nat} {w x y : Fin n → α}
    (hw : Nonnegative w) (h : CoordLE x y) : dot w x ≤ dot w y :=
  sum_le (fun i => mul_le (hw i) (h i))

theorem dot_strict {n : Nat} {w x y : Fin n → α}
    (hw : Nonnegative w) (h : CoordLE x y)
    (k : Fin n) (hk : x k < y k) (hwk : 0 < w k) : dot w x < dot w y :=
  sum_strict (fun i => mul_le (hw i) (h i)) k (mul_strict hwk hk)
end ScalarV12
