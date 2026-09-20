import Std

namespace DecisionV7

def Refines {W F C : Type} (fine : W → F) (coarse : W → C) : Prop :=
  ∀ {u v}, fine u = fine v → coarse u = coarse v

def AtMost {W S A : Type} (signal : W → S) (loss : W → A → Nat)
    (bound : W → Nat) : Prop :=
  ∃ policy : S → A, ∀ w, loss w (policy (signal w)) ≤ bound w

noncomputable def transport {W F C A : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) (policy : C → A) : F → A := by
  classical
  exact fun z =>
    if hz : ∃ w, fine w = z then policy (coarse (Classical.choose hz))
    else policy (coarse (Classical.choice inferInstance))

theorem transport_matches {W F C A : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) (policy : C → A)
    (h : Refines fine coarse) (w : W) :
    transport fine coarse policy (fine w) = policy (coarse w) := by
  classical
  unfold transport
  split
  next hz => exact congrArg policy (h (Classical.choose_spec hz))
  next hz => exact False.elim (hz ⟨w, rfl⟩)

theorem loss_profile_preserved {W F C A R : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) (policy : C → A)
    (loss : W → A → R) (h : Refines fine coarse) (w : W) :
    loss w (transport fine coarse policy (fine w)) =
      loss w (policy (coarse w)) := by
  rw [transport_matches fine coarse policy h w]

theorem attainable_threshold_inclusion {W F C A : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) (loss : W → A → Nat)
    (bound : W → Nat) (h : Refines fine coarse) :
    AtMost coarse loss bound → AtMost fine loss bound := by
  rintro ⟨policy, hp⟩
  refine ⟨transport fine coarse policy, ?_⟩
  intro w
  rw [transport_matches fine coarse policy h w]
  exact hp w

/-- Existence/minimality of values must be supplied; finite existence is
    established separately by the paper's complete finite policy space. -/
theorem attained_minimax_monotone {W F C A : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) (loss : W → A → Nat)
    (h : Refines fine coarse) (v0 v1 : Nat)
    (attained0 : AtMost coarse loss (fun _ => v0))
    (minimal1 : ∀ b, AtMost fine loss (fun _ => b) → v1 ≤ b) :
    v1 ≤ v0 :=
  minimal1 v0 (attainable_threshold_inclusion fine coarse loss (fun _ => v0) h attained0)

def mismatch {W : Type} (target : W → Bool) (w : W) (action : Bool) : Nat :=
  if action = target w then 0 else 1

theorem mismatch_zero_iff {W : Type} (target : W → Bool) (w : W) (a : Bool) :
    mismatch target w a ≤ 0 ↔ a = target w := by
  by_cases h : a = target w <;> simp [mismatch, h]

theorem mismatch_bounded {W : Type} (target : W → Bool) (w : W) (a : Bool) :
    mismatch target w a ≤ 1 := by
  by_cases h : a = target w <;> simp [mismatch, h]

noncomputable def splitTarget {W C : Type} (coarse : W → C) (pivot : W) :
    W → Bool := by
  classical
  exact fun w => decide (coarse w = coarse pivot)

/-- Any merged fine pair separated by coarse observations supplies a binary
    loss whose zero threshold coarse attains and fine cannot attain. -/
theorem separating_binary_loss {W F C : Type}
    (fine : W → F) (coarse : W → C) (u v : W)
    (same : fine u = fine v) (different : coarse u ≠ coarse v) :
    AtMost coarse (mismatch (splitTarget coarse u)) (fun _ => 0) ∧
      ¬ AtMost fine (mismatch (splitTarget coarse u)) (fun _ => 0) := by
  classical
  constructor
  · refine ⟨fun z => decide (z = coarse u), ?_⟩
    intro w
    exact (mismatch_zero_iff _ _ _).mpr (by simp [splitTarget])
  · rintro ⟨policy, hp⟩
    have hu := (mismatch_zero_iff _ _ _).mp (hp u)
    have hv := (mismatch_zero_iff _ _ _).mp (hp v)
    have bad : splitTarget coarse u u = splitTarget coarse u v := by
      rw [← hu, ← hv, same]
    simp [splitTarget, Ne.symm different] at bad

def BinaryZeroDominance {W F C : Type} (fine : W → F) (coarse : W → C) : Prop :=
  ∀ target : W → Bool,
    AtMost coarse (mismatch target) (fun _ => 0) →
      AtMost fine (mismatch target) (fun _ => 0)

theorem binary_zero_dominance_iff_refines {W F C : Type} [Nonempty W]
    (fine : W → F) (coarse : W → C) :
    BinaryZeroDominance fine coarse ↔ Refines fine coarse := by
  constructor
  · intro h u v same
    apply Classical.byContradiction
    intro different
    have separating := separating_binary_loss fine coarse u v same different
    exact separating.2 (h (splitTarget coarse u) separating.1)
  · intro h target
    exact attainable_threshold_inclusion fine coarse (mismatch target) (fun _ => 0) h

theorem paid_information_crossover (v0 v1 c : Int) :
    (v1 + c < v0 ↔ c < v0 - v1) ∧
    (v1 + c = v0 ↔ c = v0 - v1) ∧
    (v0 < v1 + c ↔ v0 - v1 < c) := by omega

end DecisionV7
