import MatricesV14
namespace OrderedWeightsV27
open StochasticV14
universe u
class OrderedWeight (α : Type u) [Weight α] extends LE α where
  refl : ∀ a : α, a≤a
  trans : ∀ {a b c : α}, a≤b → b≤c → a≤c
  antisymm : ∀ {a b : α}, a≤b → b≤a → a=b
  zero_le : ∀ a : α, 0≤a
  add_mono : ∀ {a b c d : α}, a≤b → c≤d → a+c≤b+d
  mul_left : ∀ {a b : α}, a≤b → ∀ c, c*a≤c*b
  mul_right : ∀ {a b : α}, a≤b → ∀ c, a*c≤b*c
  mul_comm : ∀ a b : α, a*b=b*a
variable {α : Type u} [Weight α] [OrderedWeight α]
theorem sum_mono {n : Nat} (f g : Fin n → α) (h : ∀ i,f i≤g i) : sum f≤sum g := by
  induction n with
  | zero => exact OrderedWeight.refl _
  | succ n ih => exact OrderedWeight.add_mono (h 0) (ih _ _ (fun i => h i.succ))
theorem le_add_right (a b : α) : a≤a+b := by
  have h := OrderedWeight.add_mono (OrderedWeight.refl a) (OrderedWeight.zero_le b)
  simpa only [add_zero] using h
theorem le_add_left (a b : α) : b≤a+b := by
  rw [Weight.add_comm]; exact le_add_right b a
theorem term_le_sum {n : Nat} (f : Fin n → α) (i : Fin n) : f i≤sum f := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    induction i using Fin.cases with
    | zero => exact le_add_right _ _
    | succ i => exact OrderedWeight.trans (ih (fun j => f j.succ) i) (le_add_left _ _)
omit [OrderedWeight α] in
theorem row_comp {n m k : Nat} (p : Matrix α n m) (q : Matrix α m k) (i : Fin n) :
    sum (mcomp p q i)=sum (fun j => p i j * sum (q j)) := by
  unfold mcomp
  rw [sum_swap]
  simp only [sum_mul_left]
theorem comp_bound {n m k : Nat} (p : Matrix α n m) (q : Matrix α m k)
    (hp : ∀ i,sum (p i)≤1) (hq : ∀ j,sum (q j)≤1) :
    ∀ i,sum (mcomp p q i)≤1 := by
  intro i; rw [row_comp]
  apply OrderedWeight.trans _ (hp i)
  have h := sum_mono (fun j => p i j * sum (q j)) (fun j => p i j * 1)
    (fun j => OrderedWeight.mul_left (hq j) (p i j))
  simpa only [Weight.mul_one] using h
instance natOrderedWeight : OrderedWeight Nat where
  le := (· ≤ ·)
  refl := Nat.le_refl
  trans := Nat.le_trans
  antisymm := Nat.le_antisymm
  zero_le := Nat.zero_le
  add_mono := Nat.add_le_add
  mul_left := fun h c => Nat.mul_le_mul_left c h
  mul_right := fun h c => Nat.mul_le_mul_right c h
  mul_comm := Nat.mul_comm
end OrderedWeightsV27
