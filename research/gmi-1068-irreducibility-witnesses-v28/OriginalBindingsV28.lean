import ContextIrreducibility
namespace OriginalBindingsV28
theorem action_cases (a : Action) : a = .a0 ∨ a = .a1 := by cases a <;> simp
theorem actions_distinct : Action.a0 ≠ Action.a1 := by intro h; cases h
theorem process_step (s : Unit) (a : Action) : processStep s a = () := rfl
theorem ctx_zero : ctx0 .a0 = 1 ∧ ctx0 .a1 = 0 := ⟨rfl,rfl⟩
theorem ctx_one : ctx1 .a0 = 0 ∧ ctx1 .a1 = 1 := ⟨rfl,rfl⟩
theorem reach_zero (a b : Bool) : reach0 a b ↔ a = b := Iff.rfl
theorem reach_one (a b : Bool) : reach1 a b ↔ a = b ∨ (a = false ∧ b = true) := Iff.rfl
theorem state_value (b : Bool) : stateValue b = if b then 1 else 0 := rfl
theorem score_left (p : Nat × Nat) : score21 p = 2*p.1+p.2 := rfl
theorem score_right (p : Nat × Nat) : score12 p = p.1+2*p.2 := rfl
end OriginalBindingsV28
