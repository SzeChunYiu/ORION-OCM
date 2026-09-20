import GuardedMapsV20
namespace PartialPostcontextV20
open PartialContextV15 GuardedMapsV20
universe u v w
noncomputable def valueMap {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) : Option W := by
  classical
  exact if P h then
    if he : k.defined h then some (k.eval ⟨h,he⟩) else none
    else none
theorem valueMap_iff {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (h : H) (w : W) :
    valueMap P k h=some w ↔ P h ∧ ∃ he : k.defined h, k.eval ⟨h,he⟩=w := by
  classical
  by_cases hp : P h
  · by_cases he : k.defined h
    · simp [valueMap,hp,he]
    · simp [valueMap,hp,he]
  · simp [valueMap,hp]
def postDomain {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (h : H) :=
  ∃ he : k.defined h, ∃ z, F (k.eval ⟨h,he⟩)=some z
noncomputable def post {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (s : PreorderSpec Z) : Context H Z where
  defined := postDomain k F
  eval h := Classical.choose (Classical.choose_spec h.property)
  order := s
theorem post_domain {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (s : PreorderSpec Z) (h : H) :
    (post k F s).defined h ↔
      ∃ he : k.defined h, ∃ z, F (k.eval ⟨h,he⟩)=some z := Iff.rfl
theorem post_eval {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (s : PreorderSpec Z)
    (h : {h : H // (post k F s).defined h}) (he : k.defined h.val) :
    F (k.eval ⟨h.val,he⟩)=some ((post k F s).eval h) :=
  Classical.choose_spec (Classical.choose_spec h.property)
theorem post_eval_eq {H : Type u} {W : Type v} {Z : Type w}
    (k : Context H W) (F : W → Option Z) (s : PreorderSpec Z)
    (h : {h : H // (post k F s).defined h}) (he : k.defined h.val)
    (z : Z) (hz : F (k.eval ⟨h.val,he⟩)=some z) :
    (post k F s).eval h=z :=
  Option.some.inj ((post_eval k F s h he).symm.trans hz)
def mapOutcome {W : Type v} {Z : Type w} (F : W → Option Z) :
    Outcome W → Outcome Z
  | .illegal => .illegal
  | .undefined => .undefined
  | .value w => match F w with | none => .undefined | some z => .value z
theorem post_observe {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (F : W → Option Z)
    (s : PreorderSpec Z) (h : H) :
    observe P (post k F s) h=mapOutcome F (observe P k h) := by
  classical
  by_cases hp : P h
  · by_cases he : k.defined h
    · rw [observe_value P k h hp he]
      cases hf : F (k.eval ⟨h,he⟩) with
      | none =>
        have hn : ¬(post k F s).defined h := by
          rintro ⟨he',z,hz⟩
          rw [hf] at hz
          cases hz
        rw [observe_undefined P (post k F s) h hp hn]
        simp [mapOutcome,hf]
      | some z =>
        have hd : (post k F s).defined h := ⟨he,z,hf⟩
        rw [observe_value P (post k F s) h hp hd]
        rw [post_eval_eq k F s ⟨h,hd⟩ he z hf]
        simp [mapOutcome,hf]
    · have hn : ¬(post k F s).defined h := fun hh => he hh.choose
      rw [observe_undefined P k h hp he,observe_undefined P (post k F s) h hp hn]
      rfl
  · rw [observe_illegal P k h hp,observe_illegal P (post k F s) h hp]
    rfl
theorem post_valueMap {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (F : W → Option Z)
    (s : PreorderSpec Z) (h : H) :
    valueMap P (post k F s) h=(valueMap P k h).bind F := by
  classical
  by_cases hp : P h
  · by_cases he : k.defined h
    · cases hf : F (k.eval ⟨h,he⟩) with
      | none =>
        have hn : ¬(post k F s).defined h := by
          rintro ⟨he',z,hz⟩
          rw [hf] at hz
          cases hz
        simp [valueMap,hp,he,hn,hf]
      | some z =>
        have hd : (post k F s).defined h := ⟨he,z,hf⟩
        simp only [valueMap,if_pos hp,dif_pos he,dif_pos hd,Option.some_bind]
        exact (congrArg some (post_eval_eq k F s ⟨h,hd⟩ he z hf)).trans hf.symm
    · have hn : ¬(post k F s).defined h := fun hh => he hh.choose
      simp [valueMap,hp,he,hn]
  · simp [valueMap,hp]
def Attained {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (T : H → Prop) (w : W) :=
  ∃ h, T h ∧ P h ∧ ∃ he : k.defined h, k.eval ⟨h,he⟩=w
theorem attained_valueMap {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (T : H → Prop) (w : W) :
    Attained P k T w ↔ Image (valueMap P k) T w := by
  simp only [Attained,Image,valueMap_iff]
theorem post_attained {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (T : H → Prop)
    (F : W → Option Z) (s : PreorderSpec Z) (z : Z) :
    Attained P (post k F s) T z ↔ Image F (Attained P k T) z := by
  constructor
  · rintro ⟨h,ht,hp,hd,hz⟩
    obtain ⟨he,y,hy⟩ := hd
    have hh := post_eval k F s ⟨h,⟨he,y,hy⟩⟩ he
    rw [hz] at hh
    exact ⟨k.eval ⟨h,he⟩,⟨h,ht,hp,he,rfl⟩,hh⟩
  · rintro ⟨y,⟨h,ht,hp,he,hy⟩,hf⟩
    have hh : F (k.eval ⟨h,he⟩)=some z := hy ▸ hf
    have hd : (post k F s).defined h := ⟨he,z,hh⟩
    exact ⟨h,ht,hp,hd,post_eval_eq k F s ⟨h,hd⟩ he z hh⟩
theorem post_active {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (F : W → Option Z)
    (s : PreorderSpec Z) (h : H) :
    (relativeDomain P (post k F s)).defined h ↔
      P h ∧ ∃ he : k.defined h, ∃ z, F (k.eval ⟨h,he⟩)=some z := Iff.rfl
end PartialPostcontextV20
