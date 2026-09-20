import Std
namespace ScalarV12
universe u
/-- Scalar operations and primitive ordered commutative ring laws only. -/
class Scalar (α : Type u) extends Add α, Mul α, Neg α, LE α, LT α,
    Zero α, OfNat α 1 where
  add_assoc : ∀ a b c : α, (a+b)+c = a+(b+c)
  add_comm : ∀ a b : α, a+b = b+a
  zero_add : ∀ a : α, 0+a = a
  neg_add : ∀ a : α, -a+a = 0
  mul_assoc : ∀ a b c : α, (a*b)*c = a*(b*c)
  mul_comm : ∀ a b : α, a*b = b*a
  one_mul : ∀ a : α, 1*a = a
  mul_add : ∀ a b c : α, a*(b+c) = a*b+a*c
  le_refl : ∀ a : α, a ≤ a
  le_trans : ∀ {a b c : α}, a ≤ b → b ≤ c → a ≤ c
  le_antisymm : ∀ {a b : α}, a ≤ b → b ≤ a → a = b
  le_total : ∀ a b : α, a ≤ b ∨ b ≤ a
  lt_iff : ∀ a b : α, a < b ↔ a ≤ b ∧ a ≠ b
  add_le_left : ∀ {a b : α}, a ≤ b → ∀ c, c+a ≤ c+b
  mul_nonneg : ∀ {a b : α}, 0 ≤ a → 0 ≤ b → 0 ≤ a*b
  mul_pos : ∀ {a b : α}, 0 < a → 0 < b → 0 < a*b
  zero_lt_one : (0 : α) < 1

variable {α : Type u} [Scalar α]
instance : Std.Associative (α := α) (· + ·) := ⟨Scalar.add_assoc⟩
instance : Std.Commutative (α := α) (· + ·) := ⟨Scalar.add_comm⟩

theorem add_zero (a : α) : a+0 = a := by rw [Scalar.add_comm, Scalar.zero_add]
theorem add_neg (a : α) : a + -a = 0 := by rw [Scalar.add_comm, Scalar.neg_add]
theorem add_cancel {a b c : α} (h : a+b = a+c) : b = c := by
  have hh := congrArg (fun z => -a+z) h
  simpa only [← Scalar.add_assoc, Scalar.neg_add, Scalar.zero_add] using hh
theorem add_right_cancel {a b c : α} (h : b+a = c+a) : b = c := by
  apply add_cancel (a := a)
  simpa only [Scalar.add_comm] using h
theorem neg_unique {a b : α} (h : a+b=0) : a = -b := by
  apply add_right_cancel (a := b)
  rw [h, Scalar.neg_add]
theorem neg_neg (a : α) : - -a = a := (neg_unique (add_neg a)).symm
theorem neg_zero : -(0 : α) = 0 := by
  have h := Scalar.neg_add (0 : α)
  simpa only [add_zero] using h
theorem mul_zero (a : α) : a*0 = 0 := by
  apply add_cancel (a := a*0)
  rw [← Scalar.mul_add, Scalar.zero_add, add_zero]
theorem zero_mul (a : α) : 0*a = 0 := by rw [Scalar.mul_comm, mul_zero]
theorem mul_neg (a b : α) : a * -b = -(a*b) := by
  apply neg_unique
  rw [← Scalar.mul_add, Scalar.neg_add, mul_zero]
theorem neg_sum (a b : α) : -(a+b) = -a + -b := by
  symm
  apply neg_unique
  calc
    (-a + -b)+(a+b) = (-a+a)+(-b+b) := by ac_rfl
    _ = 0 := by rw [Scalar.neg_add, Scalar.neg_add, Scalar.zero_add]
theorem add_mul (a b c : α) : (a+b)*c = a*c+b*c := by
  rw [Scalar.mul_comm, Scalar.mul_add, Scalar.mul_comm c a, Scalar.mul_comm c b]
theorem mul_one (a : α) : a*1 = a := by rw [Scalar.mul_comm, Scalar.one_mul]

theorem add_le_add {a b c d : α} (h : a ≤ b) (k : c ≤ d) : a+c ≤ b+d := by
  apply Scalar.le_trans (b := b+c)
  · simpa only [Scalar.add_comm] using Scalar.add_le_left h c
  · exact Scalar.add_le_left k b
theorem le_of_lt {a b : α} (h : a < b) : a ≤ b := (Scalar.lt_iff a b).mp h |>.1
theorem not_le_of_lt {a b : α} (h : a < b) : ¬ b ≤ a :=
  fun k => ((Scalar.lt_iff a b).mp h).2 (Scalar.le_antisymm (le_of_lt h) k)
