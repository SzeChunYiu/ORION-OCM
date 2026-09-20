import ConstructorBindingsV24
namespace ProofTargetsV24
open PartialContextV15 ImageTransportV24 ScalarV12
universe u v w
theorem selected_projection_contract {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) :
    (∀ z, Projected P k B f z ↔ Projected P k (fun _ => True) f z) ↔
    (∀ h, P h → ∀ he : k.defined h,
      ∃ b, B b ∧ P b ∧ ∃ hb : k.defined b,
        f (k.eval ⟨b,hb⟩)=f (k.eval ⟨h,he⟩)) := selected_iff P k B f
theorem preference_contract {I : Type u} {α : Type v} [Scalar α] {n : Nat}
    (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α) (positive : Positive w) (i : I) :
    ((∃ v, FrontierOrderV20.Maximal CandidateContextsV24.vectorOrder
      (Image P (CandidateContextsV24.context r)) (i,v)) ↔ CandidateContextsV24.Pareto P r i) ∧
    (PriceContextsV24.Argmin P r w i → CandidateContextsV24.Pareto P r i) :=
  ⟨CandidateContextsV24.maximal_ids P r i,PriceContextsV24.positive_price_pareto P r w positive i⟩
theorem plan_intersection_contract {H : Type u} {K : Type v} {Z : Type w}
    (U : K → Prop) (B : H → Prop) (F : H → K → Prop) (f : K → Z)
    (inj : ∀ a b, f a=f b → a=b) (z : Z) :
    CommonPlansV24.Mapped f (CommonPlansV24.Common U B F) z ↔
      CommonPlansV24.Mapped f U z ∧ ∀ h, B h →
        CommonPlansV24.Mapped f (fun q => U q ∧ F h q) z :=
  CommonPlansV24.mapped_intersection U B F f inj z
end ProofTargetsV24
