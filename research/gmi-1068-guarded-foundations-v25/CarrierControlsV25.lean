import AlgebraTreesV25
import InformationControlsV19
namespace CarrierControlsV25
open PartialUnitsV19 PresentedCoreV25 BracketV25
attribute [local instance] Classical.propDecidable
noncomputable def discreteAlgebra (A : Type u) : Algebra A where
  mul x y := if x = y then some x else none
  assoc := by
    intro x y z
    by_cases hxy : x = y <;> by_cases hyz : y = z <;>
      simp_all
  localUnits := by
    intro x
    have hu : IsUnit (fun a b : A => if a = b then some a else none) x := by
      refine ⟨by simp,?_,?_⟩
      · intro a b h
        by_cases ha : x = a <;> simp_all
      · intro a b h
        by_cases ha : a = x <;> simp_all
    exact ⟨x,x,hu,hu,by simp,by simp⟩
  coherent := by
    intro x y z a b h k
    by_cases hxy : x = y <;> by_cases hyz : y = z <;>
      simp_all
noncomputable def supported (S : L → Prop) : Presented L :=
  ⟨S,discreteAlgebra {x // S x}⟩
theorem supported_carrier (S : L → Prop) : (supported S).carrier = S := rfl
theorem supported_padded (S : L → Prop) (x y : L) :
    padded (supported S) x y =
    if S x ∧ x = y then some x else none := by
  by_cases hx : S x <;> by_cases hy : S y <;> by_cases hxy : x = y <;>
    simp_all [padded,supported,discreteAlgebra,Subtype.ext_iff]
theorem supported_unit (S : L → Prop) (e : L) :
    IsUnit (padded (supported S)) e ↔ S e := by
  constructor
  · intro h
    exact (result_membership _ e e e h.1).1
  · intro h
    refine ⟨?_,?_,?_⟩
    · simp [supported_padded,h]
    · intro x y hm
      rw [supported_padded] at hm
      by_cases hh : e = x <;> simp_all
    · intro x y hm
      rw [supported_padded] at hm
      by_cases hh : x = e <;> by_cases hx : S x <;> simp_all
theorem absent_present_singleton :
    RawObserversV25.observer (supported (fun _ : Bool => False)) (.arrow false) = none ∧
    RawObserversV25.observer (supported (fun x : Bool => x = false)) (.arrow false) =
      some false := by simp [RawObserversV25.arrow,supported]
theorem equal_size_labels :
    RawObserversV25.observer (supported (fun x : Bool => x = false)) (.arrow false) =
      some false ∧
    RawObserversV25.observer (supported (fun x : Bool => x = true)) (.arrow false) =
      none := by simp [RawObserversV25.arrow,supported]
theorem anchored_empty :
    RawObserversV25.observer (supported (fun _ : Bool => True))
      (.seq (.empty false) (.empty true)) = none ∧
    RawObserversV25.observer (supported (fun _ : Bool => True))
      (.seq (.empty false) (.empty false)) = some false := by
  simp [RawObserversV25.seq,RawObserversV25.empty,supported_unit,supported_padded]
noncomputable def named (swap : Bool) : NamedObserversV25.NamedPresented Bool Bool where
  presented := supported (fun _ => True)
  identityMap := fun x => if swap then !x else x
  landing := by intro x; exact (supported_unit _ _).mpr True.intro
theorem named_complete (swap : Bool) : NamedObserversV25.Complete (named swap) := by
  cases swap <;> constructor
  · intro a b h; exact h
  · intro e _; exact ⟨e,rfl⟩
  · intro a b h; cases a <;> cases b <;> simp_all [named]
  · intro e _; exact ⟨!e,by cases e <;> rfl⟩
theorem swapped_names :
    padded (named false).presented = padded (named true).presented ∧
    NamedObserversV25.observer (named false) (.empty false) = some false ∧
    NamedObserversV25.observer (named true) (.empty false) = some true := by
  exact ⟨rfl,rfl,rfl⟩
theorem table_only_nonrecovery :
    ¬ RecoverabilityV9.Recoverable (fun s : Bool => padded (named s).presented)
      (fun s => NamedObserversV25.observer (named s)) := by
  rw [RecoverabilityV9.recoverable_iff_fiber_constant]
  intro h
  have hh := congrFun (h false true rfl) (.empty false)
  change some false = some true at hh
  cases hh
theorem paired_revival :
    RecoverabilityV9.Recoverable (fun s : Bool => NamedObserversV25.data (named s))
      (fun s => NamedObserversV25.observer (named s)) := by
  rw [NamedObserversV25.observer_recovery,
    RecoverabilityV9.recoverable_iff_fiber_constant]
  exact fun _ _ h => h
end CarrierControlsV25
