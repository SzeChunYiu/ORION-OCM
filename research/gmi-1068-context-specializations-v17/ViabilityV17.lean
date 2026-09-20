import SpecializationsV17
namespace ViabilityV17
open PartialContextV15 SpecializationsV17
universe u v
variable {X : Type u}
def step (K : X → Prop) (R : X → X → Prop) (I : X → Prop) (x : X) : Prop :=
  K x ∧ ∃ y, R x y ∧ I y
def Postfixed (K : X → Prop) (R : X → X → Prop) (I : X → Prop) : Prop :=
  ∀ x, I x → step K R I x
def Viable (K : X → Prop) (R : X → X → Prop) (x : X) : Prop :=
  ∃ I : X → Prop, I x ∧ Postfixed K R I

theorem step_monotone (K : X → Prop) (R : X → X → Prop) {I J : X → Prop}
    (h : ∀ x, I x → J x) {x : X} (hx : step K R I x) : step K R J x := by
  rcases hx with ⟨hk,y,hr,hi⟩
  exact ⟨hk,y,hr,h y hi⟩

theorem viable_greatest (K : X → Prop) (R : X → X → Prop) (I : X → Prop)
    (h : Postfixed K R I) {x : X} (hx : I x) : Viable K R x := ⟨I,hx,h⟩

theorem viable_postfixed (K : X → Prop) (R : X → X → Prop) :
    Postfixed K R (Viable K R) := by
  rintro x ⟨I,hx,hI⟩
  rcases hI x hx with ⟨hk,y,hr,hy⟩
  exact ⟨hk,y,hr,I,hy,hI⟩

theorem viable_safe (K : X → Prop) (R : X → X → Prop) {x : X}
    (h : Viable K R x) : K x := (viable_postfixed K R x h).1

theorem viable_fixedpoint (K : X → Prop) (R : X → X → Prop) (x : X) :
    Viable K R x ↔ step K R (Viable K R) x := by
  constructor
  · exact viable_postfixed K R x
  · intro h
    exact viable_greatest K R (step K R (Viable K R))
      (fun _ hx => step_monotone K R (viable_postfixed K R) hx) h

def Trajectory (K : X → Prop) (R : X → X → Prop) (x : X) : Prop :=
  ∃ g : Nat → X, g 0 = x ∧ ∀ n, K (g n) ∧ R (g n) (g (n+1))

noncomputable def next (K : X → Prop) (R : X → X → Prop)
    (x : {x // Viable K R x}) : {x // Viable K R x} :=
  ⟨Classical.choose (viable_postfixed K R x.val x.property).2,
   (Classical.choose_spec (viable_postfixed K R x.val x.property).2).2⟩

theorem next_related (K : X → Prop) (R : X → X → Prop) (x : {x // Viable K R x}) :
    R x.val (next K R x).val :=
  (Classical.choose_spec (viable_postfixed K R x.val x.property).2).1

noncomputable def walk (K : X → Prop) (R : X → X → Prop)
    (x : {x // Viable K R x}) : Nat → {x // Viable K R x}
  | 0 => x
  | n+1 => next K R (walk K R x n)

theorem viable_to_trajectory (K : X → Prop) (R : X → X → Prop) {x : X}
    (h : Viable K R x) : Trajectory K R x := by
  refine ⟨fun n => (walk K R ⟨x,h⟩ n).val, rfl, ?_⟩
  intro n
  exact ⟨viable_safe K R (walk K R ⟨x,h⟩ n).property,
    next_related K R (walk K R ⟨x,h⟩ n)⟩

theorem trajectory_to_viable (K : X → Prop) (R : X → X → Prop) {x : X}
    (h : Trajectory K R x) : Viable K R x := by
  rcases h with ⟨g,h0,hg⟩
  refine ⟨(fun y => ∃ n, g n=y), ⟨0,h0⟩, ?_⟩
  rintro y ⟨n,rfl⟩
  exact ⟨(hg n).1,g (n+1),(hg n).2,n+1,rfl⟩

theorem viable_iff_trajectory (K : X → Prop) (R : X → X → Prop) (x : X) :
    Viable K R x ↔ Trajectory K R x :=
  ⟨viable_to_trajectory K R, trajectory_to_viable K R⟩

noncomputable def viabilityContext {H : Type v} (E : H → Prop)
    (endpoint : {h // E h} → X) (K : X → Prop) (R : X → X → Prop) : Context H Bool :=
  acceptance E (fun h => Viable K R (endpoint h))

theorem viability_defined {H : Type v} (E : H → Prop)
    (endpoint : {h // E h} → X) (K : X → Prop) (R : X → X → Prop) :
    (viabilityContext E endpoint K R).defined = E := rfl
theorem viability_value {H : Type v} (E : H → Prop)
    (endpoint : {h // E h} → X) (K : X → Prop) (R : X → X → Prop) (h : {h // E h}) :
    (viabilityContext E endpoint K R).eval h = true ↔ Viable K R (endpoint h) :=
  acceptance_true E _ h
theorem viability_comparison {H : Type v} (P E : H → Prop)
    (endpoint : {h // E h} → X) (K : X → Prop) (R : X → X → Prop)
    (a b : Active P (viabilityContext E endpoint K R)) :
    (activeOrder P (viabilityContext E endpoint K R)).le a b ↔
      (Viable K R (endpoint ⟨a.val,a.property.2⟩) →
       Viable K R (endpoint ⟨b.val,b.property.2⟩)) := acceptance_comparison P E _ a b

theorem viability_observe {H : Type v} (P E : H → Prop)
    (endpoint : {h // E h} → X) (K : X → Prop) (R : X → X → Prop) (h : H) :
    observe P (viabilityContext E endpoint K R) h =
      (by classical exact if P h then if he : E h then
        Outcome.value (if Viable K R (endpoint ⟨h,he⟩) then true else false)
        else .undefined else .illegal) := rfl
end ViabilityV17
