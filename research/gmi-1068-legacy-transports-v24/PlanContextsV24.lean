import ProfileContextsV24
namespace PlanContextsV24
open PartialContextV15 ImageTransportV24
universe u v w
def valueOrder {K : Type u} {L : Type v} (r : PreorderSpec L) : PreorderSpec (K × L) where
  le a b := r.le b.2 a.2
  refl _ := r.refl _
  trans h k := r.trans k h
def context {K : Type u} {L : Type v} (E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) : Context K (K × L) :=
  ⟨E,fun q => (q.val,loss q),valueOrder r⟩
def Feasible {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (eps : L) (q : K) :=
  U q ∧ P q ∧ ∃ he : E q, r.le (loss ⟨q,he⟩) eps
theorem feasible_image {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (eps : L) (q : K) :
    Feasible U P E loss r eps q ↔
    ∃ l, Image (fun q => U q ∧ P q) (context E loss r) (q,l) ∧ r.le l eps := by
  constructor
  · rintro ⟨hu,hp,he,hl⟩
    exact ⟨loss ⟨q,he⟩,(image_member _ _ _).mpr ⟨q,⟨hu,hp⟩,he,rfl⟩,hl⟩
  · rintro ⟨l,hi,hl⟩
    obtain ⟨p,⟨hu,hp⟩,he,hv⟩ := (image_member _ _ _).mp hi
    have hq := congrArg Prod.fst hv
    have hv' := congrArg Prod.snd hv
    change p=q at hq
    subst p
    change loss ⟨q,he⟩=l at hv'
    exact ⟨hu,hp,he,hv'.symm ▸ hl⟩
def identityContext {K : Type u} : Context K K :=
  ⟨fun _ => True,fun q => q.val,⟨Eq,fun _ => rfl,Eq.trans⟩⟩
theorem identity_feasible {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (eps : L) (q : K) :
    Image (Feasible U P E loss r eps) identityContext q ↔
    Feasible U P E loss r eps q := by
  simp only [image_member,identityContext,exists_prop,true_and]
  constructor
  · rintro ⟨p,hp,hq⟩; exact hq ▸ hp
  · intro h; exact ⟨q,h,rfl⟩
theorem total_specialization {K : Type u} {L : Type v} (loss : K → L)
    (r : PreorderSpec L) (eps : L) (q : K) :
    Feasible (fun _ => True) (fun _ => True) (fun _ => True)
      (fun q => loss q.val) r eps q ↔ r.le (loss q) eps := by
  simp [Feasible]
theorem context_binding {K : Type u} {L : Type v} (E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) :
    (context E loss r).defined=E ∧
    (context E loss r).eval=(fun q => (q.val,loss q)) ∧
    (context E loss r).order=valueOrder r := ⟨rfl,rfl,rfl⟩
theorem illegal {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (q : K) (h : ¬(U q ∧ P q)) :
    observe (fun q => U q ∧ P q) (context E loss r) q=.illegal :=
  observe_illegal _ _ _ h
theorem undefined {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (q : K)
    (h : U q ∧ P q) (he : ¬E q) :
    observe (fun q => U q ∧ P q) (context E loss r) q=.undefined :=
  observe_undefined _ _ _ h he
theorem value {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (q : K)
    (h : U q ∧ P q) (he : E q) :
    observe (fun q => U q ∧ P q) (context E loss r) q=.value (q,loss ⟨q,he⟩) :=
  observe_value (fun q => U q ∧ P q) (context E loss r) q h he
end PlanContextsV24
