import ScalarWitnessV28
namespace ScalarBindingsV28
theorem vector (p : Nat × Nat) (i : Fin 2) :
    ScalarWitnessV28.vector p i = if i=0 then (p.1 : Int) else p.2 := rfl
theorem left : ScalarWitnessV28.left = ScalarWitnessV28.vector (1,0) := rfl
theorem right : ScalarWitnessV28.right = ScalarWitnessV28.vector (0,1) := rfl
theorem weight21 : ScalarWitnessV28.weight21 = ScalarWitnessV28.vector (2,1) := rfl
theorem weight12 : ScalarWitnessV28.weight12 = ScalarWitnessV28.vector (1,2) := rfl
theorem zero_weight (i : Fin 2) : ScalarWitnessV28.zeroWeight i = if i=0 then 1 else 0 := rfl
theorem negative_weight (i : Fin 2) : ScalarWitnessV28.negativeWeight i = if i=0 then 1 else -1 := rfl
theorem origin (i : Fin 2) : ScalarWitnessV28.origin i = 0 := rfl
theorem dot_int (w x : Fin 2 → Int) : ScalarV12.dot w x =
    w 0 * x 0 + (w 1 * x 1 + 0) := rfl
theorem coord_int (x y : Fin 2 → Int) :
    ScalarV12.CoordLE x y ↔ ∀ i, x i ≤ y i := Iff.rfl
theorem positive_int (w : Fin 2 → Int) :
    ScalarV12.Positive w ↔ ∀ i, 0 < w i := Iff.rfl
end ScalarBindingsV28
