import ProcessMapsV26
namespace LocallyDiscreteV26
open TypedPathsV11
universe u v
variable {O : Type u} (C : Category.{u,v} O)
abbrev Two {a b : O} (f g : C.Hom a b) := PLift (f = g)
def twoId {a b : O} (f : C.Hom a b) : Two C f f := ⟨rfl⟩
def vertical {a b : O} {f g h : C.Hom a b} (p : Two C f g) (q : Two C g h) :
    Two C f h := ⟨p.down.trans q.down⟩
theorem two_unique {a b : O} {f g : C.Hom a b} (p q : Two C f g) : p = q := by
  cases p; cases q; rfl
def homCategory (a b : O) : Category (C.Hom a b) where
  Hom := Two C
  id := twoId C
  comp := vertical C
  assoc _ _ _ := two_unique C _ _
  left_id _ := two_unique C _ _
  right_id _ := two_unique C _ _
def horizontal {a b c : O} {f f' : C.Hom a b} {g g' : C.Hom b c}
    (p : Two C f f') (q : Two C g g') : Two C (C.comp f g) (C.comp f' g') :=
  ⟨(congrArg (fun x => C.comp x g) p.down).trans (congrArg (C.comp f') q.down)⟩
theorem horizontal_id {a b c : O} (f : C.Hom a b) (g : C.Hom b c) :
    horizontal C (twoId C f) (twoId C g) = twoId C (C.comp f g) := two_unique C _ _
theorem interchange {a b c : O} {f f' f'' : C.Hom a b} {g g' g'' : C.Hom b c}
    (p : Two C f f') (p' : Two C f' f'') (q : Two C g g') (q' : Two C g' g'') :
    horizontal C (vertical C p p') (vertical C q q') =
    vertical C (horizontal C p q) (horizontal C p' q') := two_unique C _ _
def associator {a b c d : O} (f : C.Hom a b) (g : C.Hom b c) (h : C.Hom c d) :
    Two C (C.comp (C.comp f g) h) (C.comp f (C.comp g h)) := ⟨C.assoc f g h⟩
def associatorInv {a b c d : O} (f : C.Hom a b) (g : C.Hom b c) (h : C.Hom c d) :
    Two C (C.comp f (C.comp g h)) (C.comp (C.comp f g) h) := ⟨(C.assoc f g h).symm⟩
def leftUnitor {a b : O} (f : C.Hom a b) : Two C (C.comp (C.id a) f) f := ⟨C.left_id f⟩
def rightUnitor {a b : O} (f : C.Hom a b) : Two C (C.comp f (C.id b)) f := ⟨C.right_id f⟩
def leftUnitorInv {a b : O} (f : C.Hom a b) : Two C f (C.comp (C.id a) f) := ⟨(C.left_id f).symm⟩
def rightUnitorInv {a b : O} (f : C.Hom a b) : Two C f (C.comp f (C.id b)) := ⟨(C.right_id f).symm⟩
theorem associator_inverse {a b c d : O} (f : C.Hom a b) (g : C.Hom b c) (h : C.Hom c d) :
    vertical C (associator C f g h) (associatorInv C f g h) = twoId C _ ∧
    vertical C (associatorInv C f g h) (associator C f g h) = twoId C _ :=
  ⟨two_unique C _ _,two_unique C _ _⟩
theorem unitor_inverse {a b : O} (f : C.Hom a b) :
    vertical C (leftUnitor C f) (leftUnitorInv C f) = twoId C _ ∧
    vertical C (leftUnitorInv C f) (leftUnitor C f) = twoId C _ ∧
    vertical C (rightUnitor C f) (rightUnitorInv C f) = twoId C _ ∧
    vertical C (rightUnitorInv C f) (rightUnitor C f) = twoId C _ :=
  ⟨two_unique C _ _,two_unique C _ _,two_unique C _ _,two_unique C _ _⟩
theorem associator_natural {a b c d : O} {f f' : C.Hom a b} {g g' : C.Hom b c}
    {h h' : C.Hom c d} (p : Two C f f') (q : Two C g g') (r : Two C h h') :
    vertical C (horizontal C (horizontal C p q) r) (associator C f' g' h') =
    vertical C (associator C f g h) (horizontal C p (horizontal C q r)) := two_unique C _ _
theorem left_natural {a b : O} {f g : C.Hom a b} (p : Two C f g) :
    vertical C (horizontal C (twoId C (C.id a)) p) (leftUnitor C g) =
    vertical C (leftUnitor C f) p := two_unique C _ _
theorem right_natural {a b : O} {f g : C.Hom a b} (p : Two C f g) :
    vertical C (horizontal C p (twoId C (C.id b))) (rightUnitor C g) =
    vertical C (rightUnitor C f) p := two_unique C _ _
theorem pentagon {a b c d e : O} (f : C.Hom a b) (g : C.Hom b c)
    (h : C.Hom c d) (k : C.Hom d e) :
    vertical C (vertical C (horizontal C (associator C f g h) (twoId C k))
      (associator C f (C.comp g h) k)) (horizontal C (twoId C f) (associator C g h k)) =
    vertical C (associator C (C.comp f g) h k) (associator C f g (C.comp h k)) := two_unique C _ _
theorem triangle {a b c : O} (f : C.Hom a b) (g : C.Hom b c) :
    vertical C (associator C f (C.id b) g) (horizontal C (twoId C f) (leftUnitor C g)) =
    horizontal C (rightUnitor C f) (twoId C g) := two_unique C _ _
def underlying : Category O := C
theorem underlying_eq : underlying C = C := rfl
theorem observer_unchanged (t : BracketV25.Tree O (BundledCategoryV19.Arrow C)) :
    CategoryTreesV25.observer (underlying C) t = CategoryTreesV25.observer C t := rfl
end LocallyDiscreteV26
