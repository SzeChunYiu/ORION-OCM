import FiniteSumsV12
namespace FiniteMarginsV18
open ScalarV12
def score {n : Nat} (w v : Fin n → Int) : Int := dot w v
def mask {n : Nat} (keep : Fin n → Bool) (w : Fin n → Int) (i : Fin n) : Int :=
  if keep i then w i else 0
def without {n : Nat} (w : Fin n → Int) (z : Fin n) (i : Fin n) : Int :=
  if i=z then 0 else w i

theorem score_constant {n : Nat} (w : Fin n → Int) (c : Int) :
    score w (fun _ => c)=c*sum w := by
  unfold score dot
  simp only [Int.mul_comm, sum_mul]
theorem score_monotone {n : Nat} (w u v : Fin n → Int)
    (hw : ∀ i, 0≤w i) (huv : ∀ i, u i≤v i) : score w u≤score w v :=
  dot_monotone hw huv
theorem score_bounds {n : Nat} (w v : Fin n → Int) (B : Int)
    (hw : ∀ i, 0≤w i) (hv : ∀ i, 0≤v i ∧ v i≤B) :
    0≤score w v ∧ score w v≤B*sum w := by
  constructor
  · exact sum_nonneg (fun i => Int.mul_nonneg (hw i) (hv i).1)
  · have h := score_monotone w v (fun _ => B) hw (fun i => (hv i).2)
    simpa only [score_constant] using h
theorem score_mask_split {n : Nat} (w v : Fin n → Int) (keep : Fin n → Bool) :
    score w v=score (mask keep w) v+score (mask (fun i => !(keep i)) w) v := by
  unfold score dot
  rw [← sum_add]
  congr 1
  funext i
  cases h : keep i <;> simp [mask,h]
theorem mask_nonnegative {n : Nat} (w : Fin n → Int) (keep : Fin n → Bool)
    (hw : ∀ i, 0≤w i) : ∀ i, 0≤mask keep w i := by
  intro i
  cases h : keep i <;> simp [mask,h,hw]
theorem omitted_bound {n : Nat} (w v : Fin n → Int) (keep : Fin n → Bool)
    (B : Int) (hw : ∀ i, 0≤w i) (hv : ∀ i, 0≤v i ∧ v i≤B) :
    0≤score w v-score (mask keep w) v ∧
    score w v-score (mask keep w) v≤B*sum (mask (fun i => !(keep i)) w) := by
  have hs := score_mask_split w v keep
  have hb := score_bounds (mask (fun i => !(keep i)) w) v B
    (mask_nonnegative w _ hw) hv
  omega
theorem score_split {n : Nat} (w v : Fin n → Int) (z : Fin n) :
    score w v=w z*v z+score (without w z) v := by
  rw [score,dot,sum_split (fun i => w i*v i) z]
  congr 1
  unfold except score dot
  congr 1
  funext i
  by_cases h : i=z <;> simp [without,h]
theorem without_nonnegative {n : Nat} (w : Fin n → Int) (z : Fin n)
    (hw : ∀ i, 0≤w i) : ∀ i, 0≤without w z i := by
  intro i
  by_cases h : i=z <;> simp [without,h,hw]
theorem target_window {n : Nat} (w v : Fin n → Int) (z : Fin n)
    (B : Int) (hw : ∀ i, 0≤w i) (hv : ∀ i, 0≤v i ∧ v i≤B) :
    w z*v z≤score w v ∧ score w v≤w z*v z+B*sum (without w z) := by
  have hs := score_split w v z
  have hb := score_bounds (without w z) v B (without_nonnegative w z hw) hv
  omega
theorem strict_separation {n : Nat} (w u v : Fin n → Int) (z : Fin n)
    (B : Int) (hw : ∀ i, 0≤w i)
    (hu : ∀ i, 0≤u i ∧ u i≤B) (hv : ∀ i, 0≤v i ∧ v i≤B)
    (hgap : B*sum (without w z)<w z*(v z-u z)) :
    score w u<score w v := by
  have hu' := (target_window w u z B hw hu).2
  have hv' := (target_window w v z B hw hv).1
  have he := Int.mul_sub (w z) (v z) (u z)
  omega
end FiniteMarginsV18
