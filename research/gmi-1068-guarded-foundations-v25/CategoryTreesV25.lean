import NamedObserversV25
import BundledCategoryV19
namespace CategoryTreesV25
open BracketV25 BundledCategoryV19 PresentedUnitsV25
universe u v
variable {O : Type u} (C : TypedPathsV11.Category.{u,v} O)
noncomputable def observer : Tree O (Arrow C) → Option (Arrow C) :=
  eval (mul C) some (fun o => some (identity C o))
theorem arrow (a : Arrow C) : observer C (.arrow a) = some a := rfl
theorem empty (o : O) : observer C (.empty o) = some (identity C o) := rfl
theorem seq (l r : Tree O (Arrow C)) :
    observer C (.seq l r) =
    (observer C l).bind (fun x => (observer C r).bind (mul C x)) := rfl
theorem guarded_flatten (t : Tree O (Arrow C)) :
    observer C t = fold (mul C) (flatten (identity C) t) :=
  OptionFoldV25.flatten_eval _ (associative C) _ t
theorem aligned_pair {a b c : O} (f : C.Hom a b) (g : C.Hom b c) :
    observer C (.seq (.arrow ⟨a,b,f⟩) (.arrow ⟨b,c,g⟩)) =
      some ⟨a,c,C.comp f g⟩ := aligned C f g
theorem rejected_pair {a b c d : O} (f : C.Hom a b) (g : C.Hom c d)
    (h : b ≠ c) :
    observer C (.seq (.arrow ⟨a,b,f⟩) (.arrow ⟨c,d,g⟩)) = none :=
  not_aligned C f g h
def pathTree {a b : O} : TypedPathsV11.Path C.Hom a b → Tree O (Arrow C)
  | .nil o => .empty o
  | @TypedPathsV11.Path.cons _ _ a b c f tail =>
    .seq (.arrow ⟨a,b,f⟩) (pathTree tail)
theorem path_nil (a : O) : pathTree C (.nil a) = .empty a := rfl
theorem path_cons {a b c : O} (f : C.Hom a b) (t : TypedPathsV11.Path C.Hom b c) :
    pathTree C (.cons f t) = .seq (.arrow ⟨a,b,f⟩) (pathTree C t) := rfl
theorem path_interpretation {a b : O} (p : TypedPathsV11.Path C.Hom a b) :
    observer C (pathTree C p) =
    some ⟨a,b,TypedPathsV11.eval C id (fun f => f) p⟩ := by
  induction p with
  | nil a => rfl
  | cons f p ih =>
    simp only [pathTree,seq,arrow,ih,Option.some_bind,TypedPathsV11.eval]
    exact aligned C f _
noncomputable def named : NamedObserversV25.NamedPresented O (Arrow C) where
  presented := full (algebra C)
  identityMap := identity C
  landing := by
    intro o
    rw [full_padded]
    exact identity_unit C o
theorem named_table : PresentedCoreV25.padded (named C).presented = mul C :=
  full_padded (algebra C)
theorem named_identity : (named C).identityMap = identity C := rfl
theorem named_complete : NamedObserversV25.Complete (named C) := by
  constructor
  · intro a b h
    exact congrArg Sigma.fst h
  · intro e he
    rw [named_table] at he
    obtain ⟨o,ho⟩ := (unit_iff_identity C e).mp he
    exact ⟨o,ho.symm⟩
theorem named_observer : NamedObserversV25.observer (named C) = observer C := by
  funext t
  simp [NamedObserversV25.observer,named,full_carrier,full_padded,observer,algebra]
theorem raw_bridge (t : Tree O (Arrow C)) :
    observer C t = RawObserversV25.observer (full (algebra C))
      (t.map (identity C) id) := by
  rw [← named_observer]
  exact NamedObserversV25.raw_translation (named C) t
end CategoryTreesV25
