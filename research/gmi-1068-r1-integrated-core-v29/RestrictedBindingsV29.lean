import RestrictedAmbientV29
namespace RestrictedBindingsV29
open TypedPathsV11 BundledCategoryV19
universe u v w x
variable {O : Type u} {L : Type w} {N : Type x} (C : Category.{u,v} O)
    (P : {a b : O} → C.Hom a b → Prop)
    (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc C) P)
    (j : Arrow C → L) (hj : ∀ a b, j a = j b → a = b) (q : N → O)
theorem label (a : Arrow (RestrictedV26.category C P closed)) :
    RestrictedAmbientV29.restrictedLabel C P closed j a =
      j ((RestrictedV26.inclusion C P closed).bundle a) := rfl
theorem full_named : RestrictedAmbientV29.fullNamed C j hj q = AmbientNamedV29.named C j hj q := rfl
theorem restricted_named :
    RestrictedAmbientV29.restrictedNamed C P closed j hj q =
      AmbientNamedV29.named (RestrictedV26.category C P closed)
        (RestrictedAmbientV29.restrictedLabel C P closed j)
        (RestrictedAmbientV29.restricted_injective C P closed j hj) q := rfl
theorem image_presented {A : Type u} {L : Type v} (j : A → L)
    (hj : ∀ a b, j a = j b → a = b) (P : PartialUnitsV19.Algebra A) :
    (ImageAlgebraV29.presented j hj P).algebra = ImageAlgebraV29.algebra j hj P := rfl
end RestrictedBindingsV29
