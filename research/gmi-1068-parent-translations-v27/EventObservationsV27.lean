import EventTestsV27
import RationalModelV14
namespace EventObservationsV27
open StochasticV14 OrderedWeightsV27 SubEventsV27
universe u
variable {α : Type u} [Weight α] [OrderedWeight α]
def prepare {n : Nat} (i : Fin n) : Event α 1 n :=
  Event.fromKernel (Kernel.embed (fun _ => i))
def effect {m : Nat} (j : Fin m) : Event α m 1 where
  value x _ := if x=j then 1 else 0
  bounded x := by
    change (if x=j then (1:α) else 0)+0≤1
    rw [add_zero]
    split
    · exact OrderedWeight.refl _
    · exact OrderedWeight.zero_le _
def observe {n m : Nat} (p : Event α n m) (i : Fin n) (j : Fin m) : α :=
  ((prepare i).comp p |>.comp (effect j)).value 0 0
theorem observation_entry {n m : Nat} (p : Event α n m) (i : Fin n) (j : Fin m) :
    observe p i j=p.value i j := by
  change mcomp (mcomp (dirac (fun _ : Fin 1 => i)) p.value)
    (fun x (_ : Fin 1) => if x=j then 1 else 0) 0 0=_
  rw [dirac_left]
  unfold mcomp
  have h : (fun x => p.value i x*(if x=j then (1:α) else 0))=
      (fun x => if x=j then p.value i x else 0) := by
    funext x
    split <;> simp only [Weight.mul_one,Weight.mul_zero]
  rw [h,sum_pick]
theorem separation {n m : Nat} (p q : Event α n m) :
    (∀ i j,observe p i j=observe q i j) ↔ p=q := by
  constructor
  · intro h; apply Event.ext
    funext i j
    simpa only [observation_entry] using h i j
  · intro h; subst q; intro i j; rfl
def scalar (a : α) (ha : a≤1) : Event α 1 1 :=
  ⟨fun _ _ => a,fun _ => by change a+0≤1; simpa only [add_zero] using ha⟩
theorem scalar_comp (a b : α) (ha : a≤1) (hb : b≤1) :
    ((scalar a ha).comp (scalar b hb)).value 0 0=a*b := by
  change a*b+0=a*b
  exact add_zero _
open RationalModel in
theorem fractional_scalar_control :
    frac 1 2 * frac 1 2=frac 1 4 ∧ frac 1 4≠(1:Q) := by decide
open RationalModel in
def testWeights (biased : Bool) (outcome : Bool) : Q :=
  if biased then (if outcome then frac 2 3 else frac 1 3) else frac 1 2
open RationalModel in
theorem equal_aggregate_different_tests :
    testWeights false false+testWeights false true=1 ∧
    testWeights true false+testWeights true true=1 ∧
    testWeights false false≠testWeights true false := by decide
end EventObservationsV27
