import FiniteSumsV12
namespace AffineArithmeticV23
open ScalarV12
universe u
variable {α : Type u} [Scalar α]
def affine (a b t : α) := a+b*t
theorem neg_mul (a b : α) : -a*b=-(a*b) := by
  rw [Scalar.mul_comm, mul_neg, Scalar.mul_comm b a]
theorem mul_le_nonneg {a b c : α} (ha : 0≤a) (hbc : b≤c) : a*b≤a*c := by
  apply (diff_nonneg (a*c) (a*b)).mp
  have h := Scalar.mul_nonneg ha ((diff_nonneg c b).mpr hbc)
  simpa only [Scalar.mul_add,mul_neg] using h
theorem mul_lt_positive {a b c : α} (ha : 0<a) (hbc : b<c) : a*b<a*c := by
  apply (diff_pos (a*c) (a*b)).mp
  have h := Scalar.mul_pos ha ((diff_pos c b).mpr hbc)
  simpa only [Scalar.mul_add,mul_neg] using h
theorem neg_order {a b : α} (h : a≤b) : -b≤-a := by
  apply (diff_nonneg (-a) (-b)).mp
  simpa only [neg_neg,Scalar.add_comm] using (diff_nonneg b a).mpr h
theorem mul_le_nonpos {a b c : α} (ha : a≤0) (hbc : b≤c) : a*c≤a*b := by
  have hp : 0≤-a := by
    simpa only [Scalar.zero_add] using (diff_nonneg 0 a).mpr ha
  have h := neg_order (mul_le_nonneg hp hbc)
  simpa only [neg_mul,neg_neg] using h
theorem affine_monotone (a b lo hi : α) (hb : 0≤b) (h : lo≤hi) :
    affine a b lo≤affine a b hi :=
  Scalar.add_le_left (mul_le_nonneg hb h) a
theorem affine_antitone (a b lo hi : α) (hb : b≤0) (h : lo≤hi) :
    affine a b hi≤affine a b lo :=
  Scalar.add_le_left (mul_le_nonpos hb h) a
theorem affine_difference (a b c d t : α) :
    affine a b t + -affine c d t=affine (a + -c) (b + -d) t := by
  simp only [affine,neg_sum,add_mul,neg_mul]
  ac_rfl
def lerp (s x y : α) := (1 + -s)*x+s*y
theorem lerp_zero (x y : α) : lerp 0 x y=x := by
  simp only [lerp,neg_zero,add_zero,Scalar.one_mul,zero_mul]
theorem lerp_one (x y : α) : lerp 1 x y=y := by
  simp only [lerp,add_neg,zero_mul,Scalar.one_mul,Scalar.zero_add]
theorem weights_sum (s : α) : (1 + -s)+s=1 := by
  rw [Scalar.add_assoc,Scalar.neg_add,add_zero]
theorem lerp_self (s a : α) : lerp s a a=a := by
  rw [lerp,← add_mul,weights_sum,Scalar.one_mul]
theorem affine_interpolation (a b s lo hi : α) :
    affine a b (lerp s lo hi)=lerp s (affine a b lo) (affine a b hi) := by
  simp only [affine,lerp,Scalar.mul_add]
  have h0 : (1 + -s)*a+s*a=a := lerp_self s a
  have h1 : b*((1 + -s)*lo)=(1 + -s)*(b*lo) := by
    rw [← Scalar.mul_assoc,Scalar.mul_comm b (1 + -s),Scalar.mul_assoc]
  have h2 : b*(s*hi)=s*(b*hi) := by
    rw [← Scalar.mul_assoc,Scalar.mul_comm b s,Scalar.mul_assoc]
  rw [h1,h2]
  calc
    a+((1 + -s)*(b*lo)+s*(b*hi)) =
        ((1 + -s)*a+s*a)+((1 + -s)*(b*lo)+s*(b*hi)) := by rw [h0]
    _ = ((1 + -s)*a+(1 + -s)*(b*lo))+(s*a+s*(b*hi)) := by ac_rfl
theorem lerp_bounds (s lo hi : α) (hs0 : 0≤s) (hs1 : s≤1) (h : lo≤hi) :
    lo≤lerp s lo hi ∧ lerp s lo hi≤hi := by
  have hw : 0≤1 + -s := (diff_nonneg 1 s).mpr hs1
  constructor
  · have hm := add_le_add (Scalar.le_refl ((1 + -s)*lo)) (mul_le_nonneg hs0 h)
    change lerp s lo lo≤lerp s lo hi at hm
    simpa only [lerp_self] using hm
  · have hm := add_le_add (mul_le_nonneg hw h) (Scalar.le_refl (s*hi))
    change lerp s lo hi≤lerp s hi hi at hm
    simpa only [lerp_self] using hm
end AffineArithmeticV23
