import PresentedUnitsV25
import RecoverabilityV9
namespace RawObserversV25
open PresentedCoreV25 PresentedUnitsV25 PartialUnitsV19 BracketV25
universe u v
attribute [local instance] Classical.propDecidable
noncomputable def observer (p : Presented L) : Tree L L → Option L :=
  eval (padded p) (fun a => if p.carrier a then some a else none)
    (fun e => if IsUnit (padded p) e then some e else none)
theorem arrow (p : Presented L) (a : L) :
    observer p (.arrow a) = if p.carrier a then some a else none := rfl
theorem empty (p : Presented L) (e : L) :
    observer p (.empty e) = if IsUnit (padded p) e then some e else none := rfl
theorem seq (p : Presented L) (l r : Tree L L) :
    observer p (.seq l r) =
    (observer p l).bind (fun x => (observer p r).bind (padded p x)) := rfl
theorem pair (p : Presented L) (x y : L) :
    observer p (.seq (.arrow x) (.arrow y)) = padded p x y := by
  by_cases hx : p.carrier x <;> by_cases hy : p.carrier y <;>
    simp [observer,eval,hx,hy,padded]
theorem guarded (p : Presented L) (t : Tree L L) :
    observer p t = if Valid p.carrier (IsUnit (padded p)) t then
      fold (padded p) (flatten id t) else none :=
  OptionFoldV25.guarded_flatten (padded p) (padded_assoc p) id _ _ t
theorem table_observer (p q : Presented L) (h : padded p = padded q) :
    observer p = observer q := by
  have hc := table_determines_carrier p q h
  simp only [observer,h,hc]
theorem observer_table (p q : Presented L) (h : observer p = observer q) :
    padded p = padded q := by
  funext x y
  exact (pair p x y).symm.trans
    ((congrFun h (.seq (.arrow x) (.arrow y))).trans (pair q x y))
theorem observer_eq_iff (p q : Presented L) :
    observer p = observer q ↔ padded p = padded q :=
  ⟨observer_table p q,table_observer p q⟩
noncomputable def core (p : Presented L) := (p.carrier,padded p)
theorem core_eq_iff (p q : Presented L) :
    core p = core q ↔ padded p = padded q := by
  constructor
  · exact fun h => congrArg Prod.snd h
  · intro h
    exact Prod.ext (table_determines_carrier p q h) h
theorem observer_recovery {M : Type u} {Z : Type v} (model : M → Presented L)
    (code : M → Z) :
    RecoverabilityV9.Recoverable code (fun m => observer (model m)) ↔
    RecoverabilityV9.Recoverable code (fun m => padded (model m)) := by
  rw [RecoverabilityV9.recoverable_iff_fiber_constant,
    RecoverabilityV9.recoverable_iff_fiber_constant]
  constructor
  · intro h x y e
    exact observer_table _ _ (h x y e)
  · intro h x y e
    exact table_observer _ _ (h x y e)
theorem core_recovery {M : Type u} {Z : Type v} (model : M → Presented L)
    (code : M → Z) :
    RecoverabilityV9.Recoverable code (fun m => core (model m)) ↔
    RecoverabilityV9.Recoverable code (fun m => padded (model m)) := by
  rw [RecoverabilityV9.recoverable_iff_fiber_constant,
    RecoverabilityV9.recoverable_iff_fiber_constant]
  constructor
  · intro h x y e
    exact (core_eq_iff _ _).mp (h x y e)
  · intro h x y e
    exact (core_eq_iff _ _).mpr (h x y e)
theorem full_observer (P : Algebra A) :
    observer (full P) =
    eval P.mul some (fun e => if IsUnit P.mul e then some e else none) := by
  funext t
  simp [observer,full_padded,full_carrier]
end RawObserversV25
