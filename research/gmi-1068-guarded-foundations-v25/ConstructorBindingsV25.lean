import LawControlsV25
namespace ConstructorBindingsV25
open BracketV25 PresentedCoreV25 NamedObserversV25 PartialUnitsV19
attribute [local instance] Classical.propDecidable
theorem lookup_present (p : Presented L) (x : L) (hx : p.carrier x) :
    lookup p x = some ⟨x,hx⟩ := by simp [lookup,hx]
theorem lookup_absent (p : Presented L) (x : L) (hx : ¬p.carrier x) :
    lookup p x = none := by simp [lookup,hx]
theorem append_binding (x y : Word A) : append x y = (x.1,x.2 ++ y.1::y.2) := rfl
theorem fold_binding (m : A → A → Option A) (w : Word A) :
    fold m w = ResponsesV19.run m w.1 w.2 := rfl
theorem eval_arrow (m : B → B → Option B) (a : A → Option B) (e : O → Option B) (x : A) :
    eval m a e (.arrow x) = a x := rfl
theorem eval_empty (m : B → B → Option B) (a : A → Option B) (e : O → Option B) (x : O) :
    eval m a e (.empty x) = e x := rfl
theorem valid_arrow (a : A → Prop) (e : O → Prop) (x : A) :
    Valid a e (.arrow x) ↔ a x := Iff.rfl
theorem valid_empty (a : A → Prop) (e : O → Prop) (x : O) :
    Valid a e (.empty x) ↔ e x := Iff.rfl
theorem valid_seq (a : A → Prop) (e : O → Prop) (l r : Tree O A) :
    Valid a e (.seq l r) ↔ Valid a e l ∧ Valid a e r := Iff.rfl
theorem map_arrow (fo : O → P) (fa : A → B) (x : A) :
    (Tree.arrow x : Tree O A).map fo fa = .arrow (fa x) := rfl
theorem map_empty (fo : O → P) (fa : A → B) (o : O) :
    (Tree.empty o : Tree O A).map fo fa = .empty (fo o) := rfl
theorem map_seq (fo : O → P) (fa : A → B) (l r : Tree O A) :
    (l.seq r).map fo fa = .seq (l.map fo fa) (r.map fo fa) := rfl
theorem core_binding (p : Presented L) : RawObserversV25.core p = (p.carrier,padded p) := rfl
theorem data_binding (p : NamedPresented O L) :
    data p = (padded p.presented,p.identityMap) := rfl
theorem named_complete_binding (p : NamedPresented O L) :
    Complete p ↔ (∀ a b, p.identityMap a = p.identityMap b → a = b) ∧
      ∀ e, IsUnit (padded p.presented) e → ∃ o, p.identityMap o = e := Iff.rfl
theorem raw_arrow_census (p : Presented L) (x : L) :
    RawObserversV25.observer p (.arrow x) = some x ↔ p.carrier x := by
  rw [RawObserversV25.arrow]
  by_cases hx : p.carrier x <;> simp [hx]
theorem raw_threeway_recovery {M : Type u} {Z : Type v} {L : Type w} (model : M → Presented L) (code : M → Z) :
    (RecoverabilityV9.Recoverable code (fun m => RawObserversV25.observer (model m)) ↔
      RecoverabilityV9.Recoverable code (fun m => RawObserversV25.core (model m))) ∧
    (RecoverabilityV9.Recoverable code (fun m => RawObserversV25.core (model m)) ↔
      RecoverabilityV9.Recoverable code (fun m => padded (model m))) :=
  ⟨(RawObserversV25.observer_recovery model code).trans
    (RawObserversV25.core_recovery model code).symm,RawObserversV25.core_recovery model code⟩
theorem category_named_carrier {O : Type u} (C : TypedPathsV11.Category.{u,v} O) :
    (CategoryTreesV25.named C).presented.carrier = fun _ => True := rfl
theorem full_mul (P : Algebra A) (x y : {_x : A // True}) :
    (PresentedUnitsV25.full P).algebra.mul x y =
      (P.mul x.val y.val).map (fun z => ⟨z,True.intro⟩) := rfl
theorem leftTree_binding (a b c : A) :
    LawControlsV25.leftTree a b c = Tree.seq (.seq (.arrow a) (.arrow b)) (.arrow c) := rfl
theorem rightTree_binding (a b c : A) :
    LawControlsV25.rightTree a b c = Tree.seq (.arrow a) (.seq (.arrow b) (.arrow c)) := rfl
theorem erase_arrow (a : A) :
    LawControlsV25.eraseAnchors (.arrow a : Tree O A) = [a] := rfl
theorem erase_empty (o : O) :
    LawControlsV25.eraseAnchors (.empty o : Tree O A) = [] := rfl
theorem erase_seq (l r : Tree O A) :
    LawControlsV25.eraseAnchors (.seq l r) =
      LawControlsV25.eraseAnchors l ++ LawControlsV25.eraseAnchors r := rfl
end ConstructorBindingsV25
