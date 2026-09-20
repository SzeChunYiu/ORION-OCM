import Std
namespace OptionalV13
universe u

/-- Only common units and interchange are needed; associativity is not assumed. -/
theorem operations_coincide {α : Type u} (seq tensor : α → α → α) (e : α)
    (sl : ∀ a, seq e a=a) (sr : ∀ a, seq a e=a)
    (tl : ∀ a, tensor e a=a) (tr : ∀ a, tensor a e=a)
    (inter : ∀ a b c d,
      tensor (seq a b) (seq c d) = seq (tensor a c) (tensor b d))
    (a b : α) : seq a b = tensor a b := by
  calc
    seq a b = seq (tensor a e) (tensor e b) := by rw [tr, tl]
    _ = tensor (seq a e) (seq e b) := (inter a e e b).symm
    _ = tensor a b := by rw [sr, sl]

theorem operations_commute {α : Type u} (seq tensor : α → α → α) (e : α)
    (sl : ∀ a, seq e a=a) (sr : ∀ a, seq a e=a)
    (tl : ∀ a, tensor e a=a) (tr : ∀ a, tensor a e=a)
    (inter : ∀ a b c d,
      tensor (seq a b) (seq c d) = seq (tensor a c) (tensor b d))
    (a b : α) : seq a b = seq b a := by
  calc
    seq a b = tensor a b := operations_coincide seq tensor e sl sr tl tr inter a b
    _ = tensor (seq e a) (seq b e) := by rw [sl, sr]
    _ = seq (tensor e b) (tensor a e) := inter e a b e
    _ = seq b a := by rw [tl, tr]

inductive BitProc where
  | identity | reset0 | reset1
  deriving DecidableEq, Repr

def act : BitProc → Bool → Bool
  | .identity, b => b
  | .reset0, _ => false
  | .reset1, _ => true

/-- Execute first f, then g; the later reset wins. -/
def sequence (f g : BitProc) : BitProc :=
  match g with
  | .identity => f
  | .reset0 => .reset0
  | .reset1 => .reset1

theorem sequence_actual (f g : BitProc) (b : Bool) :
    act (sequence f g) b = act g (act f b) := by cases g <;> rfl

theorem act_faithful {f g : BitProc} (h : ∀ b, act f b = act g b) : f=g := by
  have h0 := h false
  have h1 := h true
  cases f <;> cases g <;> simp_all [act]

theorem sequence_assoc (f g h : BitProc) :
    sequence (sequence f g) h = sequence f (sequence g h) := by cases h <;> rfl

theorem sequence_left (f : BitProc) : sequence .identity f=f := by cases f <;> rfl
theorem sequence_right (f : BitProc) : sequence f .identity=f := rfl

theorem invertible_iff_identity (f : BitProc) :
    (∃ g, sequence f g = .identity ∧ sequence g f = .identity) ↔ f = .identity := by
  constructor
  · rintro ⟨g,h1,h2⟩
    cases f <;> cases g <;> simp_all [sequence]
  · intro h
    rw [h]
    exact ⟨.identity,rfl,rfl⟩

theorem resets_noncommute :
    sequence .reset0 .reset1 ≠ sequence .reset1 .reset0 := by decide

/-- Necessary weak unitor/naturality data; strictness is not a field. -/
structure WeakTensorData (tensor : BitProc → BitProc → BitProc) where
  leftUnitor : BitProc
  rightUnitor : BitProc
  leftInverse : BitProc
  rightInverse : BitProc
  left_iso : sequence leftUnitor leftInverse = .identity ∧
    sequence leftInverse leftUnitor = .identity
  right_iso : sequence rightUnitor rightInverse = .identity ∧
    sequence rightInverse rightUnitor = .identity
  left_natural : ∀ f, sequence (tensor .identity f) leftUnitor =
    sequence leftUnitor f
  right_natural : ∀ f, sequence (tensor f .identity) rightUnitor =
    sequence rightUnitor f
  interchange : ∀ a b c d, tensor (sequence a b) (sequence c d) =
    sequence (tensor a c) (tensor b d)

theorem weak_unitors_forced {tensor : BitProc → BitProc → BitProc}
    (h : WeakTensorData tensor) :
    h.leftUnitor = .identity ∧ h.rightUnitor = .identity :=
  ⟨(invertible_iff_identity _).mp ⟨h.leftInverse,h.left_iso⟩,
   (invertible_iff_identity _).mp ⟨h.rightInverse,h.right_iso⟩⟩

theorem tensor_units_derived {tensor : BitProc → BitProc → BitProc}
    (h : WeakTensorData tensor) :
    (∀ f, tensor .identity f=f) ∧ (∀ f, tensor f .identity=f) := by
  have hu := weak_unitors_forced h
  constructor
  · intro f
    have hn := h.left_natural f
    rw [hu.1, sequence_right, sequence_left] at hn
    exact hn
  · intro f
    have hn := h.right_natural f
    rw [hu.2, sequence_right, sequence_left] at hn
    exact hn

theorem no_weak_tensor (tensor : BitProc → BitProc → BitProc) :
    ¬ Nonempty (WeakTensorData tensor) := by
  rintro ⟨h⟩
  have hu := tensor_units_derived h
  exact resets_noncommute (operations_commute sequence tensor .identity
    sequence_left sequence_right hu.1 hu.2 h.interchange .reset0 .reset1)

theorem no_any_tensor : ¬ ∃ tensor, Nonempty (WeakTensorData tensor) := by
  rintro ⟨tensor,h⟩
  exact no_weak_tensor tensor h

/-- Clean scalar control: the C2 monoid supports its XOR tensor. -/
theorem xor_interchange (a b c d : Bool) :
    Bool.xor (Bool.xor a b) (Bool.xor c d) =
      Bool.xor (Bool.xor a c) (Bool.xor b d) := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide

end OptionalV13
