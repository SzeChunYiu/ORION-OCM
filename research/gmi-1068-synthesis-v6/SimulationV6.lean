import Std

namespace SynthesisV6

inductive Term where
  | x
  | y
  | nand (left right : Term)
deriving DecidableEq, Repr

def size : Term → Nat
  | .x => 1
  | .y => 1
  | .nand a b => 1 + size a + size b

def eval {S : Type u} (x y : S) (op : S → S → S) : Term → S
  | .x => x
  | .y => y
  | .nand a b => op (eval x y op a) (eval x y op b)

inductive Instr where
  | loadX
  | loadY
  | apply
deriving DecidableEq, Repr

def step {S : Type u} (x y : S) (op : S → S → S) :
    Instr → List S → Option (List S)
  | .loadX, st => some (x :: st)
  | .loadY, st => some (y :: st)
  | .apply, right :: left :: st => some (op left right :: st)
  | .apply, _ => none

def run {S : Type u} (x y : S) (op : S → S → S) :
    List Instr → List S → Option (List S)
  | [], st => some st
  | i :: code, st => (step x y op i st).bind (run x y op code)

def compile : Term → List Instr
  | .x => [.loadX]
  | .y => [.loadY]
  | .nand a b => compile a ++ compile b ++ [.apply]

theorem run_append {S : Type u} (x y : S) (op : S → S → S)
    (a b : List Instr) (st : List S) :
    run x y op (a ++ b) st =
      (run x y op a st).bind (run x y op b) := by
  induction a generalizing st with
  | nil => rfl
  | cons i rest ih =>
    simp only [List.cons_append, run]
    cases h : step x y op i st with
    | none => rfl
    | some st' => exact ih st'

theorem compile_correct {S : Type u} (x y : S) (op : S → S → S)
    (t : Term) (st : List S) :
    run x y op (compile t) st = some (eval x y op t :: st) := by
  induction t generalizing st with
  | x => rfl
  | y => rfl
  | nand a b iha ihb =>
    simp [compile, run_append, iha, ihb, run, step, eval]

theorem compile_size (t : Term) : (compile t).length = size t := by
  induction t with
  | x => rfl
  | y => rfl
  | nand a b iha ihb =>
    simp [compile, size, iha, ihb]
    omega

/-- Every expression obeys a semantic lower bound if the two terminals and
    every semantic composition obey their local certificate inequalities. -/
theorem certificate_lower_bound {S : Type u}
    (x y : S) (op : S → S → S) (m : S → Nat)
    (hx : m x ≤ 1) (hy : m y ≤ 1)
    (hop : ∀ a b, m (op a b) ≤ 1 + m a + m b)
    (t : Term) : m (eval x y op t) ≤ size t := by
  induction t with
  | x => exact hx
  | y => exact hy
  | nand a b iha ihb =>
    have h := hop (eval x y op a) (eval x y op b)
    change m (op (eval x y op a) (eval x y op b)) ≤ 1 + size a + size b
    omega

/-- Attainment plus the inductive certificate proves minima over all finite
    trees in the unbounded grammar, not only over a searched depth bound. -/
theorem exact_minimality {S : Type u}
    (x y : S) (op : S → S → S) (m : S → Nat)
    (hx : m x ≤ 1) (hy : m y ≤ 1)
    (hop : ∀ a b, m (op a b) ≤ 1 + m a + m b)
    (attained : ∀ s, ∃ t, eval x y op t = s ∧ size t = m s) :
    ∀ s, ∃ t, eval x y op t = s ∧ size t = m s ∧
      ∀ u, eval x y op u = s → size t ≤ size u := by
  intro s
  obtain ⟨t, ht, hsize⟩ := attained s
  refine ⟨t, ht, hsize, ?_⟩
  intro u hu
  have h := certificate_lower_bound x y op m hx hy hop u
  rw [hu] at h
  rw [hsize]
  exact h

theorem apply_underflow_empty {S : Type u} (x y : S) (op : S → S → S) :
    step x y op .apply [] = none := rfl

theorem apply_underflow_single {S : Type u} (x y z : S) (op : S → S → S) :
    step x y op .apply [z] = none := rfl

end SynthesisV6
