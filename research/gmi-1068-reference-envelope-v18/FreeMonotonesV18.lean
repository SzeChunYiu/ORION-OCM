import AdmissibilityV5
import PartialContextV15
namespace FreeMonotonesV18
open FoundationV5 PartialContextV15
universe u v
def Can (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (a b : C.Obj) : Prop :=
  ∃ f : C.Hom a b, F f
theorem can_iff (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (a b : C.Obj) :
    Can C F a b ↔ ∃ f : C.Hom a b, F f := Iff.rfl
theorem can_refl (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (hF : Closed C F) (a : C.Obj) :
    Can C F a a := ⟨C.ident a,hF.1 a⟩
theorem can_trans (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (hF : Closed C F)
    {a b c : C.Obj} (hab : Can C F a b) (hbc : Can C F b c) : Can C F a c := by
  obtain ⟨f,hf⟩ := hab
  obtain ⟨g,hg⟩ := hbc
  exact ⟨C.comp f g,hF.2 f g hf hg⟩
def resourceOrder (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (hF : Closed C F) :
    PreorderSpec C.Obj where
  le a b := Can C F b a
  refl := can_refl C F hF
  trans := fun hab hbc => can_trans C F hF hbc hab
def boolOrder : PreorderSpec Bool where
  le a b := a=true → b=true
  refl _ := id
  trans h k := k ∘ h
noncomputable def target (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z a : C.Obj) : Bool := by
  classical
  exact if Can C F a z then true else false
theorem target_true (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z a : C.Obj) :
    target C F z a=true ↔ Can C F a z := by
  classical
  simp [target]
noncomputable def targetContext (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z : C.Obj) : Context C.Obj Bool where
  defined _ := True
  eval a := target C F z a.val
  order := boolOrder
theorem target_context_defined (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z a : C.Obj) :
    (targetContext C F z).defined a := True.intro
theorem target_context_value (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z a : C.Obj) :
    (targetContext C F z).eval ⟨a,True.intro⟩=true ↔
      ∃ f : C.Hom a z, F f := target_true C F z a
theorem target_context_observe (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (z a : C.Obj) :
    observe (fun _ => True) (targetContext C F z) a=.value (target C F z a) := by
  exact observe_value _ _ a True.intro True.intro
theorem target_monotone (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (hF : Closed C F)
    {a b : C.Obj} (hab : Can C F a b) (z : C.Obj) :
    boolOrder.le (target C F z b) (target C F z a) := by
  intro hb
  exact (target_true C F z a).mpr
    (can_trans C F hF hab ((target_true C F z b).mp hb))
theorem target_family_complete (C : ProcCategory.{u,v})
    (F : {a b : C.Obj} → C.Hom a b → Prop) (hF : Closed C F) (a b : C.Obj) :
    Can C F a b ↔
      ∀ z, boolOrder.le ((targetContext C F z).eval ⟨b,True.intro⟩)
                       ((targetContext C F z).eval ⟨a,True.intro⟩) := by
  constructor
  · intro h z
    exact target_monotone C F hF h z
  · intro h
    exact (target_true C F b a).mp
      (h b ((target_true C F b b).mpr (can_refl C F hF b)))
end FreeMonotonesV18
