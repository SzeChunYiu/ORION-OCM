import GuardedMapsV20
namespace SimulationV20
open PartialContextV15 GuardedMapsV20
universe u v
def run {X : Type u} {A : Type v} (d : X → A → Option X) :
    X → List A → Option X
  | x, [] => some x
  | x, a::w => (d x a).bind (fun y => run d y w)
def Simulation {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (R : X → X → Prop) :=
  ∀ x y, R x y → b.le x y ∧
    ∀ a x', d x a=some x' → ∃ y', d y a=some y' ∧ R x' y'
def WordRelation {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :=
  ∀ w x', run d x w=some x' → ∃ y', run d y w=some y' ∧ b.le x' y'
def Greatest {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :=
  ∃ R, Simulation b d R ∧ R x y
theorem simulation_run {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (R : X → X → Prop) (hs : Simulation b d R)
    (w : List A) (x y : X) (hxy : R x y) :
    ∀ x', run d x w=some x' → ∃ y', run d y w=some y' ∧ R x' y' := by
  induction w generalizing x y with
  | nil =>
    intro x' hx'
    have he : x=x' := Option.some.inj hx'
    subst x'
    exact ⟨y,rfl,hxy⟩
  | cons a w ih =>
    intro x' hx'
    cases hx : d x a with
    | none => simp [run,hx] at hx'
    | some z =>
      obtain ⟨t,ht,hzt⟩ := (hs x y hxy).2 a z hx
      obtain ⟨y',hy',hxy'⟩ := ih z t hzt x' (by simpa [run,hx] using hx')
      exact ⟨y',by simpa [run,ht] using hy',hxy'⟩
theorem simulation_words {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (R : X → X → Prop) (hs : Simulation b d R)
    (x y : X) (hxy : R x y) : WordRelation b d x y := by
  intro w x' hx'
  obtain ⟨y',hy',hr⟩ := simulation_run b d R hs w x y hxy x' hx'
  exact ⟨y',hy',(hs x' y' hr).1⟩
theorem words_simulation {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) : Simulation b d (WordRelation b d) := by
  intro x y hxy
  have base : b.le x y := by
    obtain ⟨y',hy',hxy'⟩ := hxy [] x rfl
    have he : y=y' := Option.some.inj hy'
    exact he ▸ hxy'
  refine ⟨base,?_⟩
  intro a x' hx'
  obtain ⟨y',hy',_⟩ := hxy [a] x' (by simp [run,hx'])
  have hy : d y a=some y' := by simpa [run] using hy'
  refine ⟨y',hy,?_⟩
  intro w z hz
  obtain ⟨t,ht,hzt⟩ := hxy (a::w) z (by simpa [run,hx'] using hz)
  exact ⟨t,by simpa [run,hy] using ht,hzt⟩
theorem greatest_iff_words {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :
    Greatest b d x y ↔ WordRelation b d x y := by
  constructor
  · rintro ⟨R,hs,hr⟩
    exact simulation_words b d R hs x y hr
  · intro h
    exact ⟨WordRelation b d,words_simulation b d,h⟩
theorem greatest_simulation {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) : Simulation b d (Greatest b d) := by
  intro x y hxy
  obtain ⟨hb,hs⟩ := words_simulation b d x y ((greatest_iff_words b d x y).mp hxy)
  refine ⟨hb,?_⟩
  intro a x' hx'
  obtain ⟨y',hy',hr⟩ := hs a x' hx'
  exact ⟨y',hy',(greatest_iff_words b d x' y').mpr hr⟩
theorem greatest_contains {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (R : X → X → Prop) (hs : Simulation b d R) :
    ∀ x y, R x y → Greatest b d x y := fun _ _ h => ⟨R,hs,h⟩
def simulationOrder {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) : PreorderSpec X where
  le := Greatest b d
  refl x := (greatest_iff_words b d x x).mpr
    (fun _ y hy => ⟨y,hy,b.refl y⟩)
  trans := by
    intro x y z hxy hyz
    apply (greatest_iff_words b d x z).mpr
    intro w x' hx'
    obtain ⟨y',hy',hb⟩ := (greatest_iff_words b d x y).mp hxy w x' hx'
    obtain ⟨z',hz',hc⟩ := (greatest_iff_words b d y z).mp hyz w y' hy'
    exact ⟨z',hz',b.trans hb hc⟩
theorem simulation_base {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (x y : X) :
    (simulationOrder b d).le x y → b.le x y :=
  fun h => (greatest_simulation b d x y h).1
theorem action_guarded {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (a : A) :
    Guarded (simulationOrder b d) (simulationOrder b d) (fun x => d x a) := by
  intro x y hxy x' hx'
  exact (greatest_simulation b d x y hxy).2 a x' hx'
theorem word_guarded {X : Type u} {A : Type v} (b : PreorderSpec X)
    (d : X → A → Option X) (w : List A) :
    Guarded (simulationOrder b d) (simulationOrder b d) (fun x => run d x w) := by
  intro x y hxy x' hx'
  exact simulation_run b d _ (greatest_simulation b d) w x y hxy x' hx'
end SimulationV20
