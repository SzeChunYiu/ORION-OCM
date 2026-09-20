import RawObserversV25
namespace NamedObserversV25
open PresentedCoreV25 PresentedUnitsV25 PartialUnitsV19 BracketV25
universe u v w
attribute [local instance] Classical.propDecidable
structure NamedPresented (O : Type u) (L : Type v) where
  presented : Presented L
  identityMap : O → L
  landing : ∀ o, IsUnit (padded presented) (identityMap o)
def Complete (p : NamedPresented O L) : Prop :=
  (∀ a b, p.identityMap a = p.identityMap b → a = b) ∧
    ∀ e, IsUnit (padded p.presented) e → ∃ o, p.identityMap o = e
noncomputable def observer (p : NamedPresented O L) : Tree O L → Option L :=
  eval (padded p.presented)
    (fun a => if p.presented.carrier a then some a else none)
    (fun o => some (p.identityMap o))
theorem arrow (p : NamedPresented O L) (a : L) :
    observer p (.arrow a) = if p.presented.carrier a then some a else none := rfl
theorem empty (p : NamedPresented O L) (o : O) :
    observer p (.empty o) = some (p.identityMap o) := rfl
theorem seq (p : NamedPresented O L) (l r : Tree O L) :
    observer p (.seq l r) =
    (observer p l).bind (fun x => (observer p r).bind (padded p.presented x)) := rfl
theorem pair (p : NamedPresented O L) (x y : L) :
    observer p (.seq (.arrow x) (.arrow y)) = padded p.presented x y := by
  by_cases hx : p.presented.carrier x <;> by_cases hy : p.presented.carrier y <;>
    simp [observer,eval,hx,hy,padded]
noncomputable def data (p : NamedPresented O L) :=
  (padded p.presented,p.identityMap)
theorem data_observer (p q : NamedPresented O L) (h : data p = data q) :
    observer p = observer q := by
  have ht : padded p.presented = padded q.presented := congrArg Prod.fst h
  have hi : p.identityMap = q.identityMap := congrArg Prod.snd h
  have hc := table_determines_carrier p.presented q.presented ht
  simp only [observer,ht,hi,hc]
theorem observer_data (p q : NamedPresented O L) (h : observer p = observer q) :
    data p = data q := by
  apply Prod.ext
  · funext x y
    exact (pair p x y).symm.trans
      ((congrFun h (.seq (.arrow x) (.arrow y))).trans (pair q x y))
  · funext o
    exact Option.some.inj (congrFun h (.empty o))
theorem observer_eq_iff (p q : NamedPresented O L) :
    observer p = observer q ↔ data p = data q :=
  ⟨observer_data p q,data_observer p q⟩
theorem observer_recovery {M : Type u} {Z : Type w}
    (model : M → NamedPresented O L) (code : M → Z) :
    RecoverabilityV9.Recoverable code (fun m => observer (model m)) ↔
    RecoverabilityV9.Recoverable code (fun m => data (model m)) := by
  rw [RecoverabilityV9.recoverable_iff_fiber_constant,
    RecoverabilityV9.recoverable_iff_fiber_constant]
  constructor
  · intro h x y e
    exact observer_data _ _ (h x y e)
  · intro h x y e
    exact data_observer _ _ (h x y e)
theorem raw_translation (p : NamedPresented O L) (t : Tree O L) :
    observer p t =
    RawObserversV25.observer p.presented (t.map p.identityMap id) := by
  induction t with
  | arrow a => rfl
  | empty o =>
    simp [observer,eval,Tree.map,RawObserversV25.observer,p.landing]
  | seq l r hl hr =>
    simp only [seq,Tree.map,RawObserversV25.seq,hl,hr]
end NamedObserversV25
