inductive HiddenTask where | id | not
inductive Bit where | z | o deriving DecidableEq

def flip : Bit → Bit | .z => .o | .o => .z

def trainLabel : HiddenTask → Bit
  | .id => .z
  | .not => .o

def queryTruth : HiddenTask → Bit
  | .id => .o
  | .not => .z

def adaptive (train : Bit) : Bit := flip train

theorem adaptive_solves_both (t : HiddenTask) :
    adaptive (trainLabel t) = queryTruth t := by
  cases t <;> rfl

def fixedZ (_ : Bit) : Bit := .z
def fixedO (_ : Bit) : Bit := .o

theorem fixedZ_fails_one : fixedZ (trainLabel HiddenTask.id) ≠ queryTruth HiddenTask.id := by decide
theorem fixedO_fails_one : fixedO (trainLabel HiddenTask.not) ≠ queryTruth HiddenTask.not := by decide

def compose {A B C : Type} (f : A → B) (g : B → C) : A → C :=
  fun x => g (f x)

theorem reflective_finite_composition {P D : Type}
    (m1 m2 : P → P) :
    ∃ m : P → P, ∀ p, m p = m2 (m1 p) := by
  exact ⟨compose m1 m2, by intro p; rfl⟩
