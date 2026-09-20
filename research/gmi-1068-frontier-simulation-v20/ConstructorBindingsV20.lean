import AttainedFrontierV20
import WellFoundedFrontierV20
import SimulationPruningV20
namespace ConstructorBindingsV20
open PartialContextV15 FrontierOrderV20 GuardedMapsV20 PartialPostcontextV20
open AttainedFrontierV20 WellFoundedFrontierV20 SimulationV20 SimulationPruningV20
universe u v w
theorem extend_empty {X : Type u} (r : PreorderSpec X) [DecidableRel r.le] (x : X) :
    extend r x []=x := rfl
theorem extend_cons {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (x a : X) (xs : List X) :
    extend r x (a::xs)=extend r (if r.le x a then a else x) xs := rfl
theorem frontier_definition {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) :
    frontier r xs=xs.filter (fun x => xs.all (fun y => decide (r.le x y → r.le y x))) := rfl
theorem values_definition {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (hs : List H) :
    values P k hs=hs.filterMap (valueMap P k) := rfl
theorem attained_frontier_definition {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) [DecidableRel k.order.le] (hs : List H) :
    attainedFrontier P k hs=frontier k.order (values P k hs) := rfl
theorem ascent_definition {X : Type u} (r : PreorderSpec X) (S : X → Prop)
    (x y : {x : X // S x}) :
    Ascent r S y x ↔ r.le x.val y.val ∧ ¬r.le y.val x.val := Iff.rfl
theorem guarded_definition {X : Type u} {Y : Type v} (r : PreorderSpec X)
    (s : PreorderSpec Y) (F : X → Option Y) :
    Guarded r s F ↔
      ∀ x x', r.le x x' → ∀ y, F x=some y → ∃ y', F x'=some y' ∧ s.le y y' := Iff.rfl
theorem composition_definition {X : Type u} {Y : Type v} {Z : Type w}
    (F : X → Option Y) (G : Y → Option Z) (x : X) :
    compose G F x=(F x).bind G := rfl
theorem post_order {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (s : PreorderSpec Z) :
    (post k F s).order=s := rfl
theorem run_empty {X : Type u} {A : Type v} (d : X → A → Option X) (x : X) :
    run d x []=some x := rfl
theorem run_cons {X : Type u} {A : Type v} (d : X → A → Option X)
    (x : X) (a : A) (word : List A) :
    run d x (a::word)=(d x a).bind (fun y => run d y word) := rfl
theorem simulation_definition {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (R : X → X → Prop) :
    Simulation b d R ↔
      ∀ x y, R x y → b.le x y ∧
        ∀ a x', d x a=some x' → ∃ y', d y a=some y' ∧ R x' y' := Iff.rfl
theorem greatest_union {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :
    Greatest b d x y ↔ ∃ R, Simulation b d R ∧ R x y := Iff.rfl
theorem simulation_order_relation {X : Type u} {A : Type v}
    (b : PreorderSpec X) (d : X → A → Option X) (x y : X) :
    (simulationOrder b d).le x y ↔ Greatest b d x y := Iff.rfl
theorem empty_word_attained {X : Type u} {A : Type v} {W : Type w}
    (d : X → A → Option X) (P : X → Prop) (k : Context X W)
    (S : X → Prop) (z : W) :
    WordAttained d P k [] S z ↔ Attained P k S z := by
  simp only [WordAttained,Attained,Image,run,Option.some.injEq]
  constructor
  · rintro ⟨x,⟨y,hy,hxy⟩,hp,he,hz⟩
    subst x
    exact ⟨y,hy,hp,he,hz⟩
  · rintro ⟨x,hx,hp,he,hz⟩
    exact ⟨x,⟨x,hx,rfl⟩,hp,he,hz⟩
theorem frontier_aliases {X : Type u} (r : PreorderSpec X) [DecidableRel r.le]
    (xs : List X) (x y : X) (hx : x ∈ frontier r xs)
    (hy : y ∈ xs) (hxy : r.le x y) :
    y ∈ frontier r xs := by
  obtain ⟨_,hm⟩ := (frontier_mem r xs x).mp hx
  apply (frontier_mem r xs y).mpr
  exact ⟨hy,fun z hz hyz => r.trans (hm z hz (r.trans hxy hyz)) hxy⟩
theorem outcome_illegal {W : Type v} {Z : Type w} (F : W → Option Z) :
    mapOutcome F (.illegal : Outcome W)=.illegal := rfl
theorem outcome_undefined {W : Type v} {Z : Type w} (F : W → Option Z) :
    mapOutcome F (.undefined : Outcome W)=.undefined := rfl
theorem outcome_value {W : Type v} {Z : Type w} (F : W → Option Z) (x : W) :
    mapOutcome F (.value x)=(match F x with | none => .undefined | some z => .value z) := rfl
end ConstructorBindingsV20
