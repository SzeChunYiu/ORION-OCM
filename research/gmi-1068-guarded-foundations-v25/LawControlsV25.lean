import CarrierControlsV25
namespace LawControlsV25
open BracketV25 PartialUnitsV19 CountermodelsV19 InformationControlsV19
def leftTree (a b c : A) : Tree Unit A :=
  .seq (.seq (.arrow a) (.arrow b)) (.arrow c)
def rightTree (a b c : A) : Tree Unit A :=
  .seq (.arrow a) (.seq (.arrow b) (.arrow c))
def bare (m : A → A → Option A) : Tree Unit A → Option A :=
  eval m some (fun _ => none)
theorem left_response (m : A → A → Option A) (a b c : A) :
    bare m (leftTree a b c) = (m a b).bind (fun x => m x c) := by
  simp [bare,leftTree,eval]
theorem right_response (m : A → A → Option A) (a b c : A) :
    bare m (rightTree a b c) = (m b c).bind (fun x => m a x) := rfl
theorem nonassoc_brackets :
    bare (fun x y => some (nonassoc x y)) (leftTree 1 1 2) = some 2 ∧
    bare (fun x y => some (nonassoc x y)) (rightTree 1 1 2) = some 1 := by
  decide
theorem weak_definedness_brackets :
    bare weakOnly (leftTree 0 1 2) = none ∧
    bare weakOnly (rightTree 0 1 2) = some 2 := by decide
theorem equal_flatten_different_response :
    flatten (fun _ : Unit => (0 : Fin 3)) (leftTree 1 1 2) =
      flatten (fun _ : Unit => (0 : Fin 3)) (rightTree 1 1 2) ∧
    bare (fun x y => some (nonassoc x y)) (leftTree 1 1 2) ≠
      bare (fun x y => some (nonassoc x y)) (rightTree 1 1 2) := by decide
theorem coherence_matching_failure :
    incoherent true false = some true ∧ incoherent false true = some true ∧
    incoherent true true = none ∧ IsUnit incoherent false := by
  unfold IsUnit
  decide
theorem constant_unit_failure :
    OptionFoldV25.Strong (fun x y => some (RecoverabilityV9.constantMul x y)) ∧
    (∀ e, ¬IsUnit (fun x y => some (RecoverabilityV9.constantMul x y)) e) ∧
    eval (fun x y => some (RecoverabilityV9.constantMul x y)) some
      (fun _ : Unit => some false) (.seq (.empty ()) (.arrow true)) = some false := by
  unfold OptionFoldV25.Strong IsUnit
  decide
theorem designated_insertion_changes :
    eval (fun x y => some (leftProjection x y)) some
      (fun _ : Unit => some false) (.seq (.empty ()) (.arrow true)) = some false ∧
    eval (fun x y => some (rightProjection x y)) some
      (fun _ : Unit => some false) (.seq (.arrow true) (.empty ())) = some false := by decide
theorem composition_response_loss :
    RawObserversV25.observer (PresentedUnitsV25.full (liftedAlgebra GroupLawsV16.c4))
      (.seq (.arrow .one) (.arrow .one)) = some .two ∧
    RawObserversV25.observer (PresentedUnitsV25.full (liftedAlgebra GroupLawsV16.v4))
      (.seq (.arrow .one) (.arrow .one)) = some .zero := by
  rw [RawObserversV25.pair,RawObserversV25.pair,
    PresentedUnitsV25.full_padded,PresentedUnitsV25.full_padded]
  exact c4_v4_different_products
theorem failure_tag_response_loss :
    RawObserversV25.observer (PresentedUnitsV25.full discreteAlgebra)
      (.seq (.arrow false) (.arrow true)) = none ∧
    RawObserversV25.observer (PresentedUnitsV25.full joinAlgebra)
      (.seq (.arrow false) (.arrow true)) = some true := by
  rw [RawObserversV25.pair,RawObserversV25.pair,
    PresentedUnitsV25.full_padded,PresentedUnitsV25.full_padded]
  exact default_collision.2
def eraseAnchors : Tree O A → List A
  | .arrow a => [a]
  | .empty _ => []
  | .seq l r => eraseAnchors l ++ eraseAnchors r
theorem naive_empty_loss :
    eraseAnchors (.seq (.empty false) (.empty true) : Tree Bool Bool) =
      eraseAnchors (.seq (.empty false) (.empty false) : Tree Bool Bool) ∧
    RawObserversV25.observer (CarrierControlsV25.supported (fun _ : Bool => True))
      (.seq (.empty false) (.empty true)) ≠
    RawObserversV25.observer (CarrierControlsV25.supported (fun _ : Bool => True))
      (.seq (.empty false) (.empty false)) := by
  constructor
  · rfl
  · rw [CarrierControlsV25.anchored_empty.1,CarrierControlsV25.anchored_empty.2]
    exact Option.noConfusion
end LawControlsV25
