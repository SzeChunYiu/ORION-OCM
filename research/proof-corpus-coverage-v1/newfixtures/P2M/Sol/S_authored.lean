import Lean
namespace P2MW.S_authored
theorem solution : ∀ (P : Prop), P → P := fun _ h => h
end P2MW.S_authored
macro "p2m_exact_reverting " t:term : tactic => `(tactic| exact $t)
