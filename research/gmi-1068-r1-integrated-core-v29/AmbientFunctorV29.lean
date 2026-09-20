import AmbientNamedV29
namespace AmbientFunctorV29
open TypedPathsV11 ProcessMapsV26 BundledCategoryV19 BracketV25
universe u v w x y z
variable {O : Type u} {P : Type v} {L : Type w} {N : Type x}
    {C : Category.{u,y} O} {D : Category.{v,z} P}
theorem tree_square (F : ProcessMap C D) (q : N → O) (t : Tree N (Arrow C)) :
    (t.map id F.bundle).map (fun n => F.obj (q n)) id = F.tree (t.map q id) := by
  induction t with
  | arrow => rfl
  | empty => rfl
  | seq l r hl hr => simp only [Tree.map,ProcessMap.tree,hl,hr]
theorem mapped (F : ProcessMap C D) (hi : F.ObjectInjective)
    (j : Arrow D → L) (hj : ∀ a b, j a = j b → a = b)
    (k : Arrow C → L) (hk : ∀ a b, k a = k b → a = b)
    (eqk : ∀ a, k a = j (F.bundle a)) (q : N → O) (t : Tree N (Arrow C)) :
    NamedObserversV25.observer (AmbientNamedV29.named D j hj (fun n => F.obj (q n)))
      (t.map id k) =
    NamedObserversV25.observer (AmbientNamedV29.named C k hk q) (t.map id k) := by
  have ht : t.map id k = (t.map id F.bundle).map id j := by
    rw [AmbientNamedV29.map_composition]
    have he : k = fun a => j (F.bundle a) := funext eqk
    rw [he]
  calc
    _ = NamedObserversV25.observer (AmbientNamedV29.named D j hj (fun n => F.obj (q n)))
        ((t.map id F.bundle).map id j) := congrArg _ ht
    _ = (CategoryTreesV25.observer D
        ((t.map id F.bundle).map (fun n => F.obj (q n)) id)).map j :=
      AmbientNamedV29.observer_transport D j hj _ _
    _ = (CategoryTreesV25.observer C (t.map q id)).map k := by
      rw [tree_square,RawTransportV26.trees_of_injective F hi,Option.map_map]
      exact congrArg (fun f => Option.map f (CategoryTreesV25.observer C (t.map q id)))
        (funext fun a => (eqk a).symm)
    _ = _ := (AmbientNamedV29.observer_transport C k hk q t).symm
theorem guarded (F : ProcessMap C D) (hi : F.ObjectInjective)
    (j : Arrow D → L) (hj : ∀ a b, j a = j b → a = b)
    (k : Arrow C → L) (hk : ∀ a b, k a = k b → a = b)
    (eqk : ∀ a, k a = j (F.bundle a)) (q : N → O) (t : Tree N L)
    (h : Valid (fun l => ∃ a, k a = l) (fun _ => True) t) :
    NamedObserversV25.observer (AmbientNamedV29.named D j hj (fun n => F.obj (q n))) t =
    NamedObserversV25.observer (AmbientNamedV29.named C k hk q) t := by
  obtain ⟨s,rfl⟩ := AmbientNamedV29.lift_tree k t h
  exact mapped F hi j hj k hk eqk q s
end AmbientFunctorV29
