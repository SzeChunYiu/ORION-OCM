import PermissionContextsV22
import PermissionMinimalityV22
namespace ProofTargetsV22
open ContinuationV8 BudgetResidualV21 PartialContextV15
open PermissionSetsV22 PermissionMachineV22 PermissionExecutionV22
open PermissionContextsV22 PermissionIncidenceV22 PermissionMinimalityV22
universe u v w x y z
theorem gated_success_contract {S : Type u} {A : Type v} {O : Type w}
    {E : Type x} {Q : Type y} (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (s t : S) (word : List A) :
    endpoint (gated m req enabled) s word=some t ↔
      ∃R,support m req s word=some (t,R)∧Sub R enabled :=
  gated_success m req enabled s t word
theorem context_incidence_contract {S : Type u} {A : Type v} {O : Type w}
    {E : Type x} {Q : Type y} {W : Type z}
    (m : Machine S A O E) (req : S→A→Family Q) (enabled : Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) (T : W→Prop) :
    (∃v,Image (scenario m req enabled P D k) v∧T v) ↔
      Cap (eligible m req P D k T) requirements enabled :=
  context_incidence m req enabled P D k T
theorem minimal_blocker_contract {H : Type u} {Q : Type v} (W : H→Prop)
    (R : H→Family Q) (S B : Family Q) :
    Minimal (Blocks W R S) B ↔ Blocks W R S B∧Private W R S B :=
  minimal_blocker W R S B
end ProofTargetsV22
