import OrderedWeightsV27
import ProcessMapsV26
namespace SubEventsV27
open StochasticV14 OrderedWeightsV27 TypedPathsV11 ProcessMapsV26
universe u
variable {α : Type u} [Weight α] [OrderedWeight α]
structure Event (α : Type u) [Weight α] [OrderedWeight α] (n m : Nat) where
  value : Matrix α n m
  bounded : ∀ i,sum (value i)≤1
namespace Event
@[ext] theorem ext {n m : Nat} {p q : Event α n m} (h : p.value=q.value) : p=q := by
  cases p; cases q; cases h; rfl
def comp {n m k : Nat} (p : Event α n m) (q : Event α m k) : Event α n k :=
  ⟨mcomp p.value q.value,comp_bound _ _ p.bounded q.bounded⟩
def fromKernel {n m : Nat} (p : Kernel α n m) : Event α n m :=
  ⟨p.value,fun i => by rw [p.normalized]; exact OrderedWeight.refl _⟩
def ident (n : Nat) : Event α n n := fromKernel (Kernel.ident n)
def zero (n m : Nat) : Event α n m :=
  ⟨fun _ _ => 0,fun _ => by rw [sum_zero]; exact OrderedWeight.zero_le _⟩
def toKernel {n m : Nat} (p : Event α n m) (h : Normalized p.value) : Kernel α n m :=
  ⟨p.value,h⟩
theorem kernel_roundtrip {n m : Nat} (p : Kernel α n m) :
    toKernel (fromKernel p) p.normalized=p := rfl
theorem event_roundtrip {n m : Nat} (p : Event α n m) (h : Normalized p.value) :
    fromKernel (toKernel p h)=p := ext rfl
theorem fromKernel_injective {n m : Nat} {p q : Kernel α n m}
    (h : fromKernel p=fromKernel q) : p=q := Kernel.ext (congrArg Event.value h)
theorem assoc {n m k l : Nat} (p : Event α n m) (q : Event α m k) (r : Event α k l) :
    comp (comp p q) r=comp p (comp q r) := ext (mcomp_assoc _ _ _)
theorem left_id {n m : Nat} (p : Event α n m) : comp (ident n) p=p := ext (mid_left _)
theorem right_id {n m : Nat} (p : Event α n m) : comp p (ident m)=p := ext (mid_right _)
end Event
def category (α : Type u) [Weight α] [OrderedWeight α] : Category Nat where
  Hom := Event α
  id := Event.ident
  comp := Event.comp
  assoc := Event.assoc
  left_id := Event.left_id
  right_id := Event.right_id
def kernels (α : Type u) [Weight α] : Category Nat where
  Hom := Kernel α
  id := Kernel.ident
  comp := Kernel.comp
  assoc := Kernel.assoc
  left_id := Kernel.left_id
  right_id := Kernel.right_id
def inclusion : ProcessMap (kernels α) (category α) where
  obj := id
  hom := Event.fromKernel
  id_law _ := rfl
  comp_law _ _ := Event.ext rfl
theorem inclusion_faithful : (inclusion (α:=α)).Faithful :=
  by
  intro n m p q h
  exact Event.fromKernel_injective h
theorem zero_into_empty (n : Nat) : ∃ p : Event α n 0, ∀ i,sum (p.value i)=0 :=
  ⟨Event.zero n 0,fun _ => rfl⟩
end SubEventsV27
