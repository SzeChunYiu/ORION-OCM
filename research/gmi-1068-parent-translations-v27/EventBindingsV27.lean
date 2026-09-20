import EventObservationsV27
import OptionalCategoriesV26
namespace EventBindingsV27
open StochasticV14 OrderedWeightsV27 SubEventsV27 FiniteOutcomesV27 EventTestsV27
universe u
variable {α : Type u} [Weight α] [OrderedWeight α]
theorem event_hom (n m : Nat) : (SubEventsV27.category α).Hom n m=Event α n m := rfl
theorem event_id (n : Nat) : ((SubEventsV27.category α).id n).value=mid n := rfl
theorem event_comp {n m k : Nat} (p : Event α n m) (q : Event α m k) :
    ((SubEventsV27.category α).comp p q).value=mcomp p.value q.value := rfl
theorem event_zero (n m : Nat) (x : Fin n) (y : Fin m) :
    (Event.zero (α:=α) n m).value x y=0 := rfl
theorem kernel_inclusion {n m : Nat} (p : Kernel α n m) :
    (SubEventsV27.inclusion.hom p).value=p.value := rfl
theorem to_kernel {n m : Nat} (p : Event α n m) (h : Normalized p.value) :
    (Event.toKernel p h).value=p.value := rfl
omit [OrderedWeight α] in
theorem sum_atom (n : Nat) (f : Fin n→α) : total (.atom n) f=sum f := rfl
omit [OrderedWeight α] in
theorem sum_product (I J : Shape) (f : Carrier I×Carrier J→α) :
    total (.product I J) f=total I (fun i=>total J (fun j=>f (i,j))) := rfl
theorem carrier_atom (n : Nat) : Carrier (.atom n)=Fin n := rfl
theorem carrier_product (I J : Shape) : Carrier (.product I J)=(Carrier I×Carrier J) := rfl
omit [OrderedWeight α] in
theorem aggregate_value {I : Shape} {n m : Nat} (p : Carrier I→Matrix α n m) (x : Fin n) (y : Fin m) :
    aggregate p x y=total I (fun i=>p i x y) := rfl
theorem component_value {I : Shape} {n m : Nat} (p : Test α I n m) (i : Carrier I) :
    (p.component i).value=p.value i := rfl
theorem prepare_value {n : Nat} (i : Fin n) (x : Fin 1) (y : Fin n) :
    (EventObservationsV27.prepare (α:=α) i).value x y=(if y=i then 1 else 0) := rfl
theorem effect_value {m : Nat} (j : Fin m) (x : Fin m) (y : Fin 1) :
    (EventObservationsV27.effect (α:=α) j).value x y=(if x=j then 1 else 0) := rfl
theorem scalar_value (a : α) (ha : a≤1) (x y : Fin 1) :
    (EventObservationsV27.scalar a ha).value x y=a := rfl
theorem nat_order (a b : Nat) : (@LE.le Nat natOrderedWeight.toLE a b) ↔ a≤b := Iff.rfl
omit [OrderedWeight α] in
theorem inherited_kernel_hom (n m : Nat) : (OptionalCategoriesV26.kernels α).Hom n m=Kernel α n m := rfl
omit [OrderedWeight α] in
theorem inherited_kernel_comp {n m k : Nat} (p : Kernel α n m) (q : Kernel α m k) :
    ((OptionalCategoriesV26.kernels α).comp p q).value=mcomp p.value q.value := rfl
omit [OrderedWeight α] in
theorem inherited_dirac {n m : Nat} (f : Fin n→Fin m) (i : Fin n) (j : Fin m) :
    ((OptionalCategoriesV26.dirac (α:=α)).hom f).value i j = (if j=f i then 1 else 0) := rfl
omit [OrderedWeight α] in
theorem inherited_support {n m : Nat} (p : Kernel α n m) (i : Fin n) (j : Fin m) :
    ((OptionalCategoriesV26.support (α:=α)).hom p).relates i j ↔ p.value i j≠0 := Iff.rfl
end EventBindingsV27
