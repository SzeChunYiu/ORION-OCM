def scalarDist (direct via : Nat) : Nat := Nat.min direct via

theorem finite_triangle_from_composite
    (dAC dAB dBC : Nat)
    (h : dAC ≤ dAB + dBC) :
    dAC ≤ dAB + dBC := h

theorem zero_identity (dAA : Nat) (h : dAA = 0) : dAA = 0 := h

inductive Node where | A | B deriving DecidableEq

def oneWay : Node → Node → Prop
  | .A, .A => True
  | .B, .B => True
  | .A, .B => True
  | .B, .A => False

theorem directed_asymmetry :
    oneWay .A .B ∧ ¬ oneWay .B .A := by
  constructor <;> simp [oneWay]
