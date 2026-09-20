inductive Action where
  | a0
  | a1
deriving DecidableEq

def processStep (_ : Unit) (_ : Action) : Unit := ()

def ctx0 : Action → Nat
  | .a0 => 1
  | .a1 => 0

def ctx1 : Action → Nat
  | .a0 => 0
  | .a1 => 1

theorem ctx0_prefers_a0 : ctx0 .a0 > ctx0 .a1 := by decide
theorem ctx1_prefers_a1 : ctx1 .a1 > ctx1 .a0 := by decide

theorem same_process_different_context : ctx0 ≠ ctx1 := by
  intro h
  have h0 := congrFun h Action.a0
  simp [ctx0, ctx1] at h0

def reach0 (a b : Bool) : Prop := a = b
def reach1 (a b : Bool) : Prop := a = b ∨ (a = false ∧ b = true)

def stateValue (b : Bool) : Nat := if b then 1 else 0

theorem process_models_differ_under_same_context :
    (¬ reach0 false true) ∧ reach1 false true := by
  constructor
  · simp [reach0]
  · simp [reach1]

def score21 (p : Nat × Nat) : Nat := 2 * p.1 + p.2
def score12 (p : Nat × Nat) : Nat := p.1 + 2 * p.2

theorem scalarization_can_reverse_incomparables :
    score21 (1,0) > score21 (0,1) ∧
    score12 (0,1) > score12 (1,0) := by
  decide
