import PermissionExecutionV22
import PermissionIncidenceV22
import PartialPostcontextV20
namespace PermissionContextsV22
open ContinuationV8 BudgetResidualV21 PartialContextV15 PartialPostcontextV20
open PermissionSetsV22 PermissionMachineV22 PermissionExecutionV22 PermissionIncidenceV22
universe u v w x y z
variable {S : Type u} {A : Type v} {O : Type w} {E : Type x} {Q : Type y} {W : Type z}
abbrev History (S : Type u) (A : Type v) := S × List A
structure Scenario (H : Type u) (W : Type v) where
  admission : H→Prop
  context : Context H W
def admission (m : Machine S A O E) (req : S→A→Family Q) (enabled : Family Q)
    (P D : History S A→Prop) (h : History S A) :=
  P h ∧ D h ∧ ∃t, endpoint (gated m req enabled) h.1 h.2=some t
def scenario (m : Machine S A O E) (req : S→A→Family Q) (enabled : Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) :
    Scenario (History S A) W := ⟨admission m req enabled P D,k⟩
def Image {H : Type u} (sc : Scenario H W) :=
  Attained sc.admission sc.context (fun _ => True)
noncomputable def view {H : Type u} (sc : Scenario H W) :=
  observe sc.admission sc.context
def Witness (m : Machine S A O E) (req : S→A→Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) (T : W→Prop)
    (h : History S A) (t : S) (R : Family Q) :=
  P h ∧ D h ∧ support m req h.1 h.2=some (t,R) ∧
    ∃he:k.defined h, T (k.eval ⟨h,he⟩)
abbrev WitnessIndex (S : Type u) (A : Type v) (Q : Type y) :=
  History S A × (S × Family Q)
def eligible (m : Machine S A O E) (req : S→A→Family Q)
    (P D : History S A→Prop) (k : Context (History S A) W) (T : W→Prop)
    (i : WitnessIndex S A Q) := Witness m req P D k T i.1 i.2.1 i.2.2
def requirements (i : WitnessIndex S A Q) := i.2.2
theorem image_membership (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop)
    (k : Context (History S A) W) (v : W) :
    Image (scenario m req enabled P D k) v ↔
      ∃h, P h ∧ D h ∧ ∃t R, support m req h.1 h.2=some (t,R) ∧
        Sub R enabled ∧ ∃he:k.defined h, k.eval ⟨h,he⟩=v := by
  constructor
  · rintro ⟨h,_,⟨hp,hd,t,ht⟩,he,hv⟩
    obtain ⟨R,hs,hr⟩ := (gated_success m req enabled h.1 t h.2).mp ht
    exact ⟨h,hp,hd,t,R,hs,hr,he,hv⟩
  · rintro ⟨h,hp,hd,t,R,hs,hr,he,hv⟩
    exact ⟨h,True.intro,⟨hp,hd,t,(gated_success m req enabled h.1 t h.2).mpr
      ⟨R,hs,hr⟩⟩,he,hv⟩
theorem context_incidence (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop)
    (k : Context (History S A) W) (T : W→Prop) :
    (∃v, Image (scenario m req enabled P D k) v ∧ T v) ↔
      Cap (eligible m req P D k T) requirements enabled := by
  constructor
  · rintro ⟨v,hv,ht⟩
    obtain ⟨h,hp,hd,t,R,hs,hr,he,hev⟩ := (image_membership _ _ _ _ _ _ v).mp hv
    exact ⟨(h,t,R),⟨hp,hd,hs,he,hev ▸ ht⟩,hr⟩
  · rintro ⟨⟨h,t,R⟩,⟨hp,hd,hs,he,ht⟩,hr⟩
    exact ⟨k.eval ⟨h,he⟩,(image_membership _ _ _ _ _ _ _).mpr
      ⟨h,hp,hd,t,R,hs,hr,he,rfl⟩,ht⟩
theorem context_impossible (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop)
    (k : Context (History S A) W) (T : W→Prop) :
    (∀v, Image (scenario m req enabled P D k) v → ¬T v) ↔
      ¬Cap (eligible m req P D k T) requirements enabled := by
  rw [← context_incidence]
  constructor
  · rintro h ⟨v,hv,ht⟩; exact h v hv ht
  · intro h v hv ht; exact h ⟨v,hv,ht⟩
theorem admission_mono (m : Machine S A O E) (req : S→A→Family Q)
    (lo hi : Family Q) (hsub : Sub lo hi) (P D : History S A→Prop)
    (h : History S A) : admission m req lo P D h → admission m req hi P D h := by
  rintro ⟨hp,hd,t,ht⟩
  exact ⟨hp,hd,t,success_mono m req lo hi hsub h.1 t h.2 ht⟩
theorem image_mono (m : Machine S A O E) (req : S→A→Family Q)
    (lo hi : Family Q) (hsub : Sub lo hi) (P D : History S A→Prop)
    (k : Context (History S A) W) (v : W) :
    Image (scenario m req lo P D k) v → Image (scenario m req hi P D k) v := by
  rintro ⟨h,hh,hp,he,hv⟩
  exact ⟨h,hh,admission_mono m req lo hi hsub P D h hp,he,hv⟩
theorem context_preserved (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P D : History S A→Prop) (k : Context (History S A) W) :
    (scenario m req enabled P D k).context=k := rfl
theorem view_illegal {H : Type u} (sc : Scenario H W) (h : H)
    (hp : ¬sc.admission h) : view sc h=.illegal :=
  observe_illegal sc.admission sc.context h hp
theorem view_undefined {H : Type u} (sc : Scenario H W) (h : H)
    (hp : sc.admission h) (he : ¬sc.context.defined h) : view sc h=.undefined :=
  observe_undefined sc.admission sc.context h hp he
theorem view_value {H : Type u} (sc : Scenario H W) (h : H)
    (hp : sc.admission h) (he : sc.context.defined h) :
    view sc h=.value (sc.context.eval ⟨h,he⟩) :=
  observe_value sc.admission sc.context h hp he
def fromStart (s : S) (h : History S A) := h.1=s
theorem from_start (m : Machine S A O E) (req : S→A→Family Q)
    (enabled : Family Q) (P : History S A→Prop) (s : S) (h : History S A) :
    admission m req enabled P (fromStart s) h ↔
      P h ∧ h.1=s ∧ ∃t, endpoint (gated m req enabled) h.1 h.2=some t := Iff.rfl
end PermissionContextsV22
