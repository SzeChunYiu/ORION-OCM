import ImageTransportV24
namespace ProfileContextsV24
open PartialContextV15 ContextMapsV17 ImageTransportV24
universe u v w x y
structure Profile (C : Type u) (R : Type v) (Q : Type w) (M : Type x) (H : Type y) where
  capability : C
  resources : R
  provenance : Q
  terminal : M
  history : H
def profile {C R Q M H : Type u} (c : H → C) (r : H → R)
    (q : H → Q) (m : H → M) (h : H) : Profile C R Q M H := ⟨c h,r h,q h,m h,h⟩
def codeContext {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (decode : H → W) : Context H H :=
  ⟨E,fun h => h.val,pullback s decode⟩
def context {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (decode : H → W) : Context H W :=
  ⟨E,fun h => decode h.val,s⟩
theorem decode_post {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (decode : H → W) :
    postcompose (codeContext E s decode) s decode=context E s decode := rfl
theorem decoded_image {H : Type u} {W : Type v} (P E : H → Prop)
    (s : PreorderSpec W) (decode : H → W) (w : W) :
    Image P (context E s decode) w ↔ ∃ h, P h ∧ E h ∧ decode h=w := by
  simp only [image_member,context,exists_prop]
theorem profile_identity {C R Q M H : Type u} (c : H → C) (r : H → R)
    (q : H → Q) (m : H → M) (a b : H) :
    profile c r q m a=profile c r q m b ↔ a=b := by
  constructor
  · exact congrArg Profile.history
  · intro h; cases h; rfl
theorem profile_fields {C R Q M H : Type u} (c : H → C) (r : H → R)
    (q : H → Q) (m : H → M) (h : H) :
    (profile c r q m h).capability=c h ∧
    (profile c r q m h).resources=r h ∧
    (profile c r q m h).provenance=q h ∧
    (profile c r q m h).terminal=m h ∧
    (profile c r q m h).history=h := ⟨rfl,rfl,rfl,rfl,rfl⟩
theorem context_domain {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (f : H → W) : (context E s f).defined=E := rfl
theorem context_eval {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (f : H → W) (h : {h // E h}) :
    (context E s f).eval h=f h.val := rfl
theorem context_order {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (f : H → W) : (context E s f).order=s := rfl
theorem code_eval {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (f : H → W) (h : {h // E h}) :
    (codeContext E s f).eval h=h.val := rfl
theorem decode_observe {H : Type u} {W : Type v} (P E : H → Prop)
    (s : PreorderSpec W) (f : H → W) (h : H) :
    observe P (context E s f) h=outcomeMap f (observe P (codeContext E s f) h) :=
  post_observe P (codeContext E s f) s f h
end ProfileContextsV24
