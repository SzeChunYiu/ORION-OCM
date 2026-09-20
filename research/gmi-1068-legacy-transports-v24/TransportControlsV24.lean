import CommonPlansV24
import FinitePreferenceV24
import AFErasureV24
namespace TransportControlsV24
open CommonPlansV24 CandidateContextsV24 PriceContextsV24 ScalarV12
def threePlans (h q : Fin 3) : Prop := q≠h
theorem pairwise_not_joint :
    (∀ a b : Fin 3, ∃ q, threePlans a q ∧ threePlans b q) ∧
    ¬Compatible (fun _ : Fin 3 => True) (fun _ : Fin 3 => True) threePlans := by
  unfold Compatible Common threePlans
  constructor
  · intro a b
    by_cases ha : a=0 <;> by_cases hb : b=0 <;> by_cases ha1 : a=1 <;> by_cases hb1 : b=1 <;>
      first | exact ⟨0,by omega,by omega⟩ | exact ⟨1,by omega,by omega⟩ | exact ⟨2,by omega,by omega⟩
  · rintro ⟨q,_,hq⟩
    exact hq q True.intro rfl
def distinctPlan (h q : Bool) : Prop := q=h
theorem loss_image_loses_plan :
    (∀ h : Bool, Mapped (fun _ : Bool => ()) (distinctPlan h) ()) ∧
    ¬Compatible (fun _ : Bool => True) (fun _ : Bool => True) distinctPlan := by
  unfold Compatible Common Mapped distinctPlan
  decide
theorem empty_codomain_caveat :
    (∀ _ : Empty, Mapped (fun _ : Unit => false) (fun _ => True) true) ∧
    ¬Mapped (fun _ : Unit => false) (fun _ => True) true := by
  constructor
  · intro h; cases h
  · rintro ⟨q,_,he⟩; cases he
def oneResource (i : Bool) : Fin 1 → Int := fun _ => if i then 1 else 0
theorem zero_price_dominated :
    Argmin (fun _ => True) oneResource (fun _ => 0) true ∧
    ¬Pareto (fun _ => True) oneResource true := by
  unfold Argmin Pareto CoordLE oneResource dot sum
  decide
theorem negative_price_reversal :
    Argmin (fun _ => True) oneResource (fun _ => -1) true ∧
    ¬Pareto (fun _ => True) oneResource true := by
  unfold Argmin Pareto CoordLE oneResource dot sum
  decide
theorem duplicate_vector_ids :
    (∀ i : Bool, Pareto (fun _ => True) (fun _ : Bool => fun _ : Fin 1 => (0 : Int)) i) ∧
    (∀ i : Bool, Argmin (fun _ => True) (fun _ : Bool => fun _ : Fin 1 => (0 : Int))
      (fun _ => 1) i) := by
  unfold Pareto Argmin CoordLE dot sum
  decide
def tradeoff (i : Bool) (k : Fin 2) : Int :=
  if i then (if k=0 then 0 else 1) else (if k=0 then 1 else 0)
theorem unattained_minimum :
    (∀ k : Fin 2, ∃ i : Bool, tradeoff i k=0) ∧
    ¬∃ i : Bool, ∀ k : Fin 2, tradeoff i k=0 := by decide
theorem terminal_not_profile :
    (fun _ : Bool => ()) false=(fun _ : Bool => ()) true ∧
    ProfileContextsV24.profile (fun _ : Bool => ()) (fun _ => ()) id (fun _ => ()) false ≠
      ProfileContextsV24.profile (fun _ : Bool => ()) (fun _ => ()) id (fun _ => ()) true := by
  refine ⟨rfl,?_⟩
  intro h
  have hf := congrArg ProfileContextsV24.Profile.history h
  cases hf
theorem threePlans_binding (h q : Fin 3) : threePlans h q ↔ q≠h := Iff.rfl
theorem distinctPlan_binding (h q : Bool) : distinctPlan h q ↔ q=h := Iff.rfl
theorem oneResource_binding (i : Bool) (k : Fin 1) :
    oneResource i k=(if i then (1 : Int) else 0) := rfl
theorem tradeoff_binding (i : Bool) (k : Fin 2) :
    tradeoff i k=(if i then (if k=0 then (0 : Int) else 1) else (if k=0 then 1 else 0)) := rfl
end TransportControlsV24
