import AffineArithmeticV23
namespace AffineIntervalsV23
open ScalarV12 AffineArithmeticV23
universe u
variable {α : Type u} [Scalar α]
theorem interval_nonneg (a b lo hi t : α) (hlo : lo≤t) (hhi : t≤hi)
    (hl : 0≤affine a b lo) (hh : 0≤affine a b hi) : 0≤affine a b t := by
  rcases Scalar.le_total 0 b with hb|hb
  · exact Scalar.le_trans hl (affine_monotone a b lo t hb hlo)
  · exact Scalar.le_trans hh (affine_antitone a b t hi hb hhi)
theorem interval_positive (a b lo hi t : α) (hlo : lo≤t) (hhi : t≤hi)
    (hl : 0<affine a b lo) (hh : 0<affine a b hi) : 0<affine a b t := by
  rcases Scalar.le_total 0 b with hb|hb
  · exact lt_of_lt_of_le hl (affine_monotone a b lo t hb hlo)
  · exact lt_of_lt_of_le hh (affine_antitone a b t hi hb hhi)
theorem interval_le (a b c d lo hi t : α) (hlo : lo≤t) (hhi : t≤hi)
    (hl : affine a b lo≤affine c d lo) (hh : affine a b hi≤affine c d hi) :
    affine a b t≤affine c d t := by
  apply (diff_nonneg _ _).mp
  rw [affine_difference]
  apply interval_nonneg (c + -a) (d + -b) lo hi t hlo hhi
  · rw [← affine_difference]; exact (diff_nonneg _ _).mpr hl
  · rw [← affine_difference]; exact (diff_nonneg _ _).mpr hh
theorem interval_lt (a b c d lo hi t : α) (hlo : lo≤t) (hhi : t≤hi)
    (hl : affine a b lo<affine c d lo) (hh : affine a b hi<affine c d hi) :
    affine a b t<affine c d t := by
  apply (diff_pos _ _).mp
  rw [affine_difference]
  apply interval_positive (c + -a) (d + -b) lo hi t hlo hhi
  · rw [← affine_difference]; exact (diff_pos _ _).mpr hl
  · rw [← affine_difference]; exact (diff_pos _ _).mpr hh
theorem interval_le_iff (a b c d lo hi : α) (h : lo≤hi) :
    (∀t,lo≤t→t≤hi→affine a b t≤affine c d t) ↔
      affine a b lo≤affine c d lo ∧ affine a b hi≤affine c d hi := by
  constructor
  · intro hf; exact ⟨hf lo (Scalar.le_refl _) h,hf hi h (Scalar.le_refl _)⟩
  · rintro ⟨hl,hh⟩ t hlt hth; exact interval_le _ _ _ _ _ _ _ hlt hth hl hh
theorem interval_lt_iff (a b c d lo hi : α) (h : lo≤hi) :
    (∀t,lo≤t→t≤hi→affine a b t<affine c d t) ↔
      affine a b lo<affine c d lo ∧ affine a b hi<affine c d hi := by
  constructor
  · intro hf; exact ⟨hf lo (Scalar.le_refl _) h,hf hi h (Scalar.le_refl _)⟩
  · rintro ⟨hl,hh⟩ t hlt hth; exact interval_lt _ _ _ _ _ _ _ hlt hth hl hh
theorem lerp_le (s a b c d : α) (hs0 : 0≤s) (hs1 : s≤1)
    (h : a≤c) (g : b≤d) : lerp s a b≤lerp s c d := by
  have hw : 0≤1 + -s := (diff_nonneg 1 s).mpr hs1
  exact add_le_add (mul_le_nonneg hw h) (mul_le_nonneg hs0 g)
theorem lerp_lt (s a b c d : α) (hs0 : 0≤s) (hs1 : s≤1)
    (h : a<c) (g : b<d) : lerp s a b<lerp s c d := by
  classical
  by_cases hs : 0<s
  · have hw : 0≤1 + -s := (diff_nonneg 1 s).mpr hs1
    have hl := mul_le_nonneg hw (le_of_lt h)
    have hr := mul_lt_positive hs g
    simpa only [lerp,Scalar.add_comm] using add_lt_add hr hl
  · have hn : s≤0 := by
      apply Classical.byContradiction
      intro hh
      exact hs (lt_of_not_le hh)
    have he := Scalar.le_antisymm hn hs0
    simpa only [he,lerp_zero] using h
theorem interpolated_le (a b c d s lo hi : α) (hs0 : 0≤s) (hs1 : s≤1)
    (hl : affine a b lo≤affine c d lo) (hh : affine a b hi≤affine c d hi) :
    affine a b (lerp s lo hi)≤affine c d (lerp s lo hi) := by
  rw [affine_interpolation,affine_interpolation]
  exact lerp_le s _ _ _ _ hs0 hs1 hl hh
theorem interpolated_lt (a b c d s lo hi : α) (hs0 : 0≤s) (hs1 : s≤1)
    (hl : affine a b lo<affine c d lo) (hh : affine a b hi<affine c d hi) :
    affine a b (lerp s lo hi)<affine c d (lerp s lo hi) := by
  rw [affine_interpolation,affine_interpolation]
  exact lerp_lt s _ _ _ _ hs0 hs1 hl hh
end AffineIntervalsV23
