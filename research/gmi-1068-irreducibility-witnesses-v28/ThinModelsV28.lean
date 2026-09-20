import OriginalBindingsV28
import TypedPathsV11
import RecoverabilityV9
namespace ThinModelsV28
open TypedPathsV11 RecoverabilityV9
def relation (m a b : Bool) : Prop := if m then reach1 a b else reach0 a b
theorem reflexive (m a : Bool) : relation m a a := by cases m <;> simp [relation,reach0,reach1]
theorem transitive (m : Bool) {a b c : Bool}
    (h : relation m a b) (k : relation m b c) : relation m a c := by
  cases m <;> cases a <;> cases b <;> cases c <;> simp_all [relation,reach0,reach1]
def category (m : Bool) : Category Bool where
  Hom a b := PLift (relation m a b)
  id a := ⟨reflexive m a⟩
  comp f g := ⟨transitive m f.down g.down⟩
  assoc _ _ _ := rfl
  left_id f := by cases f; rfl
  right_id f := by cases f; rfl
def admission (m a b : Bool) := Nonempty ((category m).Hom a b)
theorem hom_iff (m a b : Bool) : admission m a b ↔ relation m a b :=
  ⟨fun ⟨h⟩ => h.down,fun h => ⟨⟨h⟩⟩⟩
theorem absent : ¬ admission false false true := by
  intro h
  have hh := (hom_iff false false true).mp h
  cases hh
theorem present : admission true false true := ⟨⟨Or.inr ⟨rfl,rfl⟩⟩⟩
theorem admissions_differ : admission false ≠ admission true := by
  intro h
  exact absent ((congrFun (congrFun h false) true).symm ▸ present)
theorem categories_differ : category false ≠ category true := by
  intro h
  have hh : admission false false true = admission true false true :=
    congrArg (fun c : Category Bool => Nonempty (c.Hom false true)) h
  exact absent (hh.symm ▸ present)
def stateObservation (_ : Bool) := stateValue
theorem same_state : stateObservation false = stateObservation true := rfl
theorem no_admission_recovery : ¬ Recoverable stateObservation admission :=
  no_recovery_of_collision false true same_state admissions_differ
theorem no_category_recovery : ¬ Recoverable stateObservation category :=
  no_recovery_of_collision false true same_state categories_differ
end ThinModelsV28
