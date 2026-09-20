universe u

/-- Histories are finite lists of admitted process-step labels.
    Empty histories and associativity are therefore derived from List. -/
abbrev History (Step : Type u) := List Step

theorem empty_history_left {Step : Type u} (h : History Step) :
    ([] ++ h) = h := by
  rfl

theorem empty_history_right {Step : Type u} (h : History Step) :
    (h ++ []) = h := by
  exact List.append_nil h

theorem history_concat_assoc {Step : Type u}
    (h₁ h₂ h₃ : History Step) :
    (h₁ ++ h₂) ++ h₃ = h₁ ++ (h₂ ++ h₃) := by
  exact List.append_assoc h₁ h₂ h₃

structure PrimitiveStep where
  src : Nat
  dst : Nat

def boundaryComposable (a b : PrimitiveStep) : Prop :=
  a.dst = b.src

theorem ill_typed_example_rejected :
    ¬ boundaryComposable ⟨0,1⟩ ⟨0,1⟩ := by
  simp [boundaryComposable]
