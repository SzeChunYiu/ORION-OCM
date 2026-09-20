import JointImagesV21
namespace CapabilityThresholdV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open HistoryContextsV21 JointImagesV21
universe u v w x y
def Least (C : Nat → Prop) (n : Nat) := C n ∧ ∀ m, C m → n≤m
theorem least_exists (C : Nat → Prop) (hc : ∃ n, C n) : ∃ n, Least C n := by
  classical
  have aux : ∀ n, C n → ∃ d, Least C d := by
    intro n
    induction n using Nat.strongRecOn with
    | ind n ih =>
      intro hn
      by_cases hs : ∃ m, m<n ∧ C m
      · obtain ⟨m,hm,hc⟩ := hs
        exact ih m hm hc
      · exact ⟨n,hn,fun m hm => by
          have hnot : ¬m<n := fun hlt => hs ⟨m,hlt,hm⟩
          omega⟩
  obtain ⟨n,hn⟩ := hc
  exact aux n hn
theorem least_unique {C : Nat → Prop} {n m : Nat}
    (hn : Least C n) (hm : Least C m) : n=m :=
  Nat.le_antisymm (hn.2 m hm.1) (hm.2 n hn.1)
noncomputable def threshold (C : Nat → Prop) : Option Nat := by
  classical
  exact if hc : ∃ n, C n then some (Classical.choose (least_exists C hc)) else none
def ThresholdSpec (C : Nat → Prop) : Option Nat → Prop
  | none => ∀ n, ¬C n
  | some n => Least C n
theorem threshold_spec (C : Nat → Prop) : ThresholdSpec C (threshold C) := by
  classical
  by_cases hc : ∃ n, C n
  · simp only [threshold,dif_pos hc,ThresholdSpec]
    exact Classical.choose_spec (least_exists C hc)
  · simp only [threshold,dif_neg hc,ThresholdSpec]
    exact fun n hn => hc ⟨n,hn⟩
theorem threshold_none (C : Nat → Prop) :
    threshold C=none ↔ ¬∃ n, C n := by
  classical
  by_cases hc : ∃ n, C n <;> simp [threshold,hc]
theorem threshold_some (C : Nat → Prop) (n : Nat) :
    threshold C=some n ↔ Least C n := by
  constructor
  · intro hn
    have hs := threshold_spec C
    rw [hn] at hs
    exact hs
  · intro hn
    cases he : threshold C with
    | none =>
      have hs := threshold_spec C
      rw [he] at hs
      exact False.elim (hs n hn.1)
    | some m =>
      have hs := threshold_spec C
      rw [he] at hs
      have hmn := least_unique hs hn
      subst m
      rfl
theorem cutoff (C : Nat → Prop) (b : Nat) :
    (∃ c, c≤b ∧ C c) ↔ ∃ n, threshold C=some n ∧ n≤b := by
  constructor
  · rintro ⟨c,hcb,hc⟩
    obtain ⟨n,hn⟩ := least_exists C ⟨c,hc⟩
    exact ⟨n,(threshold_some C n).mpr hn,Nat.le_trans (hn.2 c hc) hcb⟩
  · rintro ⟨n,hn,hnb⟩
    exact ⟨n,hnb,((threshold_some C n).mp hn).1⟩
theorem capability_cutoff {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (b : Nat) :
    Capability (bounded m cost P H k b) G ↔
      ∃ n, threshold (TargetCosts m cost P H k G)=some n ∧ n≤b := by
  rw [capability_joint,cutoff]
theorem threshold_attained {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (n : Nat)
    (hn : threshold (TargetCosts m cost P H k G)=some n) :
    ∃ h, P h ∧ H h ∧ ∃ t, weighted natAdd m cost h.1 h.2=some (t,n) ∧
      ∃ he : k.defined h, G (k.eval ⟨h,he⟩) := by
  obtain ⟨v,⟨h,hp,hh,t,ht,he,hv⟩,hg⟩ :=
    ((threshold_some (TargetCosts m cost P H k G) n).mp hn).1
  exact ⟨h,hp,hh,t,ht,he,hv ▸ hg⟩
theorem value_cutoff {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (v : W) (b : Nat) :
    Image (bounded m cost P H k b) v ↔
      ∃ n, threshold (TargetCosts m cost P H k (fun z => z=v))=some n ∧ n≤b := by
  have hs : Capability (bounded m cost P H k b) (fun z => z=v) ↔
      Image (bounded m cost P H k b) v := by
    constructor
    · rintro ⟨z,hz,hzv⟩
      exact hzv ▸ hz
    · intro hv
      exact ⟨v,hv,rfl⟩
  exact hs.symm.trans (capability_cutoff m cost P H k (fun z => z=v) b)
end CapabilityThresholdV21
