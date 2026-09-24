universe u v

def dAA (_w₁ _w₂ : Nat) : Nat := 0
def dAB (w₁ _w₂ : Nat) : Nat := w₁
def dBC (_w₁ w₂ : Nat) : Nat := 2 * w₂
def dAC (w₁ w₂ : Nat) : Nat :=
  Nat.min (2 * w₁ + w₂) (w₁ + 2 * w₂)

theorem identity_zero_fixture (w₁ w₂ : Nat) :
    dAA w₁ w₂ = 0 := by
  rfl

theorem triangle_fixture (w₁ w₂ : Nat) :
    dAC w₁ w₂ ≤ dAB w₁ w₂ + dBC w₁ w₂ := by
  unfold dAC dAB dBC
  exact Nat.min_le_right _ _

inductive Node where
  | A
  | B
deriving DecidableEq

def oneWay : Node → Node → Prop
  | .A, .A => True
  | .B, .B => True
  | .A, .B => True
  | .B, .A => False

theorem directed_asymmetry :
    oneWay .A .B ∧ ¬ oneWay .B .A := by
  constructor <;> simp [oneWay]

def CostSet {P : Type u} {C : Type v}
    (cost : P → C) (c : C) : Prop :=
  ∃ p, cost p = c

/-- A bijection of path/process presentations that preserves cost transports
    the reachable cost set exactly. -/
theorem costSet_transport
    {P : Type u} {Q : Type u} {C : Type v}
    (costP : P → C) (costQ : Q → C)
    (toQ : P → Q) (toP : Q → P)
    (leftInv : ∀ p, toP (toQ p) = p)
    (rightInv : ∀ q, toQ (toP q) = q)
    (preserve : ∀ p, costQ (toQ p) = costP p)
    (c : C) :
    CostSet costP c ↔ CostSet costQ c := by
  constructor
  · intro hp
    rcases hp with ⟨p, hpc⟩
    refine ⟨toQ p, ?_⟩
    calc
      costQ (toQ p) = costP p := preserve p
      _ = c := hpc
  · intro hq
    rcases hq with ⟨q, hqc⟩
    refine ⟨toP q, ?_⟩
    calc
      costP (toP q) = costQ (toQ (toP q)) := Eq.symm (preserve (toP q))
      _ = costQ q := by rw [rightInv q]
      _ = c := hqc
