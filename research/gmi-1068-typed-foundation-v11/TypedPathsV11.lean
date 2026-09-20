import Std
namespace TypedPathsV11
universe u v w x

/-- Lawful target; source path laws are constructed below, not fields here. -/
structure Category (V : Type u) where
  Hom : V → V → Type v
  id : (a : V) → Hom a a
  comp : {a b c : V} → Hom a b → Hom b c → Hom a c
  assoc : {a b c d : V} → (f : Hom a b) → (g : Hom b c) →
    (h : Hom c d) → comp (comp f g) h = comp f (comp g h)
  left_id : {a b : V} → (f : Hom a b) → comp (id a) f = f
  right_id : {a b : V} → (f : Hom a b) → comp f (id b) = f

inductive Path {V : Type u} (G : V → V → Type v) : V → V → Type (max u v)
  | nil (a : V) : Path G a a
  | cons {a b c : V} : G a b → Path G b c → Path G a c

namespace Path
variable {V : Type u} {G : V → V → Type v}

def append {a b c : V} (p : Path G a b) (q : Path G b c) : Path G a c :=
  match p with
  | .nil _ => q
  | .cons e tail => .cons e (append tail q)

def single {a b : V} (e : G a b) : Path G a b := .cons e (.nil b)

theorem nil_append {a b : V} (p : Path G a b) :
    append (.nil a) p = p := rfl

theorem append_nil {a b : V} (p : Path G a b) :
    append p (.nil b) = p := by
  induction p with
  | nil => rfl
  | cons e tail ih => simp only [append, ih]

theorem append_assoc {a b c d : V}
    (p : Path G a b) (q : Path G b c) (r : Path G c d) :
    append (append p q) r = append p (append q r) := by
  induction p with
  | nil => rfl
  | cons e tail ih => simp only [append, ih]

def category (G : V → V → Type v) : Category V where
  Hom := Path G
  id := Path.nil
  comp := append
  assoc := append_assoc
  left_id := nil_append
  right_id := append_nil
end Path

section Interpretation
variable {V : Type u} {W : Type w} {G : V → V → Type v}
variable (C : Category.{w,x} W) (obj : V → W)
variable (edge : {a b : V} → G a b → C.Hom (obj a) (obj b))

def eval {a b : V} (p : Path G a b) : C.Hom (obj a) (obj b) :=
  match p with
  | .nil a => C.id (obj a)
  | .cons e tail => C.comp (edge e) (eval tail)

theorem eval_nil (a : V) : eval C obj edge (.nil a) = C.id (obj a) := rfl

theorem eval_append {a b c : V} (p : Path G a b) (q : Path G b c) :
    eval C obj edge (Path.append p q) =
      C.comp (eval C obj edge p) (eval C obj edge q) := by
  induction p with
  | nil a => exact (C.left_id _).symm
  | cons e tail ih =>
    simp only [Path.append, eval, ih]
    exact (C.assoc _ _ _).symm

theorem eval_single {a b : V} (e : G a b) :
    eval C obj edge (Path.single e) = edge e := C.right_id _

/-- Any law-preserving extension of the same typed edges is this evaluator. -/
theorem eval_unique
    (f : {a b : V} → Path G a b → C.Hom (obj a) (obj b))
    (hnil : ∀ a, f (.nil a) = C.id (obj a))
    (happend : ∀ {a b c} (p : Path G a b) (q : Path G b c),
      f (Path.append p q) = C.comp (f p) (f q))
    (hedge : ∀ {a b} (e : G a b), f (Path.single e) = edge e)
    {a b : V} (p : Path G a b) : f p = eval C obj edge p := by
  induction p with
  | nil a => exact hnil a
  | cons e tail ih =>
    calc
      f (.cons e tail) = f (Path.append (Path.single e) tail) := rfl
      _ = C.comp (f (Path.single e)) (f tail) := happend _ _
      _ = C.comp (edge e) (eval C obj edge tail) := by rw [hedge, ih]
      _ = eval C obj edge (.cons e tail) := rfl
end Interpretation

/-- Fixed-object-map functors, sufficient for the universal interpreter. -/
structure Interpreter {V : Type u} {W : Type w} (G : V → V → Type v)
    (C : Category.{w,x} W) (obj : V → W) where
  map : {a b : V} → Path G a b → C.Hom (obj a) (obj b)
  map_nil : ∀ a, map (.nil a) = C.id (obj a)
  map_append : ∀ {a b c} (p : Path G a b) (q : Path G b c),
    map (Path.append p q) = C.comp (map p) (map q)

def interpreter {V : Type u} {W : Type w} {G : V → V → Type v}
    (C : Category.{w,x} W) (obj : V → W)
    (edge : {a b : V} → G a b → C.Hom (obj a) (obj b)) :
    Interpreter G C obj where
  map := eval C obj edge
  map_nil := eval_nil C obj edge
  map_append := eval_append C obj edge

theorem interpreter_unique {V : Type u} {W : Type w} {G : V → V → Type v}
    (C : Category.{w,x} W) (obj : V → W)
    (edge : {a b : V} → G a b → C.Hom (obj a) (obj b))
    (F : Interpreter G C obj)
    (h : ∀ {a b} (e : G a b), F.map (Path.single e) = edge e)
    {a b : V} (p : Path G a b) :
    F.map p = (interpreter C obj edge).map p :=
  eval_unique C obj edge F.map F.map_nil F.map_append h p

end TypedPathsV11
