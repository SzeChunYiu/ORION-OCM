import Std
namespace ResourceV10

inductive Trace (O : Type u) (E : Type v) where
  | done : O → Trace O E
  | illegal : O → Trace O E
  | step : O → E → Nat → Trace O E → Trace O E
  deriving DecidableEq

def prune (b : Nat) : Trace O E → Trace O E
  | .done o => .done o
  | .illegal o => .illegal o
  | .step o e c tail =>
    if c ≤ b then .step o e c (prune (b-c) tail) else .illegal o

theorem prune_contracts (trace : Trace O E) (lo hi : Nat) (h : lo ≤ hi) :
    prune lo (prune hi trace) = prune lo trace := by
  induction trace generalizing lo hi with
  | done o => rfl
  | illegal o => rfl
  | step o e c tail ih =>
    by_cases hh : c ≤ hi
    · by_cases hl : c ≤ lo
      · have hr : lo-c ≤ hi-c := by omega
        simp only [prune, hh, hl, if_pos]
        rw [ih (lo-c) (hi-c) hr]
      · simp [prune, hh, hl]
    · have hl : ¬ c ≤ lo := by omega
      simp [prune, hh, hl]

structure Machine (S : Type u) (A : Type v) (O : Type w) (E : Type x) where
  obs : S → O
  next : S → A → Option (E × Nat × S)

def run (m : Machine S A O E) (s : S) : List A → Trace O E
  | [] => .done (m.obs s)
  | a :: w => match m.next s a with
    | none => .illegal (m.obs s)
    | some (e,c,t) => .step (m.obs s) e c (run m t w)

def runBudget (m : Machine S A O E) (s : S) (b : Nat) : List A → Trace O E
  | [] => .done (m.obs s)
  | a :: w => match m.next s a with
    | none => .illegal (m.obs s)
    | some (e,c,t) =>
      if c ≤ b then .step (m.obs s) e c (runBudget m t (b-c) w)
      else .illegal (m.obs s)

theorem actual_budget_is_pruned (m : Machine S A O E) (s : S)
    (b : Nat) (w : List A) : runBudget m s b w = prune b (run m s w) := by
  induction w generalizing s b with
  | nil => rfl
  | cons a w ih =>
    cases hd : m.next s a with
    | none => simp [runBudget, run, hd, prune]
    | some p =>
      rcases p with ⟨e,c,t⟩
      by_cases hb : c ≤ b
      · simp [runBudget, run, hd, prune, hb, ih]
      · simp [runBudget, run, hd, prune, hb]

theorem actual_response_contracts (m : Machine S A O E) (s : S)
    (lo hi : Nat) (h : lo ≤ hi) (w : List A) :
    prune lo (runBudget m s hi w) = runBudget m s lo w := by
  rw [actual_budget_is_pruned, actual_budget_is_pruned]
  exact prune_contracts _ lo hi h

theorem pointwise_equal_contracts {m : Machine S A O E} {s t : S}
    {lo hi : Nat} (h : lo ≤ hi) (w : List A)
    (he : runBudget m s hi w = runBudget m t hi w) :
    runBudget m s lo w = runBudget m t lo w := by
  rw [← actual_response_contracts m s lo hi h w,
      ← actual_response_contracts m t lo hi h w, he]

def EquivalentAt (m : Machine S A O E) (b : Nat) (s t : S) : Prop :=
  ∀ w, runBudget m s b w = runBudget m t b w

def DistinguishesAt (m : Machine S A O E) (b : Nat) (s t : S) : Prop :=
  ∃ w, runBudget m s b w ≠ runBudget m t b w

theorem budget_equivalence_nested {m : Machine S A O E} {s t : S}
    {lo hi : Nat} (h : lo ≤ hi) (he : EquivalentAt m hi s t) :
    EquivalentAt m lo s t :=
  fun w => pointwise_equal_contracts h w (he w)

theorem same_witness_persists {m : Machine S A O E} {s t : S}
    {lo hi : Nat} (h : lo ≤ hi) (w : List A)
    (hd : runBudget m s lo w ≠ runBudget m t lo w) :
    runBudget m s hi w ≠ runBudget m t hi w :=
  fun he => hd (pointwise_equal_contracts h w he)

theorem distinction_upward {m : Machine S A O E} {s t : S}
    {lo hi : Nat} (h : lo ≤ hi) (hd : DistinguishesAt m lo s t) :
    DistinguishesAt m hi s t := by
  rcases hd with ⟨w, hw⟩
  exact ⟨w, same_witness_persists h w hw⟩

theorem equivalence_trans {m : Machine S A O E} {s t u : S} {b : Nat}
    (hst : EquivalentAt m b s t) (htu : EquivalentAt m b t u) :
    EquivalentAt m b s u := fun w => (hst w).trans (htu w)

