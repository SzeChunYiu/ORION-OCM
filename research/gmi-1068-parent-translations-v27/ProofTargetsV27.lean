import ParentBindingsV27
import EventBindingsV27
import TaskBindingsV27
import ResourceControlsV26
namespace ProofTargetsV27
open LTSCoalgebraV27 StochasticV14 FiniteOutcomesV27 EventTestsV27 TaskInterfacesV27
universe u v w
theorem hom_equation_contract {S : Type u} {T : Type w} {A : Type v}
    (r : LTS S A) (q : LTS T A) (f : S→T) :
    HomEquation r q f ↔ Forward r q f ∧ Back r q f := hom_iff r q f
theorem test_composition_contract {α : Type u} [Weight α] {I J : Shape} {n m k : Nat}
    (p : Test α I n m) (q : Test α J m k) :
    (∀i j x z,(p.comp q).value (i,j) x z=sum (fun y=>p.value i x y*q.value j y z)) ∧
    aggregate (p.comp q).value=mcomp (aggregate p.value) (aggregate q.value) ∧
    Normalized (aggregate (p.comp q).value) :=
  ⟨Test.comp_value p q,Test.comp_aggregate p q,(p.comp q).aggregate_normalized⟩
theorem regular_task_contract {X : Type u} (r s : RelParentV27.Rel X X)
    (h : RegularTasksV27.Regular r s) :
    decode (RegularTasksV27.regularTask r s h)=RelParentV27.comp r s ∧
    ∀x,Dom (decode (RegularTasksV27.regularTask r s h)) x ↔ Dom r x :=
  ⟨RegularTasksV27.decode_regular r s h,RegularTasksV27.regular_domain r s h⟩
end ProofTargetsV27
