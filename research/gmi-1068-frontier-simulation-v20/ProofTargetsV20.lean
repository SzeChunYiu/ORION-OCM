import ConstructorBindingsV20
namespace ProofTargetsV20
open PartialContextV15 FrontierOrderV20 GuardedMapsV20 SimulationV20
universe u v
theorem frontier_cofinal_contract {X : Type u} (r : PreorderSpec X)
    [DecidableRel r.le] (xs : List X) :
    Cofinal r (fun x => x ∈ frontier r xs) (fun x => x ∈ xs) :=
  frontier_cofinal r xs
theorem guarded_iff_contract {X : Type u} {Y : Type v}
    (r : PreorderSpec X) (s : PreorderSpec Y) (F : X → Option Y) :
    Guarded r s F ↔ FinitePreserves r s F :=
  guarded_iff_finite_preserves r s F
theorem greatest_words_contract {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :
    Greatest b d x y ↔ WordRelation b d x y :=
  greatest_iff_words b d x y
end ProofTargetsV20
