import ContextMapsV17
import PartialPostcontextV20
namespace ImageTransportV24
open PartialContextV15 ContextMapsV17 PartialPostcontextV20
universe u v w
def Image {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) : W → Prop :=
  Attained P k (fun _ => True)
def Projected {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) (z : Z) :=
  ∃ h, B h ∧ P h ∧ ∃ he : k.defined h, f (k.eval ⟨h,he⟩)=z
theorem projected_post {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop)
    (s : PreorderSpec Z) (f : W → Z) (z : Z) :
    Attained P (postcompose k s f) B z ↔ Projected P k B f z := Iff.rfl
theorem projected_image {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) (z : Z) :
    Projected P k B f z ↔ ∃ w, Attained P k B w ∧ f w=z := by
  constructor
  · rintro ⟨h,hb,hp,he,hz⟩
    exact ⟨k.eval ⟨h,he⟩,⟨h,hb,hp,he,rfl⟩,hz⟩
  · rintro ⟨w,⟨h,hb,hp,he,hw⟩,hz⟩
    exact ⟨h,hb,hp,he,hw ▸ hz⟩
theorem image_member {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (w : W) :
    Image P k w ↔ ∃ h, P h ∧ ∃ he : k.defined h, k.eval ⟨h,he⟩=w := by
  simp only [Image,Attained,true_and]
theorem selected_subset {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) (z : Z) :
    Projected P k B f z → Projected P k (fun _ => True) f z := by
  rintro ⟨h,_,hp,he,hz⟩
  exact ⟨h,True.intro,hp,he,hz⟩
theorem selected_iff {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) :
    (∀ z, Projected P k B f z ↔ Projected P k (fun _ => True) f z) ↔
    (∀ h, P h → ∀ he : k.defined h,
      ∃ b, B b ∧ P b ∧ ∃ hb : k.defined b,
        f (k.eval ⟨b,hb⟩)=f (k.eval ⟨h,he⟩)) := by
  constructor
  · intro hi h hp he
    exact (hi _).mpr ⟨h,True.intro,hp,he,rfl⟩
  · intro cover z
    constructor
    · exact selected_subset P k B f z
    · rintro ⟨h,_,hp,he,hz⟩
      obtain ⟨b,hb,bp,be,eq⟩ := cover h hp he
      exact ⟨b,hb,bp,be,eq.trans hz⟩
theorem terminal_sufficient {H : Type u} {W : Type v} {Z M : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop)
    (f : W → Z) (terminal : H → M) (g : M → Z)
    (factor : ∀ h, P h → ∀ he : k.defined h, f (k.eval ⟨h,he⟩)=g (terminal h))
    (cover : ∀ h, P h → k.defined h →
      ∃ b, B b ∧ P b ∧ k.defined b ∧ terminal b=terminal h) :
    ∀ z, Projected P k B f z ↔ Projected P k (fun _ => True) f z := by
  apply (selected_iff P k B f).mpr
  intro h hp he
  obtain ⟨b,hb,bp,be,ht⟩ := cover h hp he
  exact ⟨b,hb,bp,be,(factor b bp be).trans ((congrArg g ht).trans (factor h hp he).symm)⟩
theorem injective_boundary {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z)
    (inj : ∀ h b, P h → P b → ∀ hh : k.defined h, ∀ hb : k.defined b,
      f (k.eval ⟨h,hh⟩)=f (k.eval ⟨b,hb⟩) → h=b) :
    (∀ z, Projected P k B f z ↔ Projected P k (fun _ => True) f z) ↔
      ∀ h, P h → k.defined h → B h := by
  rw [selected_iff]
  constructor
  · intro cover h hp he
    obtain ⟨b,hb,bp,be,eq⟩ := cover h hp he
    exact (inj b h bp hp be he eq) ▸ hb
  · intro cover h hp he
    exact ⟨h,cover h hp he,hp,he,rfl⟩
end ImageTransportV24
