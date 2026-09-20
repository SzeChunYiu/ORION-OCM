import FiniteSumsV12
import LowerFiniteV18
import PartialContextV15
namespace ExpectationContextsV18
open ScalarV12 PartialContextV15 LowerFiniteV18
universe u v
variable {α : Type v} [Scalar α]
structure Probability (α : Type v) [Scalar α] (n : Nat) where
  weight : Fin n → α
  nonnegative : ∀ i, 0≤weight i
  normalized : sum weight=1
def scalarOrder : PreorderSpec α where
  le := (· ≤ ·)
  refl := Scalar.le_refl
  trans := Scalar.le_trans
def expected {n : Nat} (w : Probability α n) (v : Fin n → α) := dot w.weight v
theorem expected_monotone {n : Nat} (w : Probability α n) (f g : Fin n → α)
    (h : ∀ i, f i≤g i) : expected w f≤expected w g :=
  dot_monotone w.nonnegative h
theorem expected_constant {n : Nat} (w : Probability α n) (c : α) :
    expected w (fun _ => c)=c := by
  unfold expected dot
  calc
    sum (fun i => w.weight i*c)=sum (fun i => c*w.weight i) := by
      congr 1; funext i; exact Scalar.mul_comm _ _
    _ = c*sum w.weight := sum_mul c w.weight
    _ = c := by rw [w.normalized,mul_one]
theorem no_empty_probability : ¬ Nonempty (Probability α 0) := by
  rintro ⟨w⟩
  have h : (0 : α)=1 := w.normalized
  exact ((Scalar.lt_iff (0 : α) 1).mp Scalar.zero_lt_one).2 h
def expectation {H : Type u} {n : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n) : Context H α where
  defined := E
  eval h := expected w (f h)
  order := scalarOrder
theorem expectation_defined {H : Type u} {n : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n) :
    (expectation E f w).defined=E := rfl
theorem expectation_value {H : Type u} {n : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n) (h : {h // E h}) :
    (expectation E f w).eval h=sum (fun i => w.weight i*f h i) := rfl
theorem expectation_active {H : Type u} {n : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n) (h : H) :
    (relativeDomain P (expectation E f w)).defined h ↔ P h ∧ E h := Iff.rfl
theorem expectation_comparison {H : Type u} {n : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n)
    (a b : Active P (expectation E f w)) :
    (activeOrder P (expectation E f w)).le a b ↔
    expected w (f ⟨a.val,a.property.2⟩)≤expected w (f ⟨b.val,b.property.2⟩) := Iff.rfl
theorem expectation_observe {H : Type u} {n : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (w : Probability α n) (h : H) :
    observe P (expectation E f w) h =
    (by classical exact if P h then if he : E h then
      Outcome.value (expected w (f ⟨h,he⟩)) else .undefined else .illegal) := by
  classical
  rfl

noncomputable def envelope {n m : Nat} (ws : Fin (m+1) → Probability α n)
    (v : Fin n → α) : α := lower (fun j => expected (ws j) v)
theorem envelope_monotone {n m : Nat} (ws : Fin (m+1) → Probability α n)
    (f g : Fin n → α) (h : ∀ i, f i≤g i) : envelope ws f≤envelope ws g :=
  lower_monotone _ _ (fun j => expected_monotone (ws j) f g h)
theorem envelope_constant {n m : Nat} (ws : Fin (m+1) → Probability α n) (c : α) :
    envelope ws (fun _ => c)=c := by
  unfold envelope
  simp only [expected_constant,lower_constant]
theorem envelope_singleton {n : Nat} (ws : Fin 1 → Probability α n) (v : Fin n → α) :
    envelope ws v=expected (ws 0) v := rfl
theorem envelope_attained {n m : Nat} (ws : Fin (m+1) → Probability α n) (v : Fin n → α) :
    ∃ j, envelope ws v=expected (ws j) v := lower_attained _
noncomputable def lowerContext {H : Type u} {n m : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n) : Context H α where
  defined := E
  eval h := envelope ws (f h)
  order := scalarOrder
theorem lower_defined {H : Type u} {n m : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n) :
    (lowerContext E f ws).defined=E := rfl
theorem lower_value {H : Type u} {n m : Nat} (E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n) (h : {h // E h}) :
    (lowerContext E f ws).eval h=lower (fun j => sum (fun i => (ws j).weight i*f h i)) := rfl
theorem lower_active {H : Type u} {n m : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n) (h : H) :
    (relativeDomain P (lowerContext E f ws)).defined h ↔ P h ∧ E h := Iff.rfl
theorem lower_comparison {H : Type u} {n m : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n)
    (a b : Active P (lowerContext E f ws)) :
    (activeOrder P (lowerContext E f ws)).le a b ↔
    envelope ws (f ⟨a.val,a.property.2⟩)≤envelope ws (f ⟨b.val,b.property.2⟩) := Iff.rfl
theorem lower_observe {H : Type u} {n m : Nat} (P E : H → Prop)
    (f : {h // E h} → Fin n → α) (ws : Fin (m+1) → Probability α n) (h : H) :
    observe P (lowerContext E f ws) h =
    (by classical exact if P h then if he : E h then
      Outcome.value (envelope ws (f ⟨h,he⟩)) else .undefined else .illegal) := by
  classical
  rfl

def intDirac (n : Nat) (z : Fin n) : Probability Int n where
  weight i := if i=z then 1 else 0
  nonnegative i := by split <;> decide
  normalized := by
    induction n with
    | zero => exact Fin.elim0 z
    | succ n ih =>
      induction z using Fin.cases with
      | zero => simp [sum,sum_zero,Fin.succ_ne_zero]
      | succ z =>
        have h := ih z
        have hz : (0 : Fin (n+1)) ≠ z.succ := Ne.symm (Fin.succ_ne_zero z)
        simpa [sum,hz,Fin.succ_ne_zero,Fin.succ_inj] using h
theorem int_dirac_value (n : Nat) (z : Fin n) (v : Fin n → Int) :
    expected (intDirac n z) v=v z := by
  unfold expected dot
  induction n with
  | zero => exact Fin.elim0 z
  | succ n ih =>
    induction z using Fin.cases with
    | zero => simp [intDirac,sum,sum_zero,Fin.succ_ne_zero]
    | succ z =>
      have h := ih z (fun i => v i.succ)
      have hz : (0 : Fin (n+1)) ≠ z.succ := Ne.symm (Fin.succ_ne_zero z)
      simpa [intDirac,sum,hz,Fin.succ_ne_zero,Fin.succ_inj] using h
end ExpectationContextsV18
