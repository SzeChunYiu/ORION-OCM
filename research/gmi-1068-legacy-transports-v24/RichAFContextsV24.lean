import AFContextBridgeV24
namespace RichAFContextsV24
open PartialContextV15 ContextMapsV17 ImageTransportV24 ProfileContextsV24 AFErasureV24 AFContextBridgeV24
universe u
abbrev OldValue (M A C Q : Type u) :=
  Profile C (Nat × Bool × Bool) (Q → Prop) M (List A)
variable {M E A C Q : Type u}
variable (label : E → A) (D : M × List E → Prop) (cap : M → C)
variable (initial external oracle : Q) (tags : A → Q → Prop)
variable (s : PreorderSpec (OldValue M A C Q))
noncomputable def richContext :
    Context (M × List E) ((M × List E) × OldValue M A C Q) :=
  context D ⟨Eq,fun _ => rfl,Eq.trans⟩
    (fun h => (h,fullProjection label cap initial external oracle tags h))
theorem rich_binding :
    richContext label D cap initial external oracle tags =
    context D ⟨Eq,fun _ => rfl,Eq.trans⟩
      (fun h => (h,oldProfile cap initial external oracle tags (erase label h))) := rfl
theorem projection_post :
    postcompose (richContext label D cap initial external oracle tags) s Prod.snd =
    fullContext label D cap initial external oracle tags s := rfl
theorem rich_image (P : M × List E → Prop) (w : (M × List E) × OldValue M A C Q) :
    Image P (richContext label D cap initial external oracle tags) w ↔
    ∃ h, P h ∧ D h ∧
      (h,oldProfile cap initial external oracle tags (erase label h))=w := by
  exact decoded_image P D _ _ w
theorem projected_image (P : M × List E → Prop) (w : OldValue M A C Q) :
    (∃ z, Image P (richContext label D cap initial external oracle tags) z ∧ z.2=w) ↔
    Image P (fullContext label D cap initial external oracle tags s) w := by
  constructor
  · rintro ⟨z,hz,hw⟩
    obtain ⟨h,hp,hd,he⟩ := (rich_image label D cap initial external oracle tags P z).mp hz
    apply (decoded_image P D s _ w).mpr
    exact ⟨h,hp,hd,(congrArg Prod.snd he).trans hw⟩
  · intro hw
    obtain ⟨h,hp,hd,he⟩ := (decoded_image P D s _ w).mp hw
    exact ⟨(h,w),(rich_image label D cap initial external oracle tags P (h,w)).mpr
      ⟨h,hp,hd,congrArg (fun z => (h,z)) he⟩,rfl⟩
theorem projected_observe (P : M × List E → Prop) (h : M × List E) :
    observe P (fullContext label D cap initial external oracle tags s) h =
    outcomeMap Prod.snd (observe P (richContext label D cap initial external oracle tags) h) :=
  post_observe P (richContext label D cap initial external oracle tags) s Prod.snd h
theorem rich_identity (a b : M × List E) :
    (a,fullProjection label cap initial external oracle tags a)=
    (b,fullProjection label cap initial external oracle tags b) ↔ a=b := by
  constructor
  · exact congrArg Prod.fst
  · intro h; cases h; rfl
end RichAFContextsV24
