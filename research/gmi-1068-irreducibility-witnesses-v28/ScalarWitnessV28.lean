import OriginalBindingsV28
import ScalarizationV12
namespace ScalarWitnessV28
open ScalarV12
def vector (p : Nat × Nat) (i : Fin 2) : Int := if i=0 then p.1 else p.2
def left : Fin 2 → Int := vector (1,0)
def right : Fin 2 → Int := vector (0,1)
def weight21 : Fin 2 → Int := vector (2,1)
def weight12 : Fin 2 → Int := vector (1,2)
theorem incomparable : ¬ CoordLE left right ∧ ¬ CoordLE right left := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem positive_weights : Positive weight21 ∧ Positive weight12 := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem scalar_values :
    dot weight21 left = 2 ∧ dot weight21 right = 1 ∧
    dot weight12 left = 1 ∧ dot weight12 right = 2 := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem original_scores :
    dot weight21 left = (score21 (1,0) : Int) ∧
    dot weight21 right = (score21 (0,1) : Int) ∧
    dot weight12 left = (score12 (1,0) : Int) ∧
    dot weight12 right = (score12 (0,1) : Int) := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem actual_reversals :
    dot weight21 right < dot weight21 left ∧ dot weight12 left < dot weight12 right := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem original_reversals :
    score21 (1,0) > score21 (0,1) ∧ score12 (0,1) > score12 (1,0) :=
  scalarization_can_reverse_incomparables
def zeroWeight : Fin 2 → Int := fun i => if i=0 then 1 else 0
def negativeWeight : Fin 2 → Int := fun i => if i=0 then 1 else -1
def origin : Fin 2 → Int := fun _ => 0
theorem zero_strictness_loss :
    Nonnegative zeroWeight ∧ CoordLE origin right ∧ origin 1 < right 1 ∧
    dot zeroWeight origin = dot zeroWeight right := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem negative_domination_reversal :
    CoordLE origin right ∧ dot negativeWeight right < dot negativeWeight origin := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
theorem identical_profile_tie : dot weight21 left = dot weight21 left ∧
    ¬ dot weight21 left < dot weight21 left := by
  try simp only [CoordLE,Positive,Nonnegative]
  decide
end ScalarWitnessV28
