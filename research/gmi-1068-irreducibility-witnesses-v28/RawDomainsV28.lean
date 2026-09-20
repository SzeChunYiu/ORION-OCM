import ThinModelsV28
import HistoryAdmissionV16
import TaggedAdmissionV28
import ActionContextsV28
namespace RawDomainsV28
open TypedPathsV11 PartialContextV15 TaggedAdmissionV28
def Graph (_ _ : Bool) := Unit
abbrev History := (a : Bool) × (b : Bool) × Path Graph a b
def edgeAllowed (m : Bool) {a b : Bool} (_ : Graph a b) : Prop := ThinModelsV28.relation m a b
def admitted (m : Bool) (h : History) : Prop := HistoryAdmissionV16.Admitted (@edgeAllowed m) h.2.2
def single (a b : Bool) : History := ⟨a,b,Path.single ()⟩
def crossing : History := single false true
def context : Context History Nat where
  defined _ := True
  eval h := stateValue h.val.2.1
  order := ActionContextsV28.natOrder
def undefinedContext : Context History Nat where
  defined _ := False
  eval h := False.elim h.property
  order := ActionContextsV28.natOrder
theorem single_admitted (m a b : Bool) :
    admitted m (single a b) ↔ ThinModelsV28.relation m a b :=
  HistoryAdmissionV16.admitted_single (@edgeAllowed m) ()
theorem crossing_absent : ¬ admitted false crossing := by
  intro h
  have hh := (single_admitted false false true).mp h
  cases hh
theorem crossing_present : admitted true crossing := (single_admitted true false true).mpr (Or.inr ⟨rfl,rfl⟩)
theorem domains_differ : admitted false ≠ admitted true := by
  intro h
  exact crossing_absent ((congrFun h crossing).symm ▸ crossing_present)
theorem tags_crossing :
    observe (admitted false) context crossing = .illegal ∧
    observe (admitted true) context crossing = .value 1 :=
  ⟨observe_illegal _ _ _ crossing_absent,observe_value _ _ _ crossing_present trivial⟩
theorem tags_differ : observe (admitted false) context ≠ observe (admitted true) context := by
  intro h
  exact domains_differ (admission_eq _ _ _ _ h)
theorem full_records_differ : (admitted false,context) ≠ (admitted true,context) := by
  intro h
  exact domains_differ (congrArg Prod.fst h)
theorem relative_domains_differ :
    (relativeDomain (admitted false) context).defined ≠
      (relativeDomain (admitted true) context).defined := by
  intro h
  have ht : (relativeDomain (admitted true) context).defined crossing := ⟨crossing_present,trivial⟩
  exact crossing_absent ((congrFun h crossing).symm ▸ ht).1
theorem active_empty (m : Bool) (h : History) :
    ¬ (relativeDomain (admitted m) undefinedContext).defined h := fun hh => hh.2
theorem active_domains_equal :
    (relativeDomain (admitted false) undefinedContext).defined =
      (relativeDomain (admitted true) undefinedContext).defined := by
  funext h
  exact propext ⟨fun hh => False.elim (active_empty false h hh),fun hh => False.elim (active_empty true h hh)⟩
theorem undefined_tags_crossing :
    observe (admitted false) undefinedContext crossing = .illegal ∧
    observe (admitted true) undefinedContext crossing = .undefined :=
  ⟨observe_illegal _ _ _ crossing_absent,observe_undefined _ _ _ crossing_present id⟩
theorem erased_undefined (m : Bool) (h : History) :
    eraseFailure (observe (admitted m) undefinedContext h) = none := by
  classical
  by_cases hp : admitted m h
  · rw [observe_undefined _ _ _ hp id]; rfl
  · rw [observe_illegal _ _ _ hp]; rfl
theorem erased_views_equal :
    (fun h => eraseFailure (observe (admitted false) undefinedContext h)) =
    (fun h => eraseFailure (observe (admitted true) undefinedContext h)) := by
  funext h
  rw [erased_undefined,erased_undefined]
end RawDomainsV28
