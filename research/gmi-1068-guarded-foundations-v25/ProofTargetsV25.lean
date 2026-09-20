import ConstructorBindingsV25
namespace ProofTargetsV25
open BracketV25 PresentedCoreV25
universe u v
theorem guarded_category_contract {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
    (t : Tree O (BundledCategoryV19.Arrow C)) :
    CategoryTreesV25.observer C t =
      fold (BundledCategoryV19.mul C) (flatten (BundledCategoryV19.identity C) t) :=
  CategoryTreesV25.guarded_flatten C t
theorem carrier_information_contract {M : Type u} {Z : Type v}
    (model : M → Presented L) (code : M → Z) :
    RecoverabilityV9.Recoverable code (fun m => RawObserversV25.observer (model m)) ↔
    RecoverabilityV9.Recoverable code (fun m => padded (model m)) :=
  RawObserversV25.observer_recovery model code
theorem bracket_loss_contract :
    LawControlsV25.bare CountermodelsV19.weakOnly
      (LawControlsV25.leftTree 0 1 2) = none ∧
    LawControlsV25.bare CountermodelsV19.weakOnly
      (LawControlsV25.rightTree 0 1 2) = some 2 :=
  LawControlsV25.weak_definedness_brackets
end ProofTargetsV25
