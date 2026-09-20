import ConstructorBindingsV21
import ResourceControlsV21
namespace ProofTargetsV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open BudgetResidualV21 CumulativeV21 HistoryContextsV21 JointImagesV21 PathPositiveV21
universe u v w x y
theorem residual_contract {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (word : List A)
    (s t : S) (b remaining : Nat) :
    budgetEndpoint m cost s b word=some (t,remaining) ↔
      ∃ c, weighted natAdd m cost s word=some (t,c) ∧ c≤b ∧ remaining=b-c :=
  residual_iff m cost word s t b remaining
theorem joint_contract {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) (v : W) :
    Image (bounded m cost P H k b) v ↔ ∃ c, c≤b ∧ Joint m cost P H k c v :=
  joint_filtration m cost P H k b v
theorem prefix_final_contract {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    {R : Type y} (r : CostMonoid R) [DecidableRel r.order.le]
    (m : Machine S A O E) (cost : E → R) (word : List A)
    (s t : S) (spent capacity out : R) (positive : Nonnegative r m cost s word) :
    cumulative r m cost capacity s spent word=some (t,out) ↔
      ∃ c, weighted r m cost s word=some (t,c) ∧
        r.order.le (r.mul spent c) capacity ∧ out=r.mul spent c :=
  prefix_path_iff_final r m cost word s t spent capacity out positive
end ProofTargetsV21
