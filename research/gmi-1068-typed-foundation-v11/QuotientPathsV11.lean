import TypedPathsV11
namespace TypedPathsV11
universe u v w x

/-- An equivalence in each typed Hom, stable under both concatenation arguments. -/
structure Congruence {V : Type u} (G : V → V → Type v) where
  rel : {a b : V} → Path G a b → Path G a b → Prop
  refl : {a b : V} → (p : Path G a b) → rel p p
  symm : {a b : V} → {p q : Path G a b} → rel p q → rel q p
  trans : {a b : V} → {p q r : Path G a b} → rel p q → rel q r → rel p r
  append : {a b c : V} → {p p' : Path G a b} → {q q' : Path G b c} →
    rel p p' → rel q q' → rel (Path.append p q) (Path.append p' q')

namespace Congruence
variable {V : Type u} {G : V → V → Type v} (R : Congruence G)

def setoid (a b : V) : Setoid (Path G a b) where
  r := R.rel
  iseqv := ⟨R.refl, R.symm, R.trans⟩

abbrev Hom (a b : V) := Quotient (R.setoid a b)
def classOf {a b : V} (p : Path G a b) : R.Hom a b := Quotient.mk _ p

def comp {a b c : V} (p : R.Hom a b) (q : R.Hom b c) : R.Hom a c :=
  Quotient.liftOn₂ p q (fun p q => R.classOf (Path.append p q))
    (fun _ _ _ _ hp hq => Quotient.sound (R.append hp hq))

theorem comp_mk {a b c : V} (p : Path G a b) (q : Path G b c) :
    R.comp (R.classOf p) (R.classOf q) = R.classOf (Path.append p q) := rfl

theorem comp_assoc {a b c d : V}
    (p : R.Hom a b) (q : R.Hom b c) (r : R.Hom c d) :
    R.comp (R.comp p q) r = R.comp p (R.comp q r) := by
  induction p using Quotient.inductionOn with
  | h p =>
    induction q using Quotient.inductionOn with
    | h q =>
      induction r using Quotient.inductionOn with
      | h r =>
        change R.classOf (Path.append (Path.append p q) r) =
          R.classOf (Path.append p (Path.append q r))
        rw [Path.append_assoc]

theorem left_id {a b : V} (p : R.Hom a b) :
    R.comp (R.classOf (.nil a)) p = p := by
  induction p using Quotient.inductionOn with
  | h p => rfl

theorem right_id {a b : V} (p : R.Hom a b) :
    R.comp p (R.classOf (.nil b)) = p := by
  induction p using Quotient.inductionOn with
  | h p =>
    change R.classOf (Path.append p (.nil b)) = R.classOf p
    rw [Path.append_nil]

def category : Category V where
  Hom := R.Hom
  id := fun a => R.classOf (.nil a)
  comp := R.comp
  assoc := R.comp_assoc
  left_id := R.left_id
  right_id := R.right_id
end Congruence

/-- The kernel of every lawful path interpretation is a typed congruence. -/
def kernel {V : Type u} {W : Type w} {G : V → V → Type v}
    (C : Category.{w,x} W) (obj : V → W)
    (edge : {a b : V} → G a b → C.Hom (obj a) (obj b)) : Congruence G where
  rel := fun p q => eval C obj edge p = eval C obj edge q
  refl := fun _ => rfl
  symm := Eq.symm
  trans := Eq.trans
  append := by
    intro a b c p p' q q' hp hq
    rw [eval_append, eval_append, hp, hq]

section Presentation
variable {V : Type u} (C : Category.{u,v} V)

abbrev ownKernel : Congruence C.Hom := kernel C (fun a => a) (fun f => f)
abbrev presented : Category V := (ownKernel C).category

theorem class_eq_iff_eval_eq {a b : V} (p q : Path C.Hom a b) :
    (ownKernel C).classOf p = (ownKernel C).classOf q ↔
      eval C (fun a => a) (fun f => f) p = eval C (fun a => a) (fun f => f) q :=
  ⟨Quotient.exact, fun h => Quotient.sound (s := (ownKernel C).setoid a b) h⟩

