import HistoryUnionsV21
import CapabilityThresholdV21
import PathPositiveV21
namespace ConstructorBindingsV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open BudgetResidualV21 CumulativeV21 HistoryContextsV21 JointImagesV21
open HistoryUnionsV21 PathPositiveV21
universe u v w x y
theorem endpoint_empty {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (s : S) : endpoint m s []=some s := rfl
theorem endpoint_cons {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (s : S) (a : A) (word : List A) :
    endpoint m s (a::word)=(m.next s a).bind (fun (_,t) => endpoint m t word) := rfl
theorem budget_actual {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (s : S) (b : Nat) (word : List A) :
    budgetEndpoint m cost s b word=endpoint (budgetMachine m cost) (s,b) word := rfl
theorem cumulative_cons {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) [DecidableRel r.order.le] (m : Machine S A O E)
    (cost : E → R) (b spent : R) (s : S) (a : A) (word : List A) :
    cumulative r m cost b s spent (a::word)=
      if r.order.le spent b then (m.next s a).bind (fun (e,t) =>
        cumulative r m cost b t (r.mul spent (cost e)) word) else none := rfl
theorem nonnegative_cons {S : Type u} {A : Type v} {O : Type w} {E : Type x} {R : Type y}
    (r : CostMonoid R) (m : Machine S A O E) (cost : E → R)
    (s : S) (a : A) (word : List A) :
    Nonnegative r m cost s (a::word) ↔
      ∀ e t, m.next s a=some (e,t) →
        r.order.le r.one (cost e) ∧ Nonnegative r m cost t word := Iff.rfl
theorem unrestricted_admission {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (h : History S A) :
    (unrestricted m cost P H k).admission h ↔
      P h ∧ H h ∧ ∃ t c, weighted natAdd m cost h.1 h.2=some (t,c) := Iff.rfl
theorem bounded_admission {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) (h : History S A) :
    (bounded m cost P H k b).admission h ↔
      P h ∧ H h ∧ ∃ t c, weighted natAdd m cost h.1 h.2=some (t,c) ∧ c≤b := Iff.rfl
theorem bounded_active {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) (h : History S A) :
    (relativeDomain (bounded m cost P H k b).admission k).defined h ↔
      (P h ∧ H h ∧ Within m cost b h) ∧ k.defined h := Iff.rfl
theorem view_definition {H : Type u} {W : Type v} (sc : Scenario H W) (h : H) :
    view sc h=observe sc.admission sc.context h := rfl
theorem joint_definition {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (c : Nat) (v : W) :
    Joint m cost P H k c v ↔
      ∃ h, P h ∧ H h ∧ ∃ t, weighted natAdd m cost h.1 h.2=some (t,c) ∧
        ∃ he : k.defined h, k.eval ⟨h,he⟩=v := Iff.rfl
theorem target_cost_definition {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (c : Nat) :
    TargetCosts m cost P H k G c ↔ ∃ v, Joint m cost P H k c v ∧ G v := Iff.rfl
theorem projection_domain {H : Type u} {W : Type v} {R : Type w}
    (k : Context H W) (rho : W → R) (r : PreorderSpec R) :
    (projectContext k rho r).defined=k.defined := rfl
theorem projection_evaluator {H : Type u} {W : Type v} {R : Type w}
    (k : Context H W) (rho : W → R) (r : PreorderSpec R)
    (h : {h : H // k.defined h}) :
    (projectContext k rho r).eval h=rho (k.eval h) := rfl
theorem projection_order {H : Type u} {W : Type v} {R : Type w}
    (k : Context H W) (rho : W → R) (r : PreorderSpec R) :
    (projectContext k rho r).order=r := rfl
theorem projection_admission {H : Type u} {W : Type v} {R : Type w}
    (sc : Scenario H W) (rho : W → R) (r : PreorderSpec R) :
    (projectScenario sc rho r).admission=sc.admission := rfl
theorem from_start_definition {S : Type u} {A : Type v} (s : S) (h : History S A) :
    fromStart s h ↔ h.1=s := Iff.rfl
theorem horizon_definition {S : Type u} {A : Type v}
    (H : History S A → Prop) (n : Nat) (h : History S A) :
    horizon H n h ↔ H h ∧ h.2.length≤n := Iff.rfl
theorem original_capability_bridge {H : Type u} {W : Type v}
    (sc : Scenario H W) (G : W → Prop) :
    TargetPossible (Image sc) G ↔ Capability sc G := Iff.rfl
theorem nat_cost_identity : natAdd.one=0 := rfl
theorem vector_cost_identity : vectorAdd.one=(0,0) := rfl
theorem mixed_cost_identity : mixed.one=(0,0) := rfl
end ConstructorBindingsV21
