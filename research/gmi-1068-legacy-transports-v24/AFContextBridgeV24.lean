import AFErasureV24
namespace AFContextBridgeV24
open PartialContextV15 ProfileContextsV24 AFErasureV24 ImageTransportV24
universe u
noncomputable def oldContext {M A C Q : Type u}
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (s : PreorderSpec (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A))) :
    Context (M × List A) (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)) :=
  context (fun _ => True) s (oldProfile cap initial external oracle tags)
noncomputable def fullContext {M E A C Q : Type u}
    (label : E → A) (D : M × List E → Prop)
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (s : PreorderSpec (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A))) :
    Context (M × List E) (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)) :=
  context D s (fullProjection label cap initial external oracle tags)
theorem full_erasure_image {M E A C Q : Type u}
    (label : E → A) (P D : M × List E → Prop)
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (s : PreorderSpec (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)))
    (w : Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)) :
    Image P (fullContext label D cap initial external oracle tags s) w ↔
    Image (fun record => ∃ h, P h ∧ D h ∧ erase label h=record)
      (oldContext cap initial external oracle tags s) w := by
  simp only [fullContext,oldContext,decoded_image]
  constructor
  · rintro ⟨h,hp,hd,hw⟩
    exact ⟨erase label h,⟨h,hp,hd,rfl⟩,True.intro,hw⟩
  · rintro ⟨record,⟨h,hp,hd,he⟩,_,hw⟩
    subst record
    exact ⟨h,hp,hd,hw⟩
theorem selected_old_image {M A C Q : Type u}
    (B : M × List A → Prop) (cap : M → C) (initial external oracle : Q)
    (tags : A → Q → Prop)
    (s : PreorderSpec (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)))
    (w : Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)) :
    Image B (oldContext cap initial external oracle tags s) w ↔
    ∃ record, B record ∧ oldProfile cap initial external oracle tags record=w := by
  simp only [oldContext,decoded_image,true_and]
theorem full_binding {M E A C Q : Type u}
    (label : E → A) (D : M × List E → Prop)
    (cap : M → C) (initial external oracle : Q) (tags : A → Q → Prop)
    (s : PreorderSpec (Profile C (Nat × Bool × Bool) (Q → Prop) M (List A))) :
    fullContext label D cap initial external oracle tags s =
    context D s (fun h => oldProfile cap initial external oracle tags (erase label h)) := rfl
end AFContextBridgeV24