theorem eval_onto {a b : V} (f : C.Hom a b) :
    ∃ p : Path C.Hom a b, eval C (fun a => a) (fun f => f) p = f :=
  ⟨Path.single f, eval_single C (fun a => a) (fun f => f) f⟩

def lower {a b : V} (p : (presented C).Hom a b) : C.Hom a b :=
  Quotient.liftOn p (eval C (fun a => a) (fun f => f)) (fun _ _ h => h)

def quote {a b : V} (f : C.Hom a b) : (presented C).Hom a b :=
  (ownKernel C).classOf (Path.single f)

theorem lower_quote {a b : V} (f : C.Hom a b) :
    lower C (quote C f) = f := eval_single C (fun a => a) (fun f => f) f

theorem quote_lower {a b : V} (p : (presented C).Hom a b) :
    quote C (lower C p) = p := by
  induction p using Quotient.inductionOn with
  | h p =>
    apply Quotient.sound
    exact eval_single C (fun a => a) (fun f => f) _

theorem lower_id (a : V) : lower C ((presented C).id a) = C.id a := rfl

theorem lower_comp {a b c : V}
    (p : (presented C).Hom a b) (q : (presented C).Hom b c) :
    lower C ((presented C).comp p q) = C.comp (lower C p) (lower C q) := by
  induction p using Quotient.inductionOn with
  | h p =>
    induction q using Quotient.inductionOn with
    | h q => exact eval_append C (fun a => a) (fun f => f) p q

theorem quote_id (a : V) : quote C (C.id a) = (presented C).id a := by
  apply Quotient.sound
  exact eval_single C (fun a => a) (fun f => f) _

theorem quote_comp {a b c : V} (f : C.Hom a b) (g : C.Hom b c) :
    quote C (C.comp f g) = (presented C).comp (quote C f) (quote C g) := by
  apply Quotient.sound
  change eval C (fun a => a) (fun f => f) (Path.single (C.comp f g)) =
    eval C (fun a => a) (fun f => f) (Path.append (Path.single f) (Path.single g))
  rw [eval_append, eval_single, eval_single, eval_single]

theorem lower_injective {a b : V} {p q : (presented C).Hom a b}
    (h : lower C p = lower C q) : p = q := by
  rw [← quote_lower C p, ← quote_lower C q, h]

theorem lower_surjective {a b : V} (f : C.Hom a b) :
    ∃ p : (presented C).Hom a b, lower C p = f :=
  ⟨quote C f, lower_quote C f⟩
end Presentation

/-- Object-fixing isomorphism: both Hom maps are inverse and preserve all laws. -/
structure CategoryIso {V : Type u} (C : Category.{u,v} V) (D : Category.{u,w} V) where
  forward : {a b : V} → C.Hom a b → D.Hom a b
  backward : {a b : V} → D.Hom a b → C.Hom a b
  backward_forward : ∀ {a b} (f : C.Hom a b), backward (forward f) = f
  forward_backward : ∀ {a b} (f : D.Hom a b), forward (backward f) = f
  forward_id : ∀ a, forward (C.id a) = D.id a
  backward_id : ∀ a, backward (D.id a) = C.id a
  forward_comp : ∀ {a b c} (f : C.Hom a b) (g : C.Hom b c),
    forward (C.comp f g) = D.comp (forward f) (forward g)
  backward_comp : ∀ {a b c} (f : D.Hom a b) (g : D.Hom b c),
    backward (D.comp f g) = C.comp (backward f) (backward g)

def presentationIso {V : Type u} (C : Category.{u,v} V) :
    CategoryIso (presented C) C where
  forward := lower C
  backward := quote C
  backward_forward := quote_lower C
  forward_backward := lower_quote C
  forward_id := lower_id C
  backward_id := quote_id C
  forward_comp := lower_comp C
  backward_comp := quote_comp C

end TypedPathsV11
