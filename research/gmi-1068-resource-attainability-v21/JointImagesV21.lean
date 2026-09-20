import HistoryContextsV21
namespace JointImagesV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open HistoryContextsV21
universe u v w x y
def Joint {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (c : Nat) (v : W) :=
  ∃ h, P h ∧ H h ∧ ∃ t, weighted natAdd m cost h.1 h.2=some (t,c) ∧
    ∃ he : k.defined h, k.eval ⟨h,he⟩=v
theorem joint_filtration {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) (v : W) :
    Image (bounded m cost P H k b) v ↔ ∃ c, c≤b ∧ Joint m cost P H k c v := by
  rw [image_iff]
  constructor
  · rintro ⟨h,⟨hp,hh,t,c,hc,hcb⟩,he,hev⟩
    exact ⟨c,hcb,h,hp,hh,t,hc,he,hev⟩
  · rintro ⟨c,hcb,h,hp,hh,t,hc,he,hev⟩
    exact ⟨h,⟨hp,hh,t,c,hc,hcb⟩,he,hev⟩
theorem joint_unrestricted {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (v : W) :
    Image (unrestricted m cost P H k) v ↔ ∃ c, Joint m cost P H k c v := by
  rw [image_iff]
  constructor
  · rintro ⟨h,⟨hp,hh,t,c,hc⟩,he,hev⟩
    exact ⟨c,h,hp,hh,t,hc,he,hev⟩
  · rintro ⟨c,h,hp,hh,t,hc,he,hev⟩
    exact ⟨h,⟨hp,hh,t,c,hc⟩,he,hev⟩
theorem all_budget_union {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (v : W) :
    Image (unrestricted m cost P H k) v ↔ ∃ b, Image (bounded m cost P H k b) v := by
  constructor
  · intro hv
    obtain ⟨c,hc⟩ := (joint_unrestricted m cost P H k v).mp hv
    exact ⟨c,(joint_filtration m cost P H k c v).mpr ⟨c,Nat.le_refl c,hc⟩⟩
  · rintro ⟨b,hb⟩
    exact bounded_subset m cost P H k b v hb
def Capability {H : Type u} {W : Type v} (sc : Scenario H W) (G : W → Prop) :=
  ∃ v, Image sc v ∧ G v
def TargetCosts {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (c : Nat) :=
  ∃ v, Joint m cost P H k c v ∧ G v
theorem capability_joint {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (b : Nat) :
    Capability (bounded m cost P H k b) G ↔
      ∃ c, c≤b ∧ TargetCosts m cost P H k G c := by
  constructor
  · rintro ⟨v,hv,hg⟩
    obtain ⟨c,hcb,hc⟩ := (joint_filtration m cost P H k b v).mp hv
    exact ⟨c,hcb,v,hc,hg⟩
  · rintro ⟨c,hcb,v,hc,hg⟩
    exact ⟨v,(joint_filtration m cost P H k b v).mpr ⟨c,hcb,hc⟩,hg⟩
theorem capability_mono {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (G : W → Prop) (lo hi : Nat) (hle : lo≤hi) :
    Capability (bounded m cost P H k lo) G → Capability (bounded m cost P H k hi) G := by
  rintro ⟨v,hv,hg⟩
  exact ⟨v,bounded_mono m cost P H k lo hi hle v hv,hg⟩
def projectContext {H : Type u} {W : Type v} {R : Type w}
    (k : Context H W) (rho : W → R) (r : PreorderSpec R) : Context H R :=
  ⟨k.defined,fun h => rho (k.eval h),r⟩
def projectScenario {H : Type u} {W : Type v} {R : Type w}
    (sc : Scenario H W) (rho : W → R) (r : PreorderSpec R) : Scenario H R :=
  ⟨sc.admission,projectContext sc.context rho r⟩
theorem projection_image {H : Type u} {W : Type v} {R : Type w}
    (sc : Scenario H W) (rho : W → R) (r : PreorderSpec R) (z : R) :
    Image (projectScenario sc rho r) z ↔ ∃ v, Image sc v ∧ rho v=z := by
  simp only [image_iff]
  constructor
  · rintro ⟨h,hp,he,hz⟩
    exact ⟨sc.context.eval ⟨h,he⟩,⟨h,hp,he,rfl⟩,hz⟩
  · rintro ⟨v,⟨h,hp,he,hv⟩,hz⟩
    exact ⟨h,hp,he,by change rho (sc.context.eval ⟨h,he⟩)=z; rw [hv,hz]⟩
end JointImagesV21
