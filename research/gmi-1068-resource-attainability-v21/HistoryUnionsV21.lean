import JointImagesV21
import Attainability
namespace HistoryUnionsV21
open ContinuationV8 PartialContextV15 OrderedCostsV21 WeightedExecutionV21
open HistoryContextsV21 JointImagesV21
universe u v w x y
def fromStart {S : Type u} {A : Type v} (s : S) (h : History S A) := h.1=s
def horizon {S : Type u} {A : Type v} (H : History S A → Prop)
    (n : Nat) (h : History S A) := H h ∧ h.2.length≤n
def fromScenario {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (s : S) :=
  unrestricted m cost P (fun h => fromStart s h ∧ H h) k
theorem from_image {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (s : S) (v : W) :
    Image (fromScenario m cost P H k s) v ↔
      ∃ word, P (s,word) ∧ H (s,word) ∧ Physical m cost (s,word) ∧
        ∃ he : k.defined (s,word), k.eval ⟨(s,word),he⟩=v := by
  rw [image_iff]
  constructor
  · rintro ⟨⟨t,word⟩,⟨hp,⟨ht,hh⟩,hphys⟩,he,hv⟩
    change t=s at ht
    subst t
    exact ⟨word,hp,hh,hphys,he,hv⟩
  · rintro ⟨word,hp,hh,hphys,he,hv⟩
    exact ⟨(s,word),⟨hp,⟨rfl,hh⟩,hphys⟩,he,hv⟩
theorem all_horizon_union {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (v : W) :
    Image (unrestricted m cost P H k) v ↔
      ∃ n, Image (unrestricted m cost P (horizon H n) k) v := by
  constructor
  · intro hv
    obtain ⟨h,⟨hp,hh,hphys⟩,he,hev⟩ := (image_iff _ v).mp hv
    exact ⟨h.2.length,(image_iff _ v).mpr
      ⟨h,⟨hp,⟨hh,Nat.le_refl _⟩,hphys⟩,he,hev⟩⟩
  · rintro ⟨n,hn⟩
    exact selector_mono m cost P (horizon H n) H k (fun _ hh => hh.1) v hn
theorem horizon_mono {S : Type u} {A : Type v} {O : Type w} {E : Type x} {W : Type y}
    (m : Machine S A O E) (cost : E → Nat) (P H : History S A → Prop)
    (k : Context (History S A) W) (lo hi : Nat) (hle : lo≤hi) :
    ∀ v, Image (unrestricted m cost P (horizon H lo) k) v →
      Image (unrestricted m cost P (horizon H hi) k) v :=
  selector_mono m cost P _ _ k (fun _ hh => ⟨hh.1,Nat.le_trans hh.2 hle⟩)
noncomputable def ambient {H : Type u} {W : Type v} (k : Context H W) :=
  PartialPostcontextV20.valueMap (fun _ => True) k
theorem original_attain_bridge {H : Type u} {W : Type v} (sc : Scenario H W) (v : W) :
    Attain sc.admission (ambient sc.context) v ↔ Image sc v := by
  simp only [Attain,ambient,PartialPostcontextV20.valueMap_iff,true_and,image_iff]
theorem v20_attained_bridge {H : Type u} {W : Type v} (sc : Scenario H W) (v : W) :
    Image sc v ↔ PartialPostcontextV20.Attained sc.admission sc.context (fun _ => True) v :=
  Iff.rfl
theorem v15_active_bridge {H : Type u} {W : Type v} (sc : Scenario H W) (v : W) :
    Image sc v ↔ ∃ h : Active sc.admission sc.context,
      restrictedEval sc.admission sc.context h=v := by
  rw [image_iff]
  constructor
  · rintro ⟨h,hp,he,hv⟩
    exact ⟨⟨h,hp,he⟩,hv⟩
  · rintro ⟨h,hv⟩
    exact ⟨h.val,h.property.1,h.property.2,hv⟩
theorem original_maximal_bridge {W : Type u} (r : PreorderSpec W)
    (S : W → Prop) (w : W) :
    _root_.Maximal r.le S w ↔ FrontierOrderV20.Maximal r S w := by
  constructor
  · rintro ⟨hs,hm⟩
    exact ⟨hs,fun y hy hwy => Classical.byContradiction (fun hn => hm y hy ⟨hwy,hn⟩)⟩
  · rintro ⟨hs,hm⟩
    exact ⟨hs,fun y hy ⟨hwy,hny⟩ => hny (hm y hy hwy)⟩
end HistoryUnionsV21
