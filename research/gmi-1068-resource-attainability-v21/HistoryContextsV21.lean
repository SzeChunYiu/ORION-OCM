import SuccessfulResponseV21
import PartialPostcontextV20
namespace HistoryContextsV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open BudgetResidualV21 PartialPostcontextV20
universe u v w x y
abbrev History (S : Type u) (A : Type v) := S × List A
structure Scenario (H : Type u) (W : Type v) where
  admission : H → Prop
  context : Context H W
def Physical {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (h : History S A) :=
  ∃ t c, weighted natAdd m cost h.1 h.2=some (t,c)
def Within {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (b : Nat) (h : History S A) :=
  ∃ t c, weighted natAdd m cost h.1 h.2=some (t,c) ∧ c≤b
def unrestricted {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) : Scenario (History S A) W :=
  ⟨fun h => P h ∧ H h ∧ Physical m cost h,k⟩
def bounded {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) : Scenario (History S A) W :=
  ⟨fun h => P h ∧ H h ∧ Within m cost b h,k⟩
def Image {H : Type u} {W : Type v} (sc : Scenario H W) :=
  PartialPostcontextV20.Attained sc.admission sc.context (fun _ => True)
noncomputable def view {H : Type u} {W : Type v} (sc : Scenario H W) (h : H) :=
  observe sc.admission sc.context h
theorem image_iff {H : Type u} {W : Type v} (sc : Scenario H W) (v : W) :
    Image sc v ↔ ∃ h, sc.admission h ∧ ∃ he : sc.context.defined h,
      sc.context.eval ⟨h,he⟩=v := by
  simp only [Image,PartialPostcontextV20.Attained,true_and]
theorem image_mono {H : Type u} {W : Type v} (k : Context H W) (P Q : H → Prop)
    (hsub : ∀ h, P h → Q h) : ∀ v, Image ⟨P,k⟩ v → Image ⟨Q,k⟩ v := by
  intro v hv
  obtain ⟨h,hp,he,hev⟩ := (image_iff _ v).mp hv
  exact (image_iff _ v).mpr ⟨h,hsub h hp,he,hev⟩
theorem selector_mono {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H K : History S A → Prop)
    (k : Context (History S A) W) (hsub : ∀ h, H h → K h) :
    ∀ v, Image (unrestricted m cost P H k) v → Image (unrestricted m cost P K k) v :=
  image_mono k _ _ (fun h hh => ⟨hh.1,hsub h hh.2.1,hh.2.2⟩)
theorem within_operational {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (b : Nat) (h : History S A) :
    Within m cost b h ↔ ∃ t r, budgetEndpoint m cost h.1 b h.2=some (t,r) := by
  constructor
  · rintro ⟨t,c,hc,hcb⟩
    exact ⟨t,b-c,(residual_iff m cost h.2 h.1 t b (b-c)).mpr ⟨c,hc,hcb,rfl⟩⟩
  · rintro ⟨t,r,hr⟩
    obtain ⟨c,hc,hcb,_⟩ := (residual_iff m cost h.2 h.1 t b r).mp hr
    exact ⟨t,c,hc,hcb⟩
theorem within_mono {S : Type u} {A : Type v} {O : Type w} {E : Type x}
    (m : Machine S A O E) (cost : E → Nat) (lo hi : Nat) (hle : lo≤hi)
    (h : History S A) : Within m cost lo h → Within m cost hi h := by
  intro hl
  obtain ⟨t,r,hr⟩ := (within_operational m cost lo h).mp hl
  obtain ⟨c,_,_,_,hhi⟩ := larger_budget m cost h.1 t h.2 lo hi r hle hr
  exact (within_operational m cost hi h).mpr ⟨t,hi-c,hhi⟩
theorem bounded_subset {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) :
    ∀ v, Image (bounded m cost P H k b) v → Image (unrestricted m cost P H k) v := by
  apply image_mono k
  rintro h ⟨hp,hh,t,c,hc,_⟩
  exact ⟨hp,hh,t,c,hc⟩
theorem bounded_mono {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (lo hi : Nat) (hle : lo≤hi) :
    ∀ v, Image (bounded m cost P H k lo) v → Image (bounded m cost P H k hi) v :=
  image_mono k _ _ (fun h hh => ⟨hh.1,hh.2.1,within_mono m cost lo hi hle h hh.2.2⟩)
theorem bounded_context {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (b : Nat) :
    (bounded m cost P H k b).context=k := rfl
theorem unrestricted_context {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) :
    (unrestricted m cost P H k).context=k := rfl
theorem view_illegal {H : Type u} {W : Type v} (sc : Scenario H W)
    (h : H) (hp : ¬sc.admission h) : view sc h=.illegal :=
  observe_illegal _ _ h hp
theorem view_undefined {H : Type u} {W : Type v} (sc : Scenario H W)
    (h : H) (hp : sc.admission h) (he : ¬sc.context.defined h) :
    view sc h=.undefined := observe_undefined _ _ h hp he
theorem view_value {H : Type u} {W : Type v} (sc : Scenario H W)
    (h : H) (hp : sc.admission h) (he : sc.context.defined h) :
    view sc h=.value (sc.context.eval ⟨h,he⟩) := observe_value _ _ h hp he
end HistoryContextsV21
