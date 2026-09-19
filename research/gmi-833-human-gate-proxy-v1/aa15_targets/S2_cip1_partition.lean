/-
  S2 — CIP-1, the exact capability-interaction partition.

  Target for: CAPABILITY_INTERACTION_PARTITION_THEOREMS_V1.md §1
  ("Theorem CI P-1 (exact partition)", axioms (N) and (M), Lemma 1.0,
   the degenerate case m = s, and Corollary CIP-1a).

  Lean 4 core only.  No `import` line: this file is self-contained.
  Proofs of the four target theorems are left as `sorry`; the small order
  instance below is proved outright so the targets are not vacuous.

  ---------------------------------------------------------------------------
  Modelling note.  The artifact states CIP-1 for `B(X), B(Y) ∈ R_{>=0}` and a
  general burden functional `J`.  Lean 4 core has no reals, and the proof uses no
  property of the reals: it uses only (i) trichotomy of `J` versus `s`, (ii) (M)
  `m ≤ J`, and (iii) `m ≤ s` (which is Lemma 1.0, the ONLY place where additivity
  and (N) are used).  Section 1 below therefore states CIP-1 over an arbitrary
  strict linear order with `m ≤ J` and `m ≤ s` as hypotheses — strictly more
  general than the real-valued statement.  Section 2 instantiates it at `Int`
  with `m` and `s` the actual max and sum, which is also the exact setting of the
  registered A4 accounting, where `B(X) = |R(X)|` is an integer cardinality.
  ---------------------------------------------------------------------------
-/

namespace S2

/-- a strict linear order, spelled out so the file needs no order library. -/
structure StrictLinOrder (α : Type) where
  lt : α → α → Prop
  trichotomous : ∀ a b, lt a b ∨ a = b ∨ lt b a
  irrefl : ∀ a, ¬ lt a a
  trans : ∀ a b c, lt a b → lt b c → lt a c

def StrictLinOrder.le {α : Type} (O : StrictLinOrder α) (a b : α) : Prop :=
  O.lt a b ∨ a = b

/-- exactly one of four propositions holds. -/
def ExactlyOne (P₀ P₁ P₂ P₃ : Prop) : Prop :=
  (P₀ ∨ P₁ ∨ P₂ ∨ P₃) ∧
  ¬(P₀ ∧ P₁) ∧ ¬(P₀ ∧ P₂) ∧ ¬(P₀ ∧ P₃) ∧ ¬(P₁ ∧ P₂) ∧ ¬(P₁ ∧ P₃) ∧ ¬(P₂ ∧ P₃)

section Abstract

/-- `INDEPENDENT`: `J = s`. -/
def Independent {α : Type} (J s : α) : Prop := J = s
/-- `REDUNDANT`: `J = m` and `m < s` (the guard is load-bearing at `m = s`). -/
def Redundant {α : Type} (O : StrictLinOrder α) (J m s : α) : Prop := J = m ∧ O.lt m s
/-- `PARTIAL_SHARING`: `m < J < s`. -/
def PartialSharing {α : Type} (O : StrictLinOrder α) (J m s : α) : Prop := O.lt m J ∧ O.lt J s
/-- `INTERFERING`: `J > s`. -/
def Interfering {α : Type} (O : StrictLinOrder α) (J s : α) : Prop := O.lt s J
/-- the shipped `Synergistic` condition, kept as the named aggregate `SAVING`. -/
def Saving {α : Type} (O : StrictLinOrder α) (J s : α) : Prop := O.lt J s

/-- **S2 / CIP-1 (exact partition).**  On the admissible region — (M) `m ≤ J`, and
    `m ≤ s`, which Lemma 1.0 derives from (N) — exactly one of the four classes holds. -/
theorem cip1_exact_partition {α : Type} (O : StrictLinOrder α) (J m s : α)
    (hM : O.le m J) (hms : O.le m s) :
    ExactlyOne (Independent J s) (Redundant O J m s) (PartialSharing O J m s)
               (Interfering O J s) := by
  sorry

