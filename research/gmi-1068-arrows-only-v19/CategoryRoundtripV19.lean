import ArrowRoundtripV19
namespace CategoryRoundtripV19
open PartialUnitsV19
universe u v
variable {V : Type u} (C : TypedPathsV11.Category.{u,v} V)
noncomputable abbrev P := BundledCategoryV19.algebra C
noncomputable abbrev Rebuilt := ReconstructedV19.category (P C)
def objectForward (a : V) : (P C).Unit :=
  ⟨BundledCategoryV19.identity C a, BundledCategoryV19.identity_unit C a⟩
def objectBackward (e : (P C).Unit) : V := e.val.1
theorem object_backward_forward (a : V) :
    objectBackward C (objectForward C a) = a := rfl
theorem object_forward_backward (e : (P C).Unit) :
    objectForward C (objectBackward C e) = e := by
  apply Subtype.ext
  obtain ⟨a,ha⟩ := (BundledCategoryV19.unit_iff_identity C e.val).mp e.property
  change BundledCategoryV19.identity C e.val.1 = e.val
  rw [ha]
  rfl
theorem object_injective {a b : V} (h : objectForward C a = objectForward C b) : a = b :=
  congrArg (objectBackward C) h
theorem object_surjective (e : (P C).Unit) : ∃ a, objectForward C a = e :=
  ⟨objectBackward C e, object_forward_backward C e⟩
noncomputable def homForward {a b : V} (f : C.Hom a b) :
    (Rebuilt C).Hom (objectForward C a) (objectForward C b) :=
  ⟨⟨a,b,f⟩, Subtype.ext (BundledCategoryV19.left_binding C _),
    Subtype.ext (BundledCategoryV19.right_binding C _)⟩
theorem object_value (a : V) : (objectForward C a).val = BundledCategoryV19.identity C a := rfl
theorem hom_forward_value {a b : V} (f : C.Hom a b) :
    (homForward C f).val = ⟨a,b,f⟩ := rfl
theorem hom_source {a b : V}
    (f : (Rebuilt C).Hom (objectForward C a) (objectForward C b)) : f.val.1 = a := by
  have h := congrArg Subtype.val f.property.1
  rw [BundledCategoryV19.left_binding] at h
  exact congrArg Sigma.fst h
theorem hom_target {a b : V}
    (f : (Rebuilt C).Hom (objectForward C a) (objectForward C b)) : f.val.2.1 = b := by
  have h := congrArg Subtype.val f.property.2
  rw [BundledCategoryV19.right_binding] at h
  exact congrArg Sigma.fst h
noncomputable def homBackward {a b : V}
    (f : (Rebuilt C).Hom (objectForward C a) (objectForward C b)) : C.Hom a b :=
  cast (congrArg (fun p : V × V => C.Hom p.1 p.2)
    (show (f.val.1,f.val.2.1) = (a,b) from
      Prod.ext (hom_source C f) (hom_target C f))) f.val.2.2
theorem hom_backward_forward {a b : V} (f : C.Hom a b) :
    homBackward C (homForward C f) = f := rfl
theorem hom_forward_backward {a b : V}
    (f : (Rebuilt C).Hom (objectForward C a) (objectForward C b)) :
    homForward C (homBackward C f) = f := by
  have hs := hom_source C f
  have ht := hom_target C f
  rcases f with ⟨⟨c,d,g⟩,hl,hr⟩
  dsimp at hs ht
  subst c; subst d
  rfl
theorem hom_forward_injective {a b : V} {f g : C.Hom a b}
    (h : homForward C f = homForward C g) : f = g :=
  (hom_backward_forward C f).symm.trans ((congrArg (homBackward C) h).trans
    (hom_backward_forward C g))
theorem forward_identity (a : V) :
    homForward C (C.id a) = (Rebuilt C).id (objectForward C a) := by
  apply Subtype.ext
  rfl
theorem forward_comp {a b c : V} (f : C.Hom a b) (g : C.Hom b c) :
    homForward C (C.comp f g) = (Rebuilt C).comp (homForward C f) (homForward C g) := by
  apply Subtype.ext
  exact (ReconstructedV19.compose_value (P C) (homForward C f) (homForward C g)
    (BundledCategoryV19.aligned C f g)).symm
theorem backward_identity (a : V) :
    homBackward C ((Rebuilt C).id (objectForward C a)) = C.id a := by
  rw [← forward_identity,hom_backward_forward]
theorem backward_comp {a b c : V}
    (f : (Rebuilt C).Hom (objectForward C a) (objectForward C b))
    (g : (Rebuilt C).Hom (objectForward C b) (objectForward C c)) :
    homBackward C ((Rebuilt C).comp f g) = C.comp (homBackward C f) (homBackward C g) := by
  apply hom_forward_injective C
  rw [hom_forward_backward,forward_comp,hom_forward_backward,hom_forward_backward]
end CategoryRoundtripV19
