import ConstructorBindingsV26
import OptionalBindingsV26
namespace ProofTargetsV26
open ProcessMapsV26 TypedPathsV11 BracketV25
universe u v w x
theorem raw_transport_contract {O : Type u} {P : Type w}
    {C : Category.{u,v} O} {D : Category.{w,x} P} (F : ProcessMap C D) :
    RawTransportV26.TreesCommute F ↔ F.ObjectInjective :=
  (RawTransportV26.sharp_equivalence F).2
theorem restricted_history_contract {O : Type u} (C : Category.{u,v} O)
    (P : {a b : O} → C.Hom a b → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc C) P)
    (t : Tree O (BundledCategoryV19.Arrow (RestrictedV26.category C P closed))) :
    CategoryTreesV25.observer C ((RestrictedV26.inclusion C P closed).tree t) =
      (CategoryTreesV25.observer (RestrictedV26.category C P closed) t).map
        (RestrictedV26.inclusion C P closed).bundle :=
  RestrictedV26.tree_transport C P closed t
theorem resource_lift_contract {O : Type u} (C : Category.{u,v} O)
    (cost : {a b : O} → C.Hom a b → Nat)
    (id0 : ∀ a, cost (C.id a) = 0)
    (add : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c), cost (C.comp f g) = cost f + cost g)
    {a b : O} (p : Path C.Hom a b) (r : Nat) :
    (∃ s, ∃ q : Path (ResourceCategoryV26.category C cost id0 add).Hom (a,r) (b,s),
      (ResourceCategoryV26.projection C cost id0 add).path q = p) ↔
        ResourceCategoryV26.pathCost C cost p ≤ r :=
  ResourcePathsV26.lift_iff C cost id0 add p r
end ProofTargetsV26
