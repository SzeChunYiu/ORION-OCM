import AmbientFunctorV29
import RestrictedV26
namespace RestrictedAmbientV29
open TypedPathsV11 BundledCategoryV19 BracketV25 RestrictedV26
universe u v w x
variable {O : Type u} {L : Type w} {N : Type x} (C : Category.{u,v} O)
    (P : {a b : O} → C.Hom a b → Prop) (closed : FoundationV5.Closed (CategoryAdaptersV26.toProc C) P)
    (j : Arrow C → L) (hj : ∀ a b, j a = j b → a = b) (q : N → O)
def restrictedLabel (a : Arrow (category C P closed)) : L := j ((inclusion C P closed).bundle a)
include hj
theorem restricted_injective (a b : Arrow (category C P closed))
    (h : restrictedLabel C P closed j a = restrictedLabel C P closed j b) : a = b :=
  RestrictedV26.bundle_injective C P closed a b (hj _ _ h)
noncomputable def fullNamed := AmbientNamedV29.named C j hj q
noncomputable def restrictedNamed :=
  AmbientNamedV29.named (category C P closed) (restrictedLabel C P closed j)
    (restricted_injective C P closed j hj) q
theorem identity_same (n : N) :
    (restrictedNamed C P closed j hj q).identityMap n = (fullNamed C j hj q).identityMap n := rfl
theorem carrier_exact (l : L) :
    (restrictedNamed C P closed j hj q).presented.carrier l ↔
      ∃ a b, ∃ f : C.Hom a b, P f ∧ j ⟨a,b,f⟩ = l := by
  change (∃ a : Arrow (category C P closed), restrictedLabel C P closed j a = l) ↔ _
  constructor
  · rintro ⟨⟨a,b,f⟩,h⟩
    exact ⟨a,b,f.val,f.property,h⟩
  · rintro ⟨a,b,f,hp,h⟩
    exact ⟨⟨a,b,⟨f,hp⟩⟩,h⟩
theorem guarded_transport (t : Tree N L)
    (h : Valid (fun l => ∃ a, restrictedLabel C P closed j a = l) (fun _ => True) t) :
    NamedObserversV25.observer (fullNamed C j hj q) t =
      NamedObserversV25.observer (restrictedNamed C P closed j hj q) t :=
  AmbientFunctorV29.guarded (inclusion C P closed) (object_injective C P closed)
    j hj (restrictedLabel C P closed j) (restricted_injective C P closed j hj)
    (fun _ => rfl) q t h
theorem removed_arrow (a b : O) (f : C.Hom a b) (hp : ¬P f) :
    NamedObserversV25.observer (restrictedNamed C P closed j hj q) (.arrow (j ⟨a,b,f⟩)) = none ∧
    NamedObserversV25.observer (fullNamed C j hj q) (.arrow (j ⟨a,b,f⟩)) = some (j ⟨a,b,f⟩) := by
  constructor
  · apply AmbientNamedV29.absent
    rintro ⟨⟨c,d,g⟩,h⟩
    have he := hj _ _ h
    change (⟨c,d,g.val⟩ : Arrow C) = ⟨a,b,f⟩ at he
    have ha := congrArg Sigma.fst he
    have hb := congrArg (fun t : Arrow C => t.2.1) he
    dsimp at ha hb
    subst c
    subst d
    have hf := eq_of_heq (Sigma.mk.inj (eq_of_heq (Sigma.mk.inj he).2)).2
    exact hp (hf ▸ g.property)
  · classical
    simp [fullNamed,NamedObserversV25.arrow,AmbientNamedV29.carrier]
end RestrictedAmbientV29
