import ConstructorBindingsV29
import ControlBindingsV29
namespace ProofTargetsV29
open TypedPathsV11 BundledCategoryV19 BracketV25 EvalKernelV29
universe u v w x y z
theorem presentation_contract {O : Type u} (C : Category.{u,v} O)
    {G : O → O → Type w} (edge : {a b : O} → G a b → C.Hom a b)
    (gen : Generates C edge) :
    (lowerMap C edge).Faithful ∧
    NamedTransportV29.Commutes (lowerMap C edge) ∧
    NamedTransportV29.Commutes (quoteMap C edge gen) ∧
    (∀ t : Tree O (Arrow (quotient C edge)),
      (quoteMap C edge gen).tree ((lowerMap C edge).tree t) = t) ∧
    (∀ t : Tree O (Arrow C), (lowerMap C edge).tree ((quoteMap C edge gen).tree t) = t) :=
  ⟨lower_faithful C edge,PresentationBridgeV29.lower_named C edge,
    PresentationBridgeV29.quote_named C edge gen,
    PresentationBridgeV29.quote_lower_tree C edge gen,PresentationBridgeV29.lower_quote_tree C edge gen⟩
theorem fixed_encoder_contract {M : Type u} {Z : Type v} {Q : Type w} {R : Type x}
    {A : Type y} {B : Type z} (code : M → Z)
    (source : M → Q → Option A) (target : M → R → Option B)
    (i : Q → R) (j : A → B) (hj : ∀ a b, j a = j b → a = b)
    (square : ∀ m q, target m (i q) = (source m q).map j) :
    RecoverabilityV9.Recoverable code source ↔
      RecoverabilityV9.Recoverable code (FixedEncodersV29.pullback target i) :=
  FixedEncodersV29.recovery_iff code source target i j hj square
theorem guarded_restriction_contract {O : Type u} {L : Type w} {N : Type x}
    (C : Category.{u,v} O) (P : {a b : O} → C.Hom a b → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc C) P)
    (j : Arrow C → L) (hj : ∀ a b, j a = j b → a = b)
    (q : N → O) (t : Tree N L)
    (h : Valid (fun l => ∃ a, RestrictedAmbientV29.restrictedLabel C P closed j a = l)
      (fun _ => True) t) :
    NamedObserversV25.observer (RestrictedAmbientV29.fullNamed C j hj q) t =
      NamedObserversV25.observer (RestrictedAmbientV29.restrictedNamed C P closed j hj q) t :=
  RestrictedAmbientV29.guarded_transport C P closed j hj q t h
end ProofTargetsV29
