import RawTransportV26
namespace NamedTransportV29
open TypedPathsV11 ProcessMapsV26 BundledCategoryV19 BracketV25
universe u v w x
variable {O : Type u} {P : Type w} {C : Category.{u,v} O} {D : Category.{w,x} P}
def Commutes (F : ProcessMap C D) : Prop :=
  ∀ t, NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree t) =
    (NamedObserversV25.observer (CategoryTreesV25.named C) t).map F.bundle
theorem sharp (F : ProcessMap C D) : Commutes F ↔ F.ObjectInjective := by
  simpa only [Commutes,CategoryTreesV25.named_observer,RawTransportV26.TreesCommute]
    using (RawTransportV26.sharp_equivalence F).2
theorem transport (F : ProcessMap C D) (hi : F.ObjectInjective) : Commutes F := (sharp F).mpr hi
theorem success (F : ProcessMap C D) (t : Tree O (Arrow C)) (a : Arrow C)
    (h : NamedObserversV25.observer (CategoryTreesV25.named C) t = some a) :
    NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree t) = some (F.bundle a) := by
  rw [CategoryTreesV25.named_observer] at h ⊢
  exact RawTransportV26.success F t a h
theorem none_iff (F : ProcessMap C D) (hi : F.ObjectInjective) (t : Tree O (Arrow C)) :
    NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree t) = none ↔
    NamedObserversV25.observer (CategoryTreesV25.named C) t = none := by
  simp only [CategoryTreesV25.named_observer]
  exact RawTransportV26.none_iff F hi t
theorem output_reflection (F : ProcessMap C D) (hi : F.ObjectInjective) (hf : F.Faithful)
    (s t : Tree O (Arrow C)) :
    NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree s) =
      NamedObserversV25.observer (CategoryTreesV25.named D) (F.tree t) ↔
    NamedObserversV25.observer (CategoryTreesV25.named C) s =
      NamedObserversV25.observer (CategoryTreesV25.named C) t := by
  simp only [CategoryTreesV25.named_observer]
  exact RawTransportV26.output_reflection F hi hf s t
end NamedTransportV29
