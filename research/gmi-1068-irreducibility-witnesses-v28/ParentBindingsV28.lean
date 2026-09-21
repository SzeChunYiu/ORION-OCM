import ContextBindingsV28
import ScalarBindingsV28
import SeparationV15
namespace ParentBindingsV28
open TypedPathsV11 PartialContextV15
universe u v w
attribute [local instance] Classical.propDecidable
theorem admitted_nil {V : Type u} {G : V → V → Type v}
    (P : {a b : V} → G a b → Prop) (a : V) :
    HistoryAdmissionV16.Admitted @P (Path.nil a) ↔ True := Iff.rfl
theorem admitted_cons {V : Type u} {G : V → V → Type v}
    (P : {a b : V} → G a b → Prop) {a b c : V} (e : G a b) (p : Path G b c) :
    HistoryAdmissionV16.Admitted @P (Path.cons e p) ↔
      P e ∧ HistoryAdmissionV16.Admitted @P p := Iff.rfl
theorem decode_single {V : Type u} {G : V → V → Type v}
    (D : {a b : V} → Path G a b → Prop) {a b : V} (e : G a b) :
    HistoryAdmissionV16.decode @D e ↔ D (Path.single e) := Iff.rfl
theorem active {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) (h : H) :
    (relativeDomain P k).defined h ↔ P h ∧ k.defined h := Iff.rfl
theorem observe_definition {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) :
    observe P k h = (if P h then
      if hd : k.defined h then .value (k.eval ⟨h,hd⟩) else .undefined else .illegal) := by
  classical
  rfl
theorem recoverable_binding {M : Type u} {P : Type v} {O : Type w}
    (p : M → P) (o : M → O) :
    RecoverabilityV9.Recoverable p o ↔
      ∃ d : RecoverabilityV9.Image p → O, ∀ m, d (RecoverabilityV9.encoded p m) = o m := Iff.rfl
theorem int_order (a b : Int) : (inferInstance : ScalarV12.Scalar Int).toLE.le a b ↔ a ≤ b := Iff.rfl
end ParentBindingsV28
