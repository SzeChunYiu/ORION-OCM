import Lean

/- Logical bridge only. Probability, matrix and runtime-refinement theorems
   remain written arguments in THEORY.md, not formalized by this file. -/
namespace MEFoundation

inductive Live where
  | dead | unknown | live
  deriving DecidableEq

def status (lower upper : Bool) : Live :=
  if lower then .live else if upper then .unknown else .dead

def meet : Live -> Live -> Live
  | .dead, _ => .dead
  | _, .dead => .dead
  | .live, .live => .live
  | _, _ => .unknown

theorem interval_conjunction (l u m v : Bool)
    (h : l = true -> u = true) (j : m = true -> v = true) :
    status (l && m) (u && v) = meet (status l u) (status m v) := by
  cases l <;> cases u <;> cases m <;> cases v <;>
    simp_all [status, meet]

theorem live_refinement (l u m v : Bool)
    (h : l = true -> m = true) (j : status l u = .live) :
    status m v = .live := by
  cases l <;> cases u <;> cases m <;> cases v <;>
    simp_all [status]

theorem separate_witnesses_not_joint :
    (Exists fun b : Bool => b = true) /\
    (Exists fun b : Bool => b = false) /\
    Not (Exists fun b : Bool => b = true /\ b = false) := by
  decide

theorem agreement_sound {H A : Type} (V : H -> Prop) (q : H -> A)
    (answer : A) (actual : H) (member : V actual)
    (agreement : forall h, V h -> q h = answer) : q actual = answer :=
  agreement actual member

theorem agreement_refinement {H A : Type} (V W : H -> Prop)
    (q : H -> A) (answer : A)
    (subset : forall h, W h -> V h)
    (agreement : forall h, V h -> q h = answer) :
    forall h, W h -> q h = answer := by
  intro h member
  exact agreement h (subset h member)

def capMeet (a b : Nat) : Nat := if a <= b then a else b

theorem authority_nonamplification (a b : Nat) :
    capMeet a b <= a /\ capMeet a b <= b := by
  by_cases h : a <= b
  · simp [capMeet, h]
  · simp [capMeet, h]
    omega

theorem integer_work_bound (xs : List Nat) :
    (forall x, x ∈ xs -> 1 <= x) -> xs.length <= xs.sum := by
  induction xs with
  | nil => intro _; simp
  | cons x xs ih =>
    intro positive
    have hx : 1 <= x := positive x (by simp)
    have ht : forall y, y ∈ xs -> 1 <= y := by
      intro y hy
      exact positive y (by simp [hy])
    have bound := ih ht
    simp only [List.length_cons, List.sum_cons]
    omega

inductive Kind where
  | exactTarget | riskBound
  deriving DecidableEq

def canAssertExact : Kind -> Bool
  | .exactTarget => true
  | .riskBound => false

theorem risk_not_exact : canAssertExact .riskBound = false := rfl

end MEFoundation

#print axioms MEFoundation.interval_conjunction
#print axioms MEFoundation.live_refinement
#print axioms MEFoundation.separate_witnesses_not_joint
#print axioms MEFoundation.agreement_sound
#print axioms MEFoundation.agreement_refinement
#print axioms MEFoundation.authority_nonamplification
#print axioms MEFoundation.integer_work_bound
#print axioms MEFoundation.risk_not_exact
