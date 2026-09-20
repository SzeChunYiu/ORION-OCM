import FrontierOrderV20
namespace WellFoundedFrontierV20
open PartialContextV15 FrontierOrderV20
universe u
def Ascent {X : Type u} (r : PreorderSpec X) (S : X → Prop)
    (y x : {x : X // S x}) := r.le x.val y.val ∧ ¬r.le y.val x.val
theorem maximal_extension {X : Type u} (r : PreorderSpec X) (S : X → Prop)
    (wf : WellFounded (Ascent r S)) (x : {x : X // S x}) :
    ∃ y, Maximal r S y ∧ r.le x.val y := by
  classical
  induction x using wf.induction with
  | h x ih =>
    by_cases hs : ∃ y : {x : X // S x}, Ascent r S y x
    · obtain ⟨y,hy⟩ := hs
      obtain ⟨z,hz,hyz⟩ := ih y hy
      exact ⟨z,hz,r.trans hy.1 hyz⟩
    · refine ⟨x.val,⟨x.property,?_⟩,r.refl x.val⟩
      intro y hy hxy
      exact Classical.byContradiction (fun hny =>
        hs ⟨⟨y,hy⟩,hxy,hny⟩)
theorem maximal_cofinal {X : Type u} (r : PreorderSpec X) (S : X → Prop)
    (wf : WellFounded (Ascent r S)) : Cofinal r (Maximal r S) S := by
  exact ⟨fun _ h => h.1,fun x hx => maximal_extension r S wf ⟨x,hx⟩⟩
theorem maximal_down {X : Type u} (r : PreorderSpec X) (S : X → Prop)
    (wf : WellFounded (Ascent r S)) :
    ∀ x, Down r (Maximal r S) x ↔ Down r S x :=
  cofinal_down r _ _ (maximal_cofinal r S wf)
end WellFoundedFrontierV20
