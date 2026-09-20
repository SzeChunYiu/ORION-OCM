import Std
namespace StochasticV14
universe u
/-- Primitive laws for a nonnegative weight carrier, not matrix conclusions. -/
class Weight (α : Type u) extends Add α, Mul α, Zero α, OfNat α 1 where
  add_assoc : ∀ a b c : α, (a+b)+c=a+(b+c)
  add_comm : ∀ a b : α, a+b=b+a
  zero_add : ∀ a : α, 0+a=a
  mul_assoc : ∀ a b c : α, (a*b)*c=a*(b*c)
  one_mul : ∀ a : α, 1*a=a
  mul_one : ∀ a : α, a*1=a
  zero_mul : ∀ a : α, 0*a=0
  mul_zero : ∀ a : α, a*0=0
  mul_add : ∀ a b c : α, a*(b+c)=a*b+a*c
  add_mul : ∀ a b c : α, (a+b)*c=a*c+b*c
  one_ne_zero : (1 : α) ≠ 0
  add_eq_zero : ∀ a b : α, a+b=0 ↔ a=0 ∧ b=0
  mul_eq_zero : ∀ a b : α, a*b=0 ↔ a=0 ∨ b=0
variable {α : Type u} [Weight α]
instance : Std.Associative (α := α) (· + ·) := ⟨Weight.add_assoc⟩
instance : Std.Commutative (α := α) (· + ·) := ⟨Weight.add_comm⟩
theorem add_zero (a : α) : a+0=a := by rw [Weight.add_comm, Weight.zero_add]

def sum : {n : Nat} → (Fin n → α) → α
  | 0, _ => 0
  | _+1, f => f 0 + sum (fun i => f i.succ)
theorem sum_zero (n : Nat) : sum (fun _ : Fin n => (0 : α))=0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp only [sum, ih, Weight.zero_add]
theorem sum_add {n : Nat} (f g : Fin n → α) :
    sum (fun i => f i+g i)=sum f+sum g := by
  induction n with
  | zero => exact (Weight.zero_add _).symm
  | succ n ih => simp only [sum, ih]; ac_rfl
theorem sum_mul_left {n : Nat} (a : α) (f : Fin n → α) :
    sum (fun i => a*f i)=a*sum f := by
  induction n with
  | zero => exact (Weight.mul_zero _).symm
  | succ n ih => simp only [sum, ih, Weight.mul_add]
theorem sum_mul_right {n : Nat} (f : Fin n → α) (a : α) :
    sum (fun i => f i*a)=sum f*a := by
  induction n with
  | zero => exact (Weight.zero_mul _).symm
  | succ n ih => simp only [sum, ih, Weight.add_mul]
theorem sum_swap {n m : Nat} (f : Fin n → Fin m → α) :
    sum (fun i => sum (f i))=sum (fun j => sum (fun i => f i j)) := by
  induction n with
  | zero => exact (sum_zero m).symm
  | succ n ih => simp only [sum, ih, sum_add]
theorem sum_pick {n : Nat} (f : Fin n → α) (k : Fin n) :
    sum (fun i => if i=k then f i else 0)=f k := by
  induction n with
  | zero => exact Fin.elim0 k
  | succ n ih =>
    induction k using Fin.cases with
    | zero => simp [sum, Fin.succ_ne_zero, sum_zero, add_zero]
    | succ k =>
      have hz : (0 : Fin (n+1)) ≠ k.succ := Ne.symm (Fin.succ_ne_zero k)
      simpa only [sum, hz, Fin.succ_inj, ↓reduceIte, Weight.zero_add] using
        ih (fun i => f i.succ) k
theorem sum_eq_zero {n : Nat} (f : Fin n → α) :
    sum f=0 ↔ ∀ i, f i=0 := by
  induction n with
  | zero => exact ⟨fun _ i => Fin.elim0 i, fun _ => rfl⟩
  | succ n ih =>
    rw [sum, Weight.add_eq_zero, ih]
    constructor
    · rintro ⟨h0,hs⟩ i
      exact Fin.cases h0 hs i
    · intro h
      exact ⟨h 0, fun i => h i.succ⟩
theorem sum_support {n : Nat} (f : Fin n → α) :
    sum f≠0 ↔ ∃ i, f i≠0 := by
  classical
  constructor
  · intro h
    by_cases he : ∃ i, f i≠0
    · exact he
    · exfalso
      apply h
      apply (sum_eq_zero f).mpr
      intro i
      apply Classical.byContradiction
      intro hi
      exact he ⟨i,hi⟩
  · rintro ⟨i,hi⟩ h
    exact hi ((sum_eq_zero f).mp h i)
theorem mul_support (a b : α) :
    a*b≠0 ↔ a≠0 ∧ b≠0 := by
  simp only [ne_eq, Weight.mul_eq_zero, not_or]

instance natWeight : Weight Nat where
  add := (· + ·); mul := (· * ·); zero := 0; ofNat := 1
  add_assoc := Nat.add_assoc
  add_comm := Nat.add_comm
  zero_add := Nat.zero_add
  mul_assoc := Nat.mul_assoc
  one_mul := Nat.one_mul
  mul_one := Nat.mul_one
  zero_mul := Nat.zero_mul
  mul_zero := Nat.mul_zero
  mul_add := Nat.mul_add
  add_mul := Nat.add_mul
  one_ne_zero := by decide
  add_eq_zero := fun _ _ => Nat.add_eq_zero_iff
  mul_eq_zero := fun _ _ => Nat.mul_eq_zero
end StochasticV14
