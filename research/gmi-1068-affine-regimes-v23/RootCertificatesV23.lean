import AffineIntervalsV23
namespace RootCertificatesV23
open ScalarV12 AffineArithmeticV23
universe u
variable {α : Type u} [Scalar α]
theorem affine_delta (a b t c : α) :
    affine a b t + -affine a b c=b*(t + -c) := by
  simp only [affine,neg_sum,Scalar.mul_add,mul_neg]
  calc
    (a+b*t)+(-a + -(b*c))=(a + -a)+(b*t + -(b*c)) := by ac_rfl
    _ = b*t + -(b*c) := by rw [add_neg,Scalar.zero_add]
theorem root_factor (a b c t : α) (h : affine a b c=0) :
    affine a b t=b*(t + -c) := by
  have hh := affine_delta a b t c
  simpa only [h,neg_zero,add_zero] using hh
theorem pair_root_factor (a b d e c t : α) (h : affine a b c=affine d e c) :
    affine d e t + -affine a b t=(e + -b)*(t + -c) := by
  rw [affine_difference]
  apply root_factor (d + -a) (e + -b) c t
  rw [← affine_difference,h,add_neg]
theorem affine_strict (a b lo hi : α) (hb : 0<b) (h : lo<hi) :
    affine a b lo<affine a b hi :=
  add_lt_left (mul_lt_positive hb h) a
theorem crossing_right (a b d e c t : α) (h : affine a b c=affine d e c)
    (hs : b<e) (ht : c<t) : affine a b t<affine d e t := by
  apply (diff_pos _ _).mp
  rw [pair_root_factor a b d e c t h]
  exact Scalar.mul_pos ((diff_pos e b).mpr hs) ((diff_pos t c).mpr ht)
theorem crossing_left (a b d e c t : α) (h : affine a b c=affine d e c)
    (hs : b<e) (ht : t<c) : affine d e t<affine a b t := by
  have hz : affine (d + -a) (e + -b) c=0 := by
    rw [← affine_difference,h,add_neg]
  have hn := affine_strict (d + -a) (e + -b) t c ((diff_pos e b).mpr hs) ht
  rw [hz] at hn
  apply lt_of_not_le
  intro hg
  have hp := (diff_nonneg (affine d e t) (affine a b t)).mpr hg
  rw [affine_difference] at hp
  exact not_le_of_lt hn hp
theorem parallel_root (a b d c : α) (h : affine a b c=affine d b c) :
    a=d ∧ ∀t,affine a b t=affine d b t := by
  have he : a=d := add_right_cancel h
  exact ⟨he,fun _ => he ▸ rfl⟩
theorem root_unique (a b d e c r : α) (hc : affine a b c=affine d e c)
    (hr : affine a b r=affine d e r) (hs : b<e) : c=r := by
  classical
  apply Scalar.le_antisymm
  · apply Classical.byContradiction
    intro h
    have hlt := crossing_left a b d e c r hc hs (lt_of_not_le h)
    exact ((Scalar.lt_iff _ _).mp hlt).2 hr.symm
  · apply Classical.byContradiction
    intro h
    have hlt := crossing_right a b d e c r hc hs (lt_of_not_le h)
    exact ((Scalar.lt_iff _ _).mp hlt).2 hr
end RootCertificatesV23
