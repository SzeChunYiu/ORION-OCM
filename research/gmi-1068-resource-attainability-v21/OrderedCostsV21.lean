import PartialContextV15
namespace OrderedCostsV21
open PartialContextV15
universe u v
structure CostMonoid (R : Type u) where
  order : PreorderSpec R
  one : R
  mul : R → R → R
  assoc : ∀ a b c, mul (mul a b) c=mul a (mul b c)
  left_id : ∀ a, mul one a=a
  right_id : ∀ a, mul a one=a
  mono : ∀ {a b c d}, order.le a b → order.le c d → order.le (mul a c) (mul b d)
def natAdd : CostMonoid Nat where
  order := ⟨Nat.le,Nat.le_refl,fun h1 h2 => Nat.le_trans h1 h2⟩
  one := 0
  mul := Nat.add
  assoc := Nat.add_assoc
  left_id := Nat.zero_add
  right_id := Nat.add_zero
  mono := Nat.add_le_add
def natMax : CostMonoid Nat where
  order := natAdd.order
  one := 0
  mul := max
  assoc := Nat.max_assoc
  left_id := Nat.zero_max
  right_id := Nat.max_zero
  mono := by intro a b c d hab hcd; change a ≤ b at hab; change c ≤ d at hcd; change max a c ≤ max b d; omega
def product {R : Type u} {T : Type v} (r : CostMonoid R) (t : CostMonoid T) :
    CostMonoid (R × T) where
  order :=
    ⟨fun a b => r.order.le a.1 b.1 ∧ t.order.le a.2 b.2,
     fun a => ⟨r.order.refl a.1,t.order.refl a.2⟩,
     fun hab hbc => ⟨r.order.trans hab.1 hbc.1,t.order.trans hab.2 hbc.2⟩⟩
  one := (r.one,t.one)
  mul a b := (r.mul a.1 b.1,t.mul a.2 b.2)
  assoc a b c := Prod.ext (r.assoc a.1 b.1 c.1) (t.assoc a.2 b.2 c.2)
  left_id a := Prod.ext (r.left_id a.1) (t.left_id a.2)
  right_id a := Prod.ext (r.right_id a.1) (t.right_id a.2)
  mono hab hcd := ⟨r.mono hab.1 hcd.1,t.mono hab.2 hcd.2⟩
def vectorAdd : CostMonoid (Nat × Nat) := product natAdd natAdd
def mixed : CostMonoid (Nat × Nat) := product natAdd natMax
theorem nat_add_operation (a b : Nat) : natAdd.mul a b=a+b := rfl
theorem nat_max_operation (a b : Nat) : natMax.mul a b=max a b := rfl
theorem vector_operation (a b : Nat × Nat) :
    vectorAdd.mul a b=(a.1+b.1,a.2+b.2) := rfl
theorem mixed_operation (a b : Nat × Nat) :
    mixed.mul a b=(a.1+b.1,max a.2 b.2) := rfl
theorem grow {R : Type u} (r : CostMonoid R) (a c : R)
    (hc : r.order.le r.one c) : r.order.le a (r.mul a c) := by
  simpa only [r.right_id] using r.mono (r.order.refl a) hc
end OrderedCostsV21