/-- **Corollary CIP-1a.**  `SAVING = REDUNDANT ⊔ PARTIAL_SHARING`, disjointly. -/
theorem cip1a_saving_splits {α : Type} (O : StrictLinOrder α) (J m s : α) (hM : O.le m J) :
    (Saving O J s ↔ (Redundant O J m s ∨ PartialSharing O J m s)) ∧
    ¬(Redundant O J m s ∧ PartialSharing O J m s) := by
  sorry

/-- **Degenerate case `m = s`.**  The `m < s` guard never orphans a triple:
    when `m = s`, (M) forces `J ≥ s`, so only `INDEPENDENT` and `INTERFERING` remain. -/
theorem cip1_degenerate {α : Type} (O : StrictLinOrder α) (J m s : α)
    (hM : O.le m J) (hdeg : m = s) :
    (Independent J s ∨ Interfering O J s) ∧ ¬ Redundant O J m s ∧ ¬ PartialSharing O J m s := by
  sorry

end Abstract

/- ------------------------------------------------------------------ -/
/- Concrete instantiation: integer burdens (the registered A4 accounting). -/
/- ------------------------------------------------------------------ -/

/-- the strict order on `Int`, proved (not assumed). -/
def intOrder : StrictLinOrder Int where
  lt := fun a b => a < b
  trichotomous := by intro a b; omega
  irrefl := by intro a; omega
  trans := by intro a b c h₁ h₂; omega

/-- `m = max(B(X), B(Y))`, spelled out to avoid any order-library dependency. -/
def mx (a b : Int) : Int := if a < b then b else a

/-- **Lemma 1.0.**  Under (N), `m ≤ s`, because `s - m = min(B(X), B(Y)) ≥ 0`. -/
theorem lemma_1_0 (bX bY : Int) (hx : 0 ≤ bX) (hy : 0 ≤ bY) :
    mx bX bY ≤ bX + bY := by
  sorry

/-- **S2 / CIP-1 at integer burdens.**  For every pair satisfying (N) and (M),
    exactly one of `J = s`, `J = m ∧ m < s`, `m < J < s`, `J > s` holds. -/
theorem cip1_int (bX bY Jv : Int)
    (hN₁ : 0 ≤ bX) (hN₂ : 0 ≤ bY) (hM : mx bX bY ≤ Jv) :
    ExactlyOne
      (Jv = bX + bY)
      (Jv = mx bX bY ∧ mx bX bY < bX + bY)
      (mx bX bY < Jv ∧ Jv < bX + bY)
      (bX + bY < Jv) := by
  sorry

/-- the canonical DEF-1 witness of the artifact: `cap-perception {S,T}` against
    `cap-communication {S,M}` — `B(X)=2, B(Y)=2, m=2, J=3, s=4` — is `PARTIAL_SHARING`
    and is NOT `REDUNDANT`, refuting the shipped `joint = max` label for that pair. -/
theorem def1_witness :
    (mx 2 2 < (3 : Int) ∧ (3 : Int) < 2 + 2) ∧ ¬ ((3 : Int) = mx 2 2) := by
  sorry

/- argument-order guards: these are definitional identities, proved by `Iff.rfl`,
   so a later edit that permutes `(J, m, s)` in a class definition breaks the build. -/
example : Independent (3 : Int) 4 ↔ ((3 : Int) = 4) := Iff.rfl
example : Redundant intOrder (3 : Int) 3 4 ↔ ((3 : Int) = 3 ∧ (3 : Int) < 4) := Iff.rfl
example : PartialSharing intOrder (3 : Int) 2 4 ↔ ((2 : Int) < 3 ∧ (3 : Int) < 4) := Iff.rfl
example : Interfering intOrder (5 : Int) 4 ↔ ((4 : Int) < 5) := Iff.rfl
example : Saving intOrder (3 : Int) 4 ↔ ((3 : Int) < 4) := Iff.rfl

end S2