theorem first_distinction_cutoff {m : Machine S A O E} {s t : S} {d : Nat}
    (hd : DistinguishesAt m d s t)
    (hbefore : ∀ b, b < d → EquivalentAt m b s t) (b : Nat) :
    EquivalentAt m b s t ↔ b < d := by
  constructor
  · intro he
    apply Nat.lt_of_not_ge
    intro hdb
    rcases distinction_upward hdb hd with ⟨w, hw⟩
    exact hw (he w)
  · exact hbefore b

/-- None denotes infinity; some n records a first distinguishing budget. -/
def Threshold (m : Machine S A O E) (s t : S) : Option Nat → Prop
  | none => ∀ b, EquivalentAt m b s t
  | some d => DistinguishesAt m d s t ∧ ∀ b, b < d → EquivalentAt m b s t

theorem bounded_threshold_exists {m : Machine S A O E} {s t : S}
    (n : Nat) (hd : DistinguishesAt m n s t) :
    ∃ d, d ≤ n ∧ Threshold m s t (some d) := by
  induction n with
  | zero => exact ⟨0, Nat.le_refl _, hd, fun b hb => by omega⟩
  | succ n ih =>
    by_cases hn : DistinguishesAt m n s t
    · rcases ih hn with ⟨d, hdn, hdt⟩
      exact ⟨d, by omega, hdt⟩
    · refine ⟨n+1, Nat.le_refl _, hd, ?_⟩
      intro b hb
      apply budget_equivalence_nested (show b ≤ n by omega)
      intro w
      exact Classical.byContradiction (fun hw => hn ⟨w, hw⟩)

theorem threshold_exists (m : Machine S A O E) (s t : S) :
    ∃ d, Threshold m s t d := by
  by_cases h : ∃ b, DistinguishesAt m b s t
  · rcases h with ⟨b, hb⟩
    rcases bounded_threshold_exists b hb with ⟨d, _, hd⟩
    exact ⟨some d, hd⟩
  · exact ⟨none, fun b w => Classical.byContradiction (fun hw => h ⟨b,w,hw⟩)⟩

theorem threshold_unique {m : Machine S A O E} {s t : S}
    {d e : Option Nat} (hd : Threshold m s t d) (he : Threshold m s t e) : d = e := by
  cases d with
  | none =>
    cases e with
    | none => rfl
    | some e => rcases he.1 with ⟨w,hw⟩; exact False.elim (hw (hd e w))
  | some d =>
    cases e with
    | none => rcases hd.1 with ⟨w,hw⟩; exact False.elim (hw (he d w))
    | some e =>
      have hde : ¬ d < e := by
        intro h; rcases hd.1 with ⟨w,hw⟩; exact hw (he.2 d h w)
      have hed : ¬ e < d := by
        intro h; rcases he.1 with ⟨w,hw⟩; exact hw (hd.2 e h w)
      have h : d = e := by omega
      rw [h]

theorem diagonal_threshold (m : Machine S A O E) (s : S) :
    Threshold m s s none := fun _ _ => rfl

theorem threshold_symmetric {m : Machine S A O E} {s t : S} {d : Option Nat}
    (hd : Threshold m s t d) : Threshold m t s d := by
  cases d with
  | none => exact fun b w => (hd b w).symm
  | some d =>
    rcases hd with ⟨⟨w,hw⟩, hb⟩
    exact ⟨⟨w, fun h => hw h.symm⟩, fun b h w => (hb b h w).symm⟩

def Below (b : Nat) : Option Nat → Prop
  | none => True
  | some d => b < d

theorem threshold_cutoff {m : Machine S A O E} {s t : S}
    {d : Option Nat} (hd : Threshold m s t d) (b : Nat) :
    EquivalentAt m b s t ↔ Below b d := by
  cases d with
  | none => exact ⟨fun _ => trivial, fun _ => hd b⟩
  | some d => exact first_distinction_cutoff hd.1 hd.2 b

/-- Extended anti-triangle stated by all strict finite lower cuts, including infinity. -/
theorem threshold_anti_triangle {m : Machine S A O E} {s t u : S}
    {dst dtu dsu : Option Nat}
    (hst : Threshold m s t dst) (htu : Threshold m t u dtu)
    (hsu : Threshold m s u dsu) (b : Nat)
    (hbst : Below b dst) (hbtu : Below b dtu) : Below b dsu := by
  apply (threshold_cutoff hsu b).mp
  exact equivalence_trans ((threshold_cutoff hst b).mpr hbst)
    ((threshold_cutoff htu b).mpr hbtu)

end ResourceV10
