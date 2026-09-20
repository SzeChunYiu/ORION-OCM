import Std
namespace PartialContextV15
universe u v
structure PreorderSpec (W : Type v) where
  le : W → W → Prop
  refl : ∀ w, le w w
  trans : ∀ {a b c}, le a b → le b c → le a c
structure PosetSpec (W : Type v) extends PreorderSpec W where
  antisymm : ∀ {a b}, le a b → le b a → a=b
structure Context (H : Type u) (W : Type v) where
  defined : H → Prop
  eval : {h : H // defined h} → W
  order : PreorderSpec W
structure RelativeDomain {H : Type u} (P : H → Prop) where
  defined : H → Prop
  admitted : ∀ h, defined h → P h
def RelativeDomain.Carrier {H : Type u} {P : H → Prop} (d : RelativeDomain P) :=
  {h : H // d.defined h}
def relativeDomain {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) :
    RelativeDomain P := ⟨fun h => P h ∧ k.defined h, fun _ h => h.1⟩
abbrev Active {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) :=
  (relativeDomain P k).Carrier
def restrictedEval {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W)
    (h : Active P k) : W := k.eval ⟨h.val,h.property.2⟩
theorem restriction_admitted {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : Active P k) : P h.val := h.property.1
theorem restriction_value {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : Active P k) :
    restrictedEval P k h=k.eval ⟨h.val,h.property.2⟩ := rfl
inductive Outcome (W : Type v) where
  | illegal | undefined | value (w : W)
noncomputable def observe {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) : Outcome W := by
  classical
  exact if P h then
    if hd : k.defined h then .value (k.eval ⟨h,hd⟩) else .undefined
    else .illegal
theorem observe_illegal {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) (hp : ¬P h) :
    observe P k h=.illegal := by simp [observe,hp]
theorem observe_undefined {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) (hp : P h) (he : ¬k.defined h) :
    observe P k h=.undefined := by simp [observe,hp,he]
theorem observe_value {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) (hp : P h) (he : k.defined h) :
    observe P k h=.value (k.eval ⟨h,he⟩) := by simp [observe,hp,he]
theorem value_ne_undefined {W : Type v} (w : W) :
    Outcome.value w ≠ Outcome.undefined := by intro h; cases h
theorem value_ne_illegal {W : Type v} (w : W) :
    Outcome.value w ≠ Outcome.illegal := by intro h; cases h
theorem illegal_ne_undefined {W : Type v} :
    (Outcome.illegal : Outcome W) ≠ Outcome.undefined := by intro h; cases h
theorem observe_has_value {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) :
    (∃ w, observe P k h=.value w) ↔ P h ∧ k.defined h := by
  classical
  constructor
  · rintro ⟨w,hw⟩
    by_cases hp : P h
    · by_cases he : k.defined h
      · exact ⟨hp,he⟩
      · rw [observe_undefined P k h hp he] at hw
        cases hw
    · rw [observe_illegal P k h hp] at hw
      cases hw
  · rintro ⟨hp,he⟩
    exact ⟨k.eval ⟨h,he⟩,observe_value P k h hp he⟩
def pullback {A : Type u} {W : Type v} (r : PreorderSpec W) (f : A → W) :
    PreorderSpec A where
  le a b := r.le (f a) (f b)
  refl a := r.refl (f a)
  trans := r.trans
def activeOrder {H : Type u} {W : Type v} (P : H → Prop) (k : Context H W) :
    PreorderSpec (Active P k) := pullback k.order (restrictedEval P k)
theorem active_refl {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (a : Active P k) :
    (activeOrder P k).le a a := (activeOrder P k).refl a
theorem active_trans {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) {a b c : Active P k}
    (hab : (activeOrder P k).le a b) (hbc : (activeOrder P k).le b c) :
    (activeOrder P k).le a c := (activeOrder P k).trans hab hbc
end PartialContextV15
