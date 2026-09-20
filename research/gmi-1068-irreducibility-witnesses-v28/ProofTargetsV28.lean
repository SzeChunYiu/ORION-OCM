import ContextBindingsV28
import ReverseBindingsV28
import ScalarBindingsV28
import SeparationV15
namespace ProofTargetsV28
open PartialContextV15 RecoverabilityV9
universe u v w
theorem forward_contract :
    ActionContextsV28.process false = ActionContextsV28.process true ∧
    (ActionContextsV28.context false).defined = (ActionContextsV28.context true).defined ∧
    ActionContextsV28.value false .a1 < ActionContextsV28.value false .a0 ∧
    ActionContextsV28.value true .a0 < ActionContextsV28.value true .a1 ∧
    ¬ Recoverable ActionContextsV28.process ActionContextsV28.context ∧
    ¬ Recoverable ActionContextsV28.process ActionContextsV28.orderView :=
  ⟨ActionContextsV28.same_process,ActionContextsV28.same_domain,
   ActionContextsV28.rankings.1,ActionContextsV28.rankings.2,
   ActionContextsV28.process_no_context,ActionContextsV28.process_no_order⟩
theorem weak_reverse_contract :
    ThinModelsV28.stateObservation false = ThinModelsV28.stateObservation true ∧
    ThinModelsV28.category false ≠ ThinModelsV28.category true ∧
    ¬ ThinModelsV28.admission false false true ∧ ThinModelsV28.admission true false true ∧
    ¬ Recoverable ThinModelsV28.stateObservation ThinModelsV28.admission ∧
    ¬ Recoverable ThinModelsV28.stateObservation ThinModelsV28.category :=
  ⟨ThinModelsV28.same_state,ThinModelsV28.categories_differ,
   ThinModelsV28.absent,ThinModelsV28.present,
   ThinModelsV28.no_admission_recovery,ThinModelsV28.no_category_recovery⟩
theorem admission_decoder_contract {H : Type u} {W : Type v} {M : Type w} :
    (∀ (P : H → Prop) (k : Context H W) (h : H), observe P k h ≠ .illegal ↔ P h) ∧
    (∀ (P Q : H → Prop) (k l : Context H W), observe P k = observe Q l → P = Q) ∧
    (∀ (P : M → H → Prop) (k : M → Context H W),
      Recoverable (fun m => observe (P m) (k m)) P) :=
  ⟨TaggedAdmissionV28.not_illegal,TaggedAdmissionV28.admission_eq,
   TaggedAdmissionV28.admission_recoverable⟩
end ProofTargetsV28
