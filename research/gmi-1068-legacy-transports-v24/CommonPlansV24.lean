import PlanContextsV24
namespace CommonPlansV24
universe u v w
def Common {H : Type u} {K : Type v} (U : K → Prop) (B : H → Prop)
    (F : H → K → Prop) (q : K) := U q ∧ ∀ h, B h → F h q
def Compatible {H : Type u} {K : Type v} (U : K → Prop) (B : H → Prop)
    (F : H → K → Prop) := ∃ q, Common U B F q
def Mapped {K : Type v} {Z : Type w} (f : K → Z) (S : K → Prop) (z : Z) :=
  ∃ q, S q ∧ f q=z
theorem common_binding {H : Type u} {K : Type v} (U : K → Prop) (B : H → Prop)
    (F : H → K → Prop) (q : K) :
    Common U B F q ↔ U q ∧ ∀ h, B h → F h q := Iff.rfl
theorem empty_family {H : Type u} {K : Type v} (U : K → Prop)
    (F : H → K → Prop) (q : K) : Common U (fun _ => False) F q ↔ U q := by
  simp [Common]
theorem empty_compatible {H : Type u} {K : Type v} (U : K → Prop)
    (F : H → K → Prop) : Compatible U (fun _ => False) F ↔ ∃ q, U q := by
  simp [Compatible,Common]
theorem mapped_intersection {H : Type u} {K : Type v} {Z : Type w}
    (U : K → Prop) (B : H → Prop) (F : H → K → Prop) (f : K → Z)
    (inj : ∀ a b, f a=f b → a=b) (z : Z) :
    Mapped f (Common U B F) z ↔
      Mapped f U z ∧ ∀ h, B h → Mapped f (fun q => U q ∧ F h q) z := by
  constructor
  · rintro ⟨q,⟨hu,hf⟩,hz⟩
    exact ⟨⟨q,hu,hz⟩,fun h hb => ⟨q,⟨hu,hf h hb⟩,hz⟩⟩
  · rintro ⟨⟨q,hu,hz⟩,hall⟩
    refine ⟨q,⟨hu,?_⟩,hz⟩
    intro h hb
    obtain ⟨p,⟨_,hp⟩,hpz⟩ := hall h hb
    exact (inj p q (hpz.trans hz.symm)) ▸ hp
theorem feasible_common {H : Type u} {K : Type v} {L : Type w}
    (U : K → Prop) (B : H → Prop) (P E : H → K → Prop)
    (loss : ∀ h, {q // E h q} → L) (r : PartialContextV15.PreorderSpec L)
    (eps : L) (q : K) :
    Common U B (fun h => PlanContextsV24.Feasible U (P h) (E h) (loss h) r eps) q ↔
    U q ∧ ∀ h, B h → ∃ l,
      ImageTransportV24.Image (fun q => U q ∧ P h q) (PlanContextsV24.context (E h) (loss h) r)
        (q,l) ∧ r.le l eps := by
  simp only [Common,PlanContextsV24.feasible_image]
theorem family_antitone {H : Type u} {K : Type v}
    (U : K → Prop) (B C : H → Prop) (F : H → K → Prop)
    (sub : ∀ h, B h → C h) (q : K) : Common U C F q → Common U B F q :=
  fun h => ⟨h.1,fun x hx => h.2 x (sub x hx)⟩
end CommonPlansV24
