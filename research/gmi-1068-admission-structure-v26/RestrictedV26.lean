import RawTransportV26
namespace RestrictedV26
open CategoryAdaptersV26 ProcessMapsV26 BundledCategoryV19 BracketV25
universe u v
variable {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
    (P : {a b : O} → C.Hom a b → Prop) (closed : FoundationV5.Closed (toProc C) P)
def category : TypedPathsV11.Category O :=
  fromProc (FoundationV5.restrictedCategory (toProc C) P closed)
def inclusion : ProcessMap (category C P closed) C where
  obj := id
  hom := Subtype.val
  id_law _ := rfl
  comp_law _ _ := rfl
theorem hom_binding (a b : O) :
    (category C P closed).Hom a b = {f : C.Hom a b // P f} := rfl
theorem id_binding (a : O) :
    ((category C P closed).id a).val = C.id a := rfl
theorem comp_binding {a b c : O}
    (f : (category C P closed).Hom a b) (g : (category C P closed).Hom b c) :
    ((category C P closed).comp f g).val = C.comp f.val g.val := rfl
theorem object_injective : (inclusion C P closed).ObjectInjective := fun _ _ h => h
theorem faithful : (inclusion C P closed).Faithful := fun _ _ h => Subtype.ext h
theorem bundle_binding (a b : O) (f : (category C P closed).Hom a b) :
    (inclusion C P closed).bundle ⟨a,b,f⟩ = ⟨a,b,f.val⟩ := rfl
theorem bundle_injective (a b : Arrow (category C P closed))
    (h : (inclusion C P closed).bundle a = (inclusion C P closed).bundle b) : a = b :=
  (inclusion C P closed).bundle_injective (object_injective C P closed) (faithful C P closed) a b h
theorem product_transport (a b : Arrow (category C P closed)) :
    mul C ((inclusion C P closed).bundle a) ((inclusion C P closed).bundle b) =
      (mul (category C P closed) a b).map (inclusion C P closed).bundle :=
  (inclusion C P closed).product_commutes (object_injective C P closed) a b
theorem tree_transport (t : Tree O (Arrow (category C P closed))) :
    CategoryTreesV25.observer C ((inclusion C P closed).tree t) =
      (CategoryTreesV25.observer (category C P closed) t).map (inclusion C P closed).bundle :=
  RawTransportV26.trees_of_injective _ (object_injective C P closed) t
theorem failure_reflection (t : Tree O (Arrow (category C P closed))) :
    CategoryTreesV25.observer C ((inclusion C P closed).tree t) = none ↔
      CategoryTreesV25.observer (category C P closed) t = none :=
  RawTransportV26.none_iff _ (object_injective C P closed) t
theorem output_reflection (s t : Tree O (Arrow (category C P closed))) :
    CategoryTreesV25.observer C ((inclusion C P closed).tree s) =
      CategoryTreesV25.observer C ((inclusion C P closed).tree t) ↔
    CategoryTreesV25.observer (category C P closed) s =
      CategoryTreesV25.observer (category C P closed) t :=
  RawTransportV26.output_reflection _ (object_injective C P closed) (faithful C P closed) s t
theorem arrow_lift_iff (a b : O) (f : C.Hom a b) :
    (∃ g : (category C P closed).Hom a b, g.val = f) ↔ P f := by
  constructor
  · rintro ⟨g,rfl⟩; exact g.property
  · intro h; exact ⟨⟨f,h⟩,rfl⟩
theorem no_spurious_unit (x : Arrow (category C P closed))
    (hx : PartialUnitsV19.IsUnit (mul (category C P closed)) x) :
    ∃ a, (inclusion C P closed).bundle x = identity C a := by
  obtain ⟨a,ha⟩ := (unit_iff_identity (category C P closed) x).mp hx
  exact ⟨a,ha ▸ (inclusion C P closed).bundle_identity a⟩
theorem path_transport {a b : O} (p : TypedPathsV11.Path (category C P closed).Hom a b) :
    TypedPathsV11.eval C id (fun f => f) ((inclusion C P closed).path p) =
    (TypedPathsV11.eval (category C P closed) id (fun f => f) p).val :=
  (inclusion C P closed).path_eval p
theorem exact_closure :
    Nonempty (FoundationV5.RestrictedOperations (toProc C) P) ↔ FoundationV5.Closed (toProc C) P :=
  FoundationV5.restricted_operations_iff_closed (toProc C) P
end RestrictedV26
