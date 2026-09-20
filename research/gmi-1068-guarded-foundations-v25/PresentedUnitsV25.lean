import PresentedCoreV25
namespace PresentedUnitsV25
open PresentedCoreV25 PartialUnitsV19
universe u
attribute [local instance] Classical.propDecidable
theorem map_injective {P : L → Prop} {a b : Option {x // P x}}
    (h : a.map Subtype.val = b.map Subtype.val) : a = b := by
  cases a <;> cases b <;> simp_all [Subtype.ext_iff]
theorem unit_present (p : Presented L) (e : {x // p.carrier x}) :
    IsUnit (padded p) e.val ↔ IsUnit p.algebra.mul e := by
  constructor
  · rintro ⟨h,hl,hr⟩
    refine ⟨?_,?_,?_⟩
    · apply map_injective
      simpa only [padded_present] using h
    · intro x y hxy
      apply Subtype.ext
      exact hl x.val y.val (by rw [padded_present,hxy]; rfl)
    · intro x y hxy
      apply Subtype.ext
      exact hr x.val y.val (by rw [padded_present,hxy]; rfl)
  · rintro ⟨h,hl,hr⟩
    refine ⟨?_,?_,?_⟩
    · rw [padded_present,h]; rfl
    · intro x y hxy
      obtain ⟨he,hx,hy,hm⟩ := (padded_some p e.val x y).mp hxy
      exact congrArg Subtype.val (hl ⟨x,hx⟩ ⟨y,hy⟩ hm)
    · intro x y hxy
      obtain ⟨hx,he,hy,hm⟩ := (padded_some p x e.val y).mp hxy
      exact congrArg Subtype.val (hr ⟨x,hx⟩ ⟨y,hy⟩ hm)
theorem padded_unit (p : Presented L) (e : L) :
    IsUnit (padded p) e ↔ ∃ he : p.carrier e, IsUnit p.algebra.mul ⟨e,he⟩ := by
  constructor
  · intro h
    have he := (result_membership p e e e h.1).1
    exact ⟨he,(unit_present p ⟨e,he⟩).mp h⟩
  · rintro ⟨he,h⟩
    exact (unit_present p ⟨e,he⟩).mpr h
theorem lift_some {q : Option A} {b : {_a : A // True}}
    (h : q.map (fun a => (⟨a,True.intro⟩ : {_a : A // True})) = some b) :
    q = some b.val := by
  have hh := congrArg (Option.map Subtype.val) h
  simpa [Option.map_map,Function.comp_def] using hh
noncomputable def full (P : Algebra A) : Presented A where
  carrier := fun _ => True
  algebra := {
    mul := fun x y => (P.mul x.val y.val).map (fun z => ⟨z,True.intro⟩)
    assoc := by
      intro x y z
      have h := congrArg (Option.map (fun a => (⟨a,True.intro⟩ : {_a : A // True})))
        (P.assoc x.val y.val z.val)
      simpa [Option.bind_map,Option.map_bind,Function.comp_def] using h
    localUnits := by
      intro x
      obtain ⟨e,f,he,hf,hl,hr⟩ := P.localUnits x.val
      refine ⟨⟨e,True.intro⟩,⟨f,True.intro⟩,?_,?_,?_,?_⟩
      · refine ⟨?_,?_,?_⟩
        · exact congrArg (Option.map (fun a => (⟨a,True.intro⟩ : {_a : A // True}))) he.1
        · intro a b h
          apply Subtype.ext
          apply he.2.1 a.val b.val
          exact lift_some h
        · intro a b h
          apply Subtype.ext
          apply he.2.2 a.val b.val
          exact lift_some h
      · refine ⟨?_,?_,?_⟩
        · exact congrArg (Option.map (fun a => (⟨a,True.intro⟩ : {_a : A // True}))) hf.1
        · intro a b h
          apply Subtype.ext
          apply hf.2.1 a.val b.val
          exact lift_some h
        · intro a b h
          apply Subtype.ext
          apply hf.2.2 a.val b.val
          exact lift_some h
      · simp [hl]
      · simp [hr]
    coherent := by
      intro x y z a b h k
      have h' : P.mul x.val y.val = some a.val := lift_some h
      have k' : P.mul y.val z.val = some b.val := lift_some k
      obtain ⟨w,hw⟩ := P.coherent _ _ _ _ _ h' k'
      exact ⟨⟨w,True.intro⟩,by simp [hw]⟩ }
theorem full_carrier (P : Algebra A) : (full P).carrier = fun _ => True := rfl
theorem full_padded (P : Algebra A) : padded (full P) = P.mul := by
  funext x y
  simp [padded,full,Option.map_map,Function.comp_def]
end PresentedUnitsV25
