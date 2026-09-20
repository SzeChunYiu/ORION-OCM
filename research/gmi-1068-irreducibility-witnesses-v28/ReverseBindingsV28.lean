import RawDomainsV28
namespace ReverseBindingsV28
open TypedPathsV11 PartialContextV15
theorem relation_false (a b : Bool) : ThinModelsV28.relation false a b ↔ reach0 a b := Iff.rfl
theorem relation_true (a b : Bool) : ThinModelsV28.relation true a b ↔ reach1 a b := Iff.rfl
theorem hom (m a b : Bool) : (ThinModelsV28.category m).Hom a b =
    PLift (ThinModelsV28.relation m a b) := rfl
theorem identity (m a : Bool) : ((ThinModelsV28.category m).id a).down =
    ThinModelsV28.reflexive m a := rfl
theorem composition (m : Bool) {a b c : Bool}
    (f : (ThinModelsV28.category m).Hom a b) (g : (ThinModelsV28.category m).Hom b c) :
    ((ThinModelsV28.category m).comp f g).down = ThinModelsV28.transitive m f.down g.down := rfl
theorem state_observer (m : Bool) : ThinModelsV28.stateObservation m = stateValue := rfl
theorem admission (m a b : Bool) : ThinModelsV28.admission m a b ↔
    Nonempty ((ThinModelsV28.category m).Hom a b) := Iff.rfl
theorem graph (a b : Bool) : RawDomainsV28.Graph a b = Unit := rfl
theorem edge (m : Bool) {a b : Bool} (e : RawDomainsV28.Graph a b) :
    RawDomainsV28.edgeAllowed m e ↔ ThinModelsV28.relation m a b := Iff.rfl
theorem raw_admission (m : Bool) (h : RawDomainsV28.History) :
    RawDomainsV28.admitted m h ↔
      HistoryAdmissionV16.Admitted (@RawDomainsV28.edgeAllowed m) h.2.2 := Iff.rfl
theorem raw_single (a b : Bool) : RawDomainsV28.single a b =
    (⟨a,b,Path.single ()⟩ : RawDomainsV28.History) := rfl
theorem raw_crossing : RawDomainsV28.crossing = RawDomainsV28.single false true := rfl
theorem endpoint_defined (h : RawDomainsV28.History) : RawDomainsV28.context.defined h ↔ True := Iff.rfl
theorem endpoint_value (h : {h : RawDomainsV28.History // RawDomainsV28.context.defined h}) :
    RawDomainsV28.context.eval h = stateValue h.val.2.1 := rfl
theorem endpoint_order (a b : Nat) : RawDomainsV28.context.order.le a b ↔ a ≤ b := Iff.rfl
theorem undefined_domain (h : RawDomainsV28.History) : RawDomainsV28.undefinedContext.defined h ↔ False := Iff.rfl
theorem undefined_eval (h : {h : RawDomainsV28.History // RawDomainsV28.undefinedContext.defined h}) :
    RawDomainsV28.undefinedContext.eval h = False.elim h.property := rfl
theorem undefined_order (a b : Nat) : RawDomainsV28.undefinedContext.order.le a b ↔ a ≤ b := Iff.rfl
end ReverseBindingsV28
