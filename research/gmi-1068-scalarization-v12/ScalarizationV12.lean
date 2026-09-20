import FiniteSumsV12
namespace ScalarV12
universe u
variable {α : Type u} [Scalar α]

/-- The frozen division-free separator; the selected difference must be positive. -/
noncomputable def separator {n : Nat} (d : Fin n → α) (k : Fin n) (i : Fin n) : α :=
  if i=k then except (fun j => magnitude (d j)) k + 1 else d k

theorem separator_positive {n : Nat} (d : Fin n → α) (k : Fin n)
    (h : 0 < d k) : Positive (separator d k) := by
  intro i
  by_cases hi : i=k
  · simp only [separator, if_pos hi]
    have hs := except_nonneg (fun j => (magnitude_bounds (d j)).1) k
    have hh := add_lt_add (Scalar.zero_lt_one (α := α)) hs
    simpa only [Scalar.zero_add, Scalar.add_comm] using hh
  · simpa only [separator, if_neg hi] using h

theorem separator_formula {n : Nat} (d : Fin n → α) (k : Fin n) :
    dot (separator d k) d =
      d k * ((except (fun j => magnitude (d j)) k + 1) + except d k) := by
  have he : except (fun i => separator d k i*d i) k = d k*except d k := by
    rw [← except_mul]
    unfold except
    congr 1
    funext i
    by_cases h : i=k <;> simp only [h, separator, ↓reduceIte]
  unfold dot
  rw [sum_split (fun i => separator d k i*d i) k, he]
  simp only [separator, ↓reduceIte]
  rw [Scalar.mul_comm (except (fun j => magnitude (d j)) k + 1), ← Scalar.mul_add]

theorem separator_dot_positive {n : Nat} (d : Fin n → α) (k : Fin n)
    (h : 0 < d k) : 0 < dot (separator d k) d := by
  have he : ∀ i, 0 ≤ magnitude (d i)+d i := by
    intro i
    have hh := (diff_nonneg (magnitude (d i)) (-d i)).mpr (magnitude_bounds (d i)).2
    simpa only [neg_neg] using hh
  have hs := except_nonneg he k
  rw [except_add] at hs
  have hp := add_lt_add (Scalar.zero_lt_one (α := α)) hs
  rw [Scalar.zero_add] at hp
  rw [separator_formula]
  apply Scalar.mul_pos h
  have eqn : (except (fun j => magnitude (d j)) k + 1) + except d k =
      1 + (except (fun j => magnitude (d j)) k + except d k) := by ac_rfl
  rw [eqn]
  exact hp

theorem separating_weight {n : Nat} {x y : Fin n → α}
    (h : ¬ CoordLE x y) : ∃ w, Positive w ∧ dot w y < dot w x := by
  classical
  have hk : ∃ k, ¬ x k ≤ y k := by
    apply Classical.byContradiction
    intro hn
    apply h
    intro k
    exact Classical.byContradiction (fun hki => hn ⟨k,hki⟩)
  rcases hk with ⟨k,hk⟩
  let d := fun i => x i + -y i
  have hd : 0 < d k := (diff_pos (x k) (y k)).mpr (lt_of_not_le hk)
  refine ⟨separator d k, separator_positive d k hd, ?_⟩
  apply (diff_pos (dot (separator d k) x) (dot (separator d k) y)).mp
  rw [← dot_difference]
  exact separator_dot_positive d k hd

/-- T3: the entire family of strictly positive linear scores recovers the order. -/
theorem positive_family_recovers_order {n : Nat} (x y : Fin n → α) :
    CoordLE x y ↔ ∀ w, Positive w → dot w x ≤ dot w y := by
  constructor
  · intro h w hw
    exact dot_monotone (fun i => le_of_lt (hw i)) h
  · intro h
    classical
    apply Classical.byContradiction
    intro hn
    rcases separating_weight hn with ⟨w,hw,hs⟩
    exact not_le_of_lt hs (h w hw)

/-- T4: incomparable vectors have two positive weights with opposite rankings. -/
theorem incomparable_reversal {n : Nat} {x y : Fin n → α}
    (hxy : ¬ CoordLE x y) (hyx : ¬ CoordLE y x) :
    ∃ w v, Positive w ∧ Positive v ∧ dot w x < dot w y ∧ dot v y < dot v x := by
  rcases separating_weight hyx with ⟨w,hw,hs⟩
  rcases separating_weight hxy with ⟨v,hv,ht⟩
  exact ⟨w,v,hw,hv,hs,ht⟩

/-- T5: total comparability already obstructs exact order reflection, including ties. -/
theorem no_total_scalar_reflection {X : Type u} {β : Type v} [LE β]
    (total : ∀ a b : β, a ≤ b ∨ b ≤ a) (r : X → X → Prop)
    (x y : X) (hxy : ¬ r x y) (hyx : ¬ r y x) :
    ¬ ∃ f : X → β, ∀ a b, f a ≤ f b → r a b := by
  rintro ⟨f,hf⟩
  rcases total (f x) (f y) with h | h
  · exact hxy (hf x y h)
  · exact hyx (hf y x h)

theorem coordinate_no_total_reflection {n : Nat} {D : (Fin n → α) → Prop}
    {β : Type v} [LE β] (total : ∀ a b : β, a ≤ b ∨ b ≤ a)
    (x y : {v : Fin n → α // D v})
    (hxy : ¬ CoordLE x.val y.val) (hyx : ¬ CoordLE y.val x.val) :
    ¬ ∃ f : {v : Fin n → α // D v} → β,
      ∀ a b, f a ≤ f b → CoordLE a.val b.val :=
  no_total_scalar_reflection total (fun a b => CoordLE a.val b.val) x y hxy hyx

def ParetoEfficient {n : Nat} (D : (Fin n → α) → Prop) (x : Fin n → α) : Prop :=
  D x ∧ ¬ ∃ y, D y ∧ CoordLE y x ∧ ∃ k, y k < x k

def Minimizer {n : Nat} (D : (Fin n → α) → Prop) (w x : Fin n → α) : Prop :=
  D x ∧ ∀ y, D y → dot w x ≤ dot w y

/-- T6: any attained positive-weight minimizer is efficient; no convexity premise. -/
theorem positive_minimizer_efficient {n : Nat} {D : (Fin n → α) → Prop}
    {w x : Fin n → α} (hw : Positive w) (hm : Minimizer D w x) :
    ParetoEfficient D x := by
  refine ⟨hm.1, ?_⟩
  rintro ⟨y,hy,hcoord,k,hk⟩
  have hs := dot_strict (fun i => le_of_lt (hw i)) hcoord k hk (hw k)
  exact not_le_of_lt hs (hm.2 y hy)

end ScalarV12