theorem lt_of_not_le {a b : α} (h : ¬ b ≤ a) : a < b := by
  apply (Scalar.lt_iff a b).mpr
  refine ⟨(Scalar.le_total a b).resolve_right h, ?_⟩
  intro e
  exact h (e ▸ Scalar.le_refl a)
theorem lt_of_lt_of_le {a b c : α} (h : a < b) (k : b ≤ c) : a < c := by
  apply lt_of_not_le
  intro e
  exact not_le_of_lt h (Scalar.le_trans k e)
theorem lt_of_le_of_lt {a b c : α} (h : a ≤ b) (k : b < c) : a < c := by
  apply lt_of_not_le
  intro e
  exact not_le_of_lt k (Scalar.le_trans e h)
theorem add_lt_left {a b : α} (h : a < b) (c : α) : c+a < c+b := by
  apply (Scalar.lt_iff _ _).mpr
  exact ⟨Scalar.add_le_left (le_of_lt h) c,
    fun e => ((Scalar.lt_iff _ _).mp h).2 (add_cancel e)⟩
theorem add_lt_add {a b c d : α} (h : a < b) (k : c ≤ d) : a+c < b+d := by
  apply lt_of_lt_of_le (b := b+c)
  · simpa only [Scalar.add_comm] using add_lt_left h c
  · exact Scalar.add_le_left k b
theorem diff_eq_zero (a b : α) : a + -b = 0 ↔ a = b := by
  constructor
  · intro h
    have h' := neg_unique h
    simpa only [neg_neg] using h'
  · intro h
    rw [h, add_neg]
theorem diff_nonneg (a b : α) : 0 ≤ a + -b ↔ b ≤ a := by
  constructor
  · intro h
    have hh := Scalar.add_le_left h b
    have e : b+(a + -b) = a := by
      calc
        b+(a + -b) = a+(b + -b) := by ac_rfl
        _ = a := by rw [add_neg, add_zero]
    simpa only [add_zero, e] using hh
  · intro h
    have hh := Scalar.add_le_left h (-b)
    simpa only [Scalar.neg_add, add_neg, Scalar.add_comm] using hh
theorem diff_pos (a b : α) : 0 < a + -b ↔ b < a := by
  rw [Scalar.lt_iff, Scalar.lt_iff, diff_nonneg]
  constructor
  · rintro ⟨h,hn⟩
    refine ⟨h, ?_⟩
    intro he
    exact hn ((diff_eq_zero a b).mpr he.symm).symm
  · rintro ⟨h,hn⟩
    exact ⟨h, fun he => hn ((diff_eq_zero a b).mp he.symm).symm⟩

noncomputable def magnitude (a : α) : α := by
  classical
  exact if 0 ≤ a then a else -a

theorem magnitude_bounds (a : α) : 0 ≤ magnitude a ∧ -a ≤ magnitude a := by
  classical
  by_cases h : 0 ≤ a
  · have hn : -a ≤ 0 := by
      have hh := Scalar.add_le_left h (-a)
      simpa only [add_zero, Scalar.neg_add] using hh
    simp only [magnitude, if_pos h]
    exact ⟨h, Scalar.le_trans hn h⟩
  · have ha : a ≤ 0 := (Scalar.le_total a 0).resolve_right h
    have hh := Scalar.add_le_left ha (-a)
    have hn : 0 ≤ -a := by simpa only [Scalar.neg_add, add_zero] using hh
    simp only [magnitude, if_neg h]
    exact ⟨hn, Scalar.le_refl _⟩

instance intScalar : Scalar Int where
  add := (· + ·); mul := (· * ·); neg := Neg.neg; le := (· ≤ ·); lt := (· < ·)
  zero := 0
  ofNat := 1
  add_assoc := Int.add_assoc
  add_comm := Int.add_comm
  zero_add := Int.zero_add
  neg_add := fun _ => by omega
  mul_assoc := Int.mul_assoc
  mul_comm := Int.mul_comm
  one_mul := Int.one_mul
  mul_add := Int.mul_add
  le_refl := Int.le_refl
  le_trans := Int.le_trans
  le_antisymm := Int.le_antisymm
  le_total := Int.le_total
  lt_iff := fun _ _ => Int.lt_iff_le_and_ne
  add_le_left := Int.add_le_add_left
  mul_nonneg := Int.mul_nonneg
  mul_pos := Int.mul_pos
  zero_lt_one := by decide
end ScalarV12
