import TypedPathsV11
namespace GroupLawsV16
inductive Label where
  | zero | one | two | three
  deriving DecidableEq, Repr

def number : Label → Nat
  | .zero => 0 | .one => 1 | .two => 2 | .three => 3

def rotate : Label → Label
  | .zero => .one | .one => .two | .two => .three | .three => .zero

def c4mul : Label → Label → Label
  | .zero, b => b
  | .one, b => rotate b
  | .two, b => rotate (rotate b)
  | .three, b => rotate (rotate (rotate b))

def v4mul : Label → Label → Label
  | .zero, b => b
  | .one, .zero => .one | .one, .one => .zero
  | .one, .two => .three | .one, .three => .two
  | .two, .zero => .two | .two, .one => .three
  | .two, .two => .zero | .two, .three => .one
  | .three, .zero => .three | .three, .one => .two
  | .three, .two => .one | .three, .three => .zero

theorem c4_is_modulo (a b : Label) :
    number (c4mul a b) = (number a + number b) % 4 := by
  cases a <;> cases b <;> rfl

theorem v4_is_xor (a b : Label) :
    number (v4mul a b) = Nat.xor (number a) (number b) := by
  cases a <;> cases b <;> rfl

structure Law where
  comp : Label → Label → Label
  assoc : ∀ a b c, comp (comp a b) c = comp a (comp b c)
  left_id : ∀ a, comp .zero a = a
  right_id : ∀ a, comp a .zero = a

def c4 : Law where
  comp := c4mul
  assoc a b c := by cases a <;> cases b <;> cases c <;> rfl
  left_id a := by cases a <;> rfl
  right_id a := by cases a <;> rfl

def v4 : Law where
  comp := v4mul
  assoc a b c := by cases a <;> cases b <;> cases c <;> rfl
  left_id a := by cases a <;> rfl
  right_id a := by cases a <;> rfl

def category (m : Law) : TypedPathsV11.Category Unit where
  Hom _ _ := Label
  id _ := .zero
  comp := m.comp
  assoc := m.assoc
  left_id := m.left_id
  right_id := m.right_id

def parity : Label → Bool
  | .zero | .two => false
  | .one | .three => true

theorem c4_parity_comp (a b : Label) :
    parity (c4.comp a b) = Bool.xor (parity a) (parity b) := by
  cases a <;> cases b <;> rfl

theorem v4_parity_comp (a b : Label) :
    parity (v4.comp a b) = Bool.xor (parity a) (parity b) := by
  cases a <;> cases b <;> rfl

theorem composition_different : c4.comp ≠ v4.comp := by
  intro h
  have bad := congrArg (fun f => f Label.one Label.one) h
  cases bad

theorem actual_products : c4.comp .one .one = .two ∧ v4.comp .one .one = .zero :=
  ⟨rfl, rfl⟩

theorem c4_assoc (a b c : Label) :
    c4.comp (c4.comp a b) c = c4.comp a (c4.comp b c) := c4.assoc a b c
theorem v4_assoc (a b c : Label) :
    v4.comp (v4.comp a b) c = v4.comp a (v4.comp b c) := v4.assoc a b c
theorem c4_units (a : Label) : c4.comp .zero a = a ∧ c4.comp a .zero = a :=
  ⟨c4.left_id a, c4.right_id a⟩
theorem v4_units (a : Label) : v4.comp .zero a = a ∧ v4.comp a .zero = a :=
  ⟨v4.left_id a, v4.right_id a⟩
theorem category_comp (m : Law) (a b : Label) :
    (category m).comp (a:=()) (b:=()) (c:=()) (a : (category m).Hom () ()) (b : (category m).Hom () ()) =
      m.comp a b := rfl
theorem category_id (m : Law) : (category m).id () = Label.zero := rfl
end GroupLawsV16
