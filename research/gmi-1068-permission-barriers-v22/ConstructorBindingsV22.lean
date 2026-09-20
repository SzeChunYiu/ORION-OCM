import PermissionContextsV22
import HistoryPermissionsV22
import SupportFrontierV22
namespace ConstructorBindingsV22
open ContinuationV8 BudgetResidualV21 PartialContextV15
open PermissionSetsV22 PermissionMachineV22 PermissionContextsV22
open PermissionIncidenceV22 PermissionMinimalityV22 FinitePermissionsV22
universe u v w x y z
theorem sub_binding {Q : Type u} (R S : Family Q) :
    Sub R S ↔ ∀q,R q→S q := Iff.rfl
theorem union_binding {Q : Type u} (R S : Family Q) (q : Q) :
    union R S q ↔ R q ∨ S q := Iff.rfl
theorem diff_binding {Q : Type u} (R S : Family Q) (q : Q) :
    diff R S q ↔ R q ∧ ¬S q := Iff.rfl
theorem minimal_binding {Q : Type u} (F : Family Q→Prop) (B : Family Q) :
    Minimal F B ↔ F B ∧ ∀C,Sub C B→F C→C=B := Iff.rfl
variable {S : Type u} {A : Type v} {O : Type w} {E : Type x} {Q : Type y} {W : Type z}
theorem gated_next (m : Machine S A O E) (req : S→A→Family Q) (enabled : Family Q)
    (s : S) (a : A) :
    (gated m req enabled).next s a=(m.next s a).bind (fun p =>
      @ite _ (Sub (req s a) enabled) (Classical.propDecidable _) (some p) none) := rfl
theorem scenario_admission (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop) (k : Context (History S A) W)
    (h : History S A) :
    (scenario m req enabled P D k).admission h ↔
      P h ∧ D h ∧ ∃t,endpoint (gated m req enabled) h.1 h.2=some t := Iff.rfl
theorem scenario_domain (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop) (k : Context (History S A) W)
    (h : History S A) :
    (scenario m req enabled P D k).context.defined h ↔ k.defined h := Iff.rfl
theorem scenario_eval (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop) (k : Context (History S A) W)
    (h : History S A) (he : k.defined h) :
    (scenario m req enabled P D k).context.eval ⟨h,he⟩=k.eval ⟨h,he⟩ := rfl
theorem scenario_order (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop) (k : Context (History S A) W) :
    (scenario m req enabled P D k).context.order=k.order := rfl
theorem witness_binding (m : Machine S A O E) (req : S→A→Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) (T : W→Prop)
    (h : History S A) (t : S) (R : Family Q) :
    Witness m req P D k T h t R ↔ P h ∧ D h ∧
      support m req h.1 h.2=some (t,R) ∧ ∃he:k.defined h,T (k.eval ⟨h,he⟩) := Iff.rfl
theorem eligible_binding (m : Machine S A O E) (req : S→A→Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) (T : W→Prop)
    (i : WitnessIndex S A Q) :
    eligible m req P D k T i ↔ Witness m req P D k T i.1 i.2.1 i.2.2 := Iff.rfl
theorem requirements_binding (i : WitnessIndex S A Q) (q : Q) :
    requirements i q ↔ i.2.2 q := Iff.rfl
theorem image_binding {H : Type u} (sc : Scenario H W) (v : W) :
    Image sc v ↔ ∃h, sc.admission h ∧ ∃he:sc.context.defined h,
      sc.context.eval ⟨h,he⟩=v := by
  simp only [Image,PartialPostcontextV20.Attained,true_and]
theorem cap_binding {H : Type u} (V : H→Prop) (R : H→Family Q) (S : Family Q) :
    Cap V R S ↔ ∃h,V h∧Sub (R h) S := Iff.rfl
theorem block_binding {H : Type u} (V : H→Prop) (R : H→Family Q) (S B : Family Q) :
    Blocks V R S B ↔ ¬Cap V R (diff S B) := Iff.rfl
theorem private_binding {H : Type u} (V : H→Prop) (R : H→Family Q) (S B : Family Q) :
    Private V R S B ↔
      ∀b,B b→∃h,V h∧Sub (R h) S∧∀q,(R h q∧B q)↔q=b := Iff.rfl
theorem deficit_binding {H : Type u} (V : H→Prop) (R : H→Family Q)
    (U S0 D : Family Q) :
    DeficitFamily V R U S0 D ↔ ∃h,V h∧Sub (R h) U∧D=diff (R h) S0 := Iff.rfl
theorem enabling_binding {H : Type u} (V : H→Prop) (R : H→Family Q)
    (U S0 D : Family Q) :
    Enabling V R U S0 D ↔ Sub D (diff U S0)∧Cap V R (union S0 D) := Iff.rfl
theorem choices_nil : choices ([] : List Q)=[empty] := rfl
theorem choices_cons (q : Q) (L : List Q) :
    choices (q::L)=choices L++(choices L).map (union (single q)) := rfl
theorem members_binding (L : List Q) (q : Q) : members L q ↔ q∈L := Iff.rfl
theorem reverse_binding (R S : Family Q) : reverseInclusion.le R S ↔ Sub S R := Iff.rfl
theorem candidates_binding (L : List Q) (F : Family Q→Prop) :
    candidates L F=(choices L).filter (fun R => @decide (F R) (Classical.propDecidable _)) := rfl
theorem minimal_members_binding (L : List Q) (F : Family Q→Prop) :
    minimalMembers L F=@FrontierOrderV20.frontier _ reverseInclusion
      (fun _ _ => Classical.propDecidable _) (candidates L F) := rfl
end ConstructorBindingsV22
