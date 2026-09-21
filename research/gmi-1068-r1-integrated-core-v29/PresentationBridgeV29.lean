import EvalKernelV29
import NamedTransportV29
namespace PresentationBridgeV29
open TypedPathsV11 ProcessMapsV26 BundledCategoryV19 BracketV25 EvalKernelV29
universe u v w
variable {O : Type u} (C : Category.{u,v} O) {G : O → O → Type w}
    (edge : {a b : O} → G a b → C.Hom a b) (gen : Generates C edge)
theorem lower_named : NamedTransportV29.Commutes (lowerMap C edge) :=
  NamedTransportV29.transport _ (lower_objects C edge)
theorem quote_named : NamedTransportV29.Commutes (quoteMap C edge gen) :=
  NamedTransportV29.transport _ (quote_objects C edge gen)
theorem quote_lower_bundle (a : Arrow (quotient C edge)) :
    (quoteMap C edge gen).bundle ((lowerMap C edge).bundle a) = a := by
  rcases a with ⟨a,b,f⟩
  change (⟨a,b,quote C edge gen (lower C edge f)⟩ : Arrow (quotient C edge)) = _
  rw [EvalKernelV29.quote_lower]
theorem lower_quote_bundle (a : Arrow C) :
    (lowerMap C edge).bundle ((quoteMap C edge gen).bundle a) = a := by
  rcases a with ⟨a,b,f⟩
  change (⟨a,b,lower C edge (quote C edge gen f)⟩ : Arrow C) = _
  rw [EvalKernelV29.lower_quote]
theorem quote_lower_tree (t : Tree O (Arrow (quotient C edge))) :
    (quoteMap C edge gen).tree ((lowerMap C edge).tree t) = t :=
  BracketV25.map_map id _ id _ (fun _ => rfl) (quote_lower_bundle C edge gen) t
theorem lower_quote_tree (t : Tree O (Arrow C)) :
    (lowerMap C edge).tree ((quoteMap C edge gen).tree t) = t :=
  BracketV25.map_map id _ id _ (fun _ => rfl) (lower_quote_bundle C edge gen) t
theorem inverse_observers (t : Tree O (Arrow (quotient C edge))) :
    NamedObserversV25.observer (CategoryTreesV25.named (quotient C edge)) t =
      (NamedObserversV25.observer (CategoryTreesV25.named C)
        ((lowerMap C edge).tree t)).map (quoteMap C edge gen).bundle := by
  rw [← quote_named C edge gen,quote_lower_tree]
end PresentationBridgeV29
