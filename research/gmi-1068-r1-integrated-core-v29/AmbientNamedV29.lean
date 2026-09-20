import ImageAlgebraV29
import NamedTransportV29
namespace AmbientNamedV29
open TypedPathsV11 BundledCategoryV19 BracketV25 PartialUnitsV19
universe u v w x
variable {O : Type u} {L : Type w} {N : Type x} (C : Category.{u,v} O)
    (j : Arrow C → L) (hj : ∀ a b, j a = j b → a = b) (q : N → O)
noncomputable def named : NamedObserversV25.NamedPresented N L where
  presented := ImageAlgebraV29.presented j hj (algebra C)
  identityMap := fun n => j (identity C (q n))
  landing := by
    intro n
    apply (PresentedUnitsV25.padded_unit _ _).mpr
    refine ⟨⟨identity C (q n),rfl⟩,?_⟩
    exact (ImageAlgebraV29.tableIso j hj (mul C)).unit_forward (identity_unit C (q n))
theorem carrier (l : L) : (named C j hj q).presented.carrier l ↔ ∃ a, j a = l := Iff.rfl
theorem identity_binding (n : N) : (named C j hj q).identityMap n = j (identity C (q n)) := rfl
theorem padded_binding (a b : Arrow C) :
    PresentedCoreV25.padded (named C j hj q).presented (j a) (j b) =
      (mul C a b).map j := ImageAlgebraV29.padded_put j hj (algebra C) a b
theorem absent (l : L) (h : ¬∃ a, j a = l) :
    NamedObserversV25.observer (named C j hj q) (.arrow l) = none := by
  classical
  simp only [NamedObserversV25.arrow,carrier]
  exact if_neg h
theorem observer_transport (t : Tree N (Arrow C)) :
    NamedObserversV25.observer (named C j hj q) (t.map id j) =
      (CategoryTreesV25.observer C (t.map q id)).map j := by
  induction t with
  | arrow a =>
    classical
    simp [Tree.map,NamedObserversV25.arrow,carrier,CategoryTreesV25.arrow]
  | empty n => rfl
  | seq l r hl hr =>
    simp only [Tree.map,NamedObserversV25.seq,CategoryTreesV25.seq,hl,hr]
    cases CategoryTreesV25.observer C (l.map q id) with
    | none => rfl
    | some a =>
      cases CategoryTreesV25.observer C (r.map q id) with
      | none => rfl
      | some b => exact padded_binding C j hj q a b
theorem complete (qi : ∀ a b, q a = q b → a = b) (qs : ∀ o, ∃ n, q n = o) :
    NamedObserversV25.Complete (named C j hj q) := by
  constructor
  · intro a b h
    apply qi
    exact congrArg Sigma.fst (hj _ _ h)
  · intro e he
    obtain ⟨hec,hu⟩ := (PresentedUnitsV25.padded_unit _ _).mp he
    let a : ImageAlgebraV29.Image j := ⟨e,hec⟩
    have hu' : IsUnit (ImageAlgebraV29.operation j (mul C)) a := hu
    have hv := (ImageAlgebraV29.tableIso j hj (mul C)).symm.unit_forward hu'
    obtain ⟨o,ho⟩ := (unit_iff_identity C _).mp hv
    obtain ⟨n,hn⟩ := qs o
    refine ⟨n,?_⟩
    change j (identity C (q n)) = e
    rw [hn,← ho]
    exact congrArg Subtype.val (ImageAlgebraV29.put_get j a)
theorem lift_tree {A : Type u} {B : Type v} {K : Type w} (f : A → B)
    (t : Tree K B) (h : Valid (fun b => ∃ a, f a = b) (fun _ => True) t) :
    ∃ s : Tree K A, s.map id f = t := by
  induction t with
  | arrow b => obtain ⟨a,ha⟩ := h; exact ⟨.arrow a,congrArg Tree.arrow ha⟩
  | empty k => exact ⟨.empty k,rfl⟩
  | seq l r hl hr =>
    obtain ⟨s,hs⟩ := hl h.1
    obtain ⟨t,ht⟩ := hr h.2
    exact ⟨.seq s t,by simp only [Tree.map,hs,ht]⟩
theorem map_composition {A : Type u} {B : Type v} {K : Type w} {L : Type x}
    (f : A → B) (g : B → L) (t : Tree K A) :
    (t.map id f).map id g = t.map id (fun a => g (f a)) := by
  induction t with
  | arrow => rfl
  | empty => rfl
  | seq l r hl hr => simp only [Tree.map,hl,hr]
end AmbientNamedV29
