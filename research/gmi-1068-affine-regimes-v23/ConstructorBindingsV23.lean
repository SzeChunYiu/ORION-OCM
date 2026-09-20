import AffineControlsV23
namespace ConstructorBindingsV23
open ScalarV12 AffineArithmeticV23 PartialContextV15 ContextMapsV17 FrontierOrderV20
open AffineContextsV23 AffineWinnersV23 FiniteWinnersV23
universe u v
variable {I : Type u} {α : Type v} [Scalar α]
theorem affine_binding (a b t : α) : affine a b t=a+b*t := rfl
theorem lerp_binding (s x y : α) : lerp s x y=(1 + -s)*x+s*y := rfl
theorem score_binding (a b : I→α) (t : α) (i : I) : score a b t i=a i+b i*t := rfl
theorem active_binding (P E : I→Prop) (i : I) : active P E i ↔ P i∧E i := Iff.rfl
theorem value_order_binding (x y : I×α) : valueOrder.le x y ↔ y.2≤x.2 := Iff.rfl
theorem coded_order_binding (a b : I→α) (t : α) (i j : I) :
    (codedOrder a b t).le i j ↔ score a b t j≤score a b t i := Iff.rfl
theorem context_domain (E : I→Prop) (a b : I→α) (t : α) :
    (context E a b t).defined=E := rfl
theorem context_eval (E : I→Prop) (a b : I→α) (t : α) (i : I) (he : E i) :
    (context E a b t).eval ⟨i,he⟩=(i,score a b t i) := rfl
theorem context_order (E : I→Prop) (a b : I→α) (t : α) :
    (context E a b t).order=valueOrder := rfl
theorem code_domain (E : I→Prop) (a b : I→α) (t : α) :
    (codedContext E a b t).defined=E := rfl
theorem code_eval (E : I→Prop) (a b : I→α) (t : α) (i : I) (he : E i) :
    (codedContext E a b t).eval ⟨i,he⟩=i := rfl
theorem code_order (E : I→Prop) (a b : I→α) (t : α) :
    (codedContext E a b t).order=codedOrder a b t := rfl
theorem decoder_binding (a b : I→α) (t : α) (i : I) :
    decode a b t i=(i,score a b t i) := rfl
theorem image_binding {W : Type v} (P : I→Prop) (k : Context I W) (w : W) :
    Image P k w ↔ ∃i,P i∧∃he:k.defined i,k.eval ⟨i,he⟩=w := by
  simp only [Image,PartialPostcontextV20.Attained,true_and]
theorem winner_binding (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    Winner P E a b t i ↔ active P E i∧∀j,active P E j→score a b t i≤score a b t j := Iff.rfl
theorem unique_binding (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    UniqueWinner P E a b t i ↔ Winner P E a b t i∧∀j,Winner P E a b t j→j=i := Iff.rfl
theorem strict_binding (P E : I→Prop) (a b : I→α) (t : α) (i : I) :
    StrictWinner P E a b t i ↔
      active P E i∧∀j,active P E j→j≠i→score a b t i<score a b t j := Iff.rfl
theorem active_list_binding (P E : I→Prop) (xs : List I) :
    activeList P E xs=xs.filter (fun i => @decide (active P E i) (Classical.propDecidable _)) := rfl
theorem winner_list_binding (P E : I→Prop) (a b : I→α) (t : α) (xs : List I) :
    winnerList P E a b t xs=@frontier _ (codedOrder a b t)
      (fun _ _ => Classical.propDecidable _) (activeList P E xs) := rfl
theorem observation_illegal (P E : I→Prop) (a b : I→α) (t : α) (i : I) (h : ¬P i) :
    observe P (context E a b t) i=.illegal := observe_illegal P _ i h
theorem observation_undefined (P E : I→Prop) (a b : I→α) (t : α) (i : I)
    (hp : P i) (he : ¬E i) :
    observe P (context E a b t) i=.undefined := observe_undefined P _ i hp he
theorem observation_value (P E : I→Prop) (a b : I→α) (t : α) (i : I)
    (hp : P i) (he : E i) :
    observe P (context E a b t) i=.value (decode a b t i) := observe_value P _ i hp he
end ConstructorBindingsV23
