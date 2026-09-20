import ConstructorBindingsV22
namespace PermissionControlsV22
open ContinuationV8 BudgetResidualV21
open PermissionSetsV22 PermissionMachineV22 PermissionExecutionV22
open PermissionIncidenceV22 PermissionMinimalityV22
def samePayload : Machine Bool Unit Bool Unit := ⟨id,fun s _ => some ((),s)⟩
def edgeRequirements (s : Bool) (_a : Unit) : Family Bool := single s
theorem state_sensitive_payload :
    (gated samePayload edgeRequirements (single false)).next false ()=some ((),false) ∧
    (gated samePayload edgeRequirements (single false)).next true ()=none := by
  constructor
  · exact gated_present _ _ _ false false () () rfl (sub_refl _)
  · apply gated_denied _ _ _ true true () () rfl
    intro h
    have hh : true=false := h true rfl
    cases hh
def singletonSupports (h : Bool) : Family Bool := single h
theorem private_is_insufficient :
    Private (fun _ : Bool => True) singletonSupports (fun _ => True) (single false) ∧
    ¬Blocks (fun _ : Bool => True) singletonSupports (fun _ => True) (single false) := by
  simp [Private,Blocks,Cap,singletonSupports,PermissionSetsV22.Sub,single,diff,empty]
theorem empty_private_is_insufficient :
    Private (fun _ : Bool => True) singletonSupports (fun _ => True) empty ∧
    ¬Blocks (fun _ : Bool => True) singletonSupports (fun _ => True) empty := by
  simp [Private,Blocks,Cap,singletonSupports,PermissionSetsV22.Sub,single,diff,empty]
theorem baseline_not_identifying :
    ¬Cap (fun _ : Unit => True) (fun _ => single false) empty ∧
    ¬Cap (fun _ : Unit => True) (fun _ => single true) empty ∧
    Cap (fun _ : Unit => True) (fun _ => single false) (single false) ∧
    ¬Cap (fun _ : Unit => True) (fun _ => single true) (single false) := by
  simp [Private,Blocks,Cap,singletonSupports,PermissionSetsV22.Sub,single,diff,empty]
theorem admitted_baseline {H : Type u} {Q : Type v} (W : H→Prop) (R : H→Family Q)
    (U S0 : Family Q) (h : Cap W R S0) :
    Minimal (Enabling W R U S0) empty := by
  refine ⟨⟨fun _ hh => False.elim hh,?_⟩,?_⟩
  · exact cap_mono W R S0 (union S0 empty) (fun _ hh => Or.inl hh) h
  · intro C hC _
    exact sub_antisymm hC (fun _ hh => False.elim hh)
def tail (n : Nat) : Family Nat := fun q => n≤q
theorem no_minimal_tail_enabler (B : Family Nat) :
    ¬Minimal (Cap (fun _ : Nat => True) tail) B := by
  rintro ⟨⟨n,_,hn⟩,hm⟩
  have hnext : Sub (tail (n+1)) B := by
    intro q hq
    exact hn q (Nat.le_trans (Nat.le_succ n) hq)
  have he := hm (tail (n+1)) hnext ⟨n+1,True.intro,sub_refl _⟩
  have hBn := hn n (Nat.le_refl n)
  have hbad : tail (n+1) n := he ▸ hBn
  change n+1≤n at hbad
  omega
theorem no_minimal_tail_blocker (B : Family Nat) :
    ¬Minimal (Blocks (fun _ : Nat => True) tail (fun _ => True)) B := by
  intro hm
  obtain ⟨hb,hp⟩ := (minimal_blocker _ _ _ B).mp hm
  obtain ⟨b,_,hBb⟩ := (blocks_iff_hits _ _ _ B).mp hb 0 True.intro
    (fun _ _ => True.intro)
  obtain ⟨n,_,_,hpriv⟩ := hp b hBb
  obtain ⟨q,hq,hBq⟩ := (blocks_iff_hits _ _ _ B).mp hb (max n (b+1)) True.intro
    (fun _ _ => True.intro)
  have hq' : max n (b+1)≤q := hq
  have hnq : n≤q := by omega
  have he := (hpriv q).mp ⟨hnq,hBq⟩
  omega
theorem tail_binding (n q : Nat) : tail n q ↔ n≤q := Iff.rfl
theorem same_payload_next (s : Bool) (a : Unit) :
    samePayload.next s a=some ((),s) := rfl
theorem same_payload_obs (s : Bool) : samePayload.obs s=s := rfl
theorem edge_requirements_binding (s q : Bool) (a : Unit) :
    edgeRequirements s a q ↔ q=s := Iff.rfl
theorem singleton_supports_binding (h q : Bool) : singletonSupports h q ↔ q=h := Iff.rfl
end PermissionControlsV22
