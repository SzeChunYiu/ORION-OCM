import RawTransportV26
namespace FunctorControlsV26
open TypedPathsV11 ProcessMapsV26 BundledCategoryV19
def indiscrete (O : Type u) : Category O where
  Hom _ _ := Unit
  id _ := ()
  comp _ _ := ()
  assoc _ _ _ := rfl
  left_id f := by cases f; rfl
  right_id f := by cases f; rfl
def collapse : ProcessMap (indiscrete Bool) (indiscrete Unit) where
  obj _ := ()
  hom _ := ()
  id_law _ := rfl
  comp_law _ _ := rfl
def sectionMap : ProcessMap (indiscrete Unit) (indiscrete Bool) where
  obj _ := false
  hom _ := ()
  id_law _ := rfl
  comp_law _ _ := rfl
theorem collapse_faithful : collapse.Faithful := by
  intro a b f g _
  cases f; cases g; rfl
theorem collapse_full (a b : Bool) (f : (indiscrete Unit).Hom (collapse.obj a) (collapse.obj b)) :
    ∃ g : (indiscrete Bool).Hom a b, collapse.hom g = f := by
  cases f
  exact ⟨(),rfl⟩
def equivalenceTo (a : Bool) : (indiscrete Bool).Hom (sectionMap.obj (collapse.obj a)) a := ()
def equivalenceFrom (a : Bool) : (indiscrete Bool).Hom a (sectionMap.obj (collapse.obj a)) := ()
theorem equivalence_inverse (a : Bool) :
    (indiscrete Bool).comp (equivalenceTo a) (equivalenceFrom a) =
      (indiscrete Bool).id (sectionMap.obj (collapse.obj a)) ∧
    (indiscrete Bool).comp (equivalenceFrom a) (equivalenceTo a) =
      (indiscrete Bool).id a := ⟨rfl,rfl⟩
theorem equivalence_natural {a b : Bool} (f : (indiscrete Bool).Hom a b) :
    (indiscrete Bool).comp (sectionMap.hom (collapse.hom f)) (equivalenceTo b) =
    (indiscrete Bool).comp (equivalenceTo a) f := rfl
theorem collapsed_anchors :
    CategoryTreesV25.observer (indiscrete Bool) (.seq (.empty false) (.empty true)) = none ∧
    CategoryTreesV25.observer (indiscrete Unit)
      (collapse.tree (.seq (.empty false) (.empty true))) =
      some (identity (indiscrete Unit) ()) :=
  RawTransportV26.collapsed_empty_witness collapse false true (by decide) rfl
def bitGroup : Category Unit where
  Hom _ _ := Bool
  id _ := false
  comp f g := Bool.xor f g
  assoc := by intro _ _ _ _ f g h; cases f <;> cases g <;> cases h <;> rfl
  left_id f := by cases f <;> rfl
  right_id f := by cases f <;> rfl
def eraseGroup : ProcessMap bitGroup (indiscrete Unit) where
  obj := id
  hom _ := ()
  id_law _ := rfl
  comp_law _ _ := rfl
theorem group_object_injective : eraseGroup.ObjectInjective := fun _ _ h => h
theorem group_transport : RawTransportV26.TreesCommute eraseGroup :=
  RawTransportV26.trees_of_injective eraseGroup group_object_injective
theorem group_output_loss :
    eraseGroup.bundle (⟨(),(),false⟩ : Arrow bitGroup) =
      eraseGroup.bundle (⟨(),(),true⟩ : Arrow bitGroup) ∧
    (⟨(),(),false⟩ : Arrow bitGroup) ≠ ⟨(),(),true⟩ := by
  constructor
  · rfl
  · intro h
    have hh := eq_of_heq (Sigma.mk.inj (eq_of_heq (Sigma.mk.inj h).2)).2
    cases hh
end FunctorControlsV26
