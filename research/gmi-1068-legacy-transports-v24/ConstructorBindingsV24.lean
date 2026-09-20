import RichAFContextsV24
import TransportControlsV24
namespace ConstructorBindingsV24
open PartialContextV15 ImageTransportV24 ScalarV12
universe u v w
theorem image_binding {H : Type u} {W : Type v}
    (P : H → Prop) (k : Context H W) (w : W) :
    Image P k w ↔ ∃ h, True ∧ P h ∧ ∃ he : k.defined h, k.eval ⟨h,he⟩=w := Iff.rfl
theorem projection_binding {H : Type u} {W : Type v} {Z : Type w}
    (P : H → Prop) (k : Context H W) (B : H → Prop) (f : W → Z) (z : Z) :
    Projected P k B f z ↔
      ∃ h, B h ∧ P h ∧ ∃ he : k.defined h, f (k.eval ⟨h,he⟩)=z := Iff.rfl
theorem active_binding {I : Type u} (v r : I → Prop) (mode : Bool) (i : I) :
    CandidateContextsV24.active v r mode i ↔ v i ∧ (r i ∨ mode=false) := by
  cases mode <;> simp [CandidateContextsV24.active]
theorem pareto_binding {I : Type u} {α : Type v} [Scalar α] {n : Nat}
    (P : I → Prop) (r : I → Fin n → α) (i : I) :
    CandidateContextsV24.Pareto P r i ↔
    P i ∧ ∀ j, P j → (∀ k, r j k≤r i k) → ∀ k, r i k≤r j k := Iff.rfl
theorem argmin_binding {I : Type u} {α : Type v} [Scalar α] {n : Nat}
    (P : I → Prop) (r : I → Fin n → α) (w : Fin n → α) (i : I) :
    PriceContextsV24.Argmin P r w i ↔
    P i ∧ ∀ j, P j → dot w (r i)≤dot w (r j) := Iff.rfl
theorem code_binding {H : Type u} {W : Type v} (E : H → Prop)
    (s : PreorderSpec W) (f : H → W) :
    (ProfileContextsV24.codeContext E s f).defined=E ∧
    (ProfileContextsV24.codeContext E s f).order=pullback s f := ⟨rfl,rfl⟩
theorem feasible_binding {K : Type u} {L : Type v} (U P E : K → Prop)
    (loss : {q // E q} → L) (r : PreorderSpec L) (eps : L) (q : K) :
    PlanContextsV24.Feasible U P E loss r eps q ↔
    U q ∧ P q ∧ ∃ he : E q, r.le (loss ⟨q,he⟩) eps := Iff.rfl
theorem identity_plan_binding {K : Type u} :
    (PlanContextsV24.identityContext (K:=K)).defined=(fun _ => True) ∧
    (PlanContextsV24.identityContext (K:=K)).eval=(fun q => q.val) ∧
    (PlanContextsV24.identityContext (K:=K)).order.le=Eq := ⟨rfl,rfl,rfl⟩
theorem mapped_binding {K : Type v} {Z : Type w} (f : K → Z) (S : K → Prop) (z : Z) :
    CommonPlansV24.Mapped f S z ↔ ∃ q, S q ∧ f q=z := Iff.rfl
theorem compatible_binding {H : Type u} {K : Type v}
    (U : K → Prop) (B : H → Prop) (F : H → K → Prop) :
    CommonPlansV24.Compatible U B F ↔ ∃ q, U q ∧ ∀ h, B h → F h q := Iff.rfl
theorem int_operations (a b : Int) :
    @HAdd.hAdd Int Int Int inferInstance a b=Int.add a b ∧
    @HMul.hMul Int Int Int inferInstance a b=Int.mul a b ∧
    (@LE.le Int inferInstance a b ↔ Int.le a b) := ⟨rfl,rfl,Iff.rfl⟩
end ConstructorBindingsV24
